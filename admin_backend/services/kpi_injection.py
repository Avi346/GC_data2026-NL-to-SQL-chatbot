import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterable, Tuple

from dotenv import load_dotenv

load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        "Missing dependency: sentence-transformers. Install with 'pip install sentence-transformers'."
    ) from exc

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        "Missing dependency: pypdf. Install with 'pip install pypdf'."
    ) from exc


# Qdrant connection
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "user_kpi_framework_premium_chunks")

# Embedding model
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Default PDF path (repository root)
DEFAULT_PDF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "User_KPI_Framework_Premium.pdf"
)


@dataclass
class Chunk:
    text: str
    page: int
    chunk_index: int


def connect_qdrant() -> QdrantClient:
    if not QDRANT_URL:
        raise ValueError("QDRANT_URL is not set in environment variables.")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    """
    Recreate the collection to store RAG chunks for the KPI framework PDF.
    Running multiple times is safe; it will drop and recreate the collection.
    """
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="doc_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )


def _extract_pdf_text(pdf_path: str) -> List[str]:
    """
    Extract raw text per page from the PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages_text: List[str] = []
    for page in reader.pages:
        # Some pages may return None, normalise to empty string
        text = page.extract_text() or ""
        pages_text.append(text)
    return pages_text


def _chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = 512,
    overlap: int = 64,
) -> Iterable[Chunk]:
    """
    Simple whitespace-based chunking with overlap.
    """
    words = text.split()
    if not words:
        return []

    chunks: List[Chunk] = []
    start = 0
    idx = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words).strip()
        if chunk_text:
            chunks.append(Chunk(text=chunk_text, page=page_number, chunk_index=idx))
        idx += 1
        if end == len(words):
            break
        start = end - overlap
    return chunks


def build_pdf_chunks(
    pdf_path: str = DEFAULT_PDF_PATH,
    chunk_size: int = 512,
    overlap: int = 64,
) -> List[Chunk]:
    """
    Load the KPI framework PDF and convert it into semantic chunks.
    """
    pages_text = _extract_pdf_text(pdf_path)
    all_chunks: List[Chunk] = []
    for page_idx, page_text in enumerate(pages_text):
        page_number = page_idx + 1
        page_chunks = list(_chunk_text(page_text, page_number, chunk_size, overlap))
        all_chunks.extend(page_chunks)
    return all_chunks


def _chunk_payload(chunk: Chunk, doc_id: str = "User_KPI_Framework_Premium") -> Dict[str, Any]:
    return {
        "doc_id": doc_id,
        "text": chunk.text,
        "page": chunk.page,
        "chunk_index": chunk.chunk_index,
    }


def index_pdf_chunks(
    client: QdrantClient,
    embedder: SentenceTransformer,
    pdf_path: str = DEFAULT_PDF_PATH,
    chunk_size: int = 512,
    overlap: int = 64,
) -> Tuple[int, str]:
    """
    End-to-end pipeline:
    - read KPI framework PDF
    - chunk it
    - embed each chunk
    - store in Qdrant as a RAG knowledge base

    Returns (num_chunks, collection_name).
    """
    chunks = build_pdf_chunks(pdf_path=pdf_path, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        raise ValueError("No chunks were generated from the PDF; check the file contents.")

    texts = [c.text for c in chunks]
    vectors = embedder.encode(texts, normalize_embeddings=True)

    vector_size = int(vectors.shape[1])
    ensure_collection(client, vector_size=vector_size)

    points: List[Dict[str, Any]] = []
    for idx, (vec, chunk) in enumerate(zip(vectors, chunks), start=1):
        payload = _chunk_payload(chunk)
        points.append(
            {
                "id": idx,
                "vector": vec.tolist(),
                "payload": payload,
            }
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points), COLLECTION_NAME


def search_pdf_chunks(
    client: QdrantClient,
    embedder: SentenceTransformer,
    query: str,
    top_k: int = 5,
    doc_id: Optional[str] = "User_KPI_Framework_Premium",
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant KPI framework chunks for a natural language query.
    This will be useful for later RAG-style answering.
    """
    query_vector = embedder.encode([query], normalize_embeddings=True)[0].tolist()

    qdrant_filter = None
    if doc_id is not None:
        qdrant_filter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        )

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )
    results = response.points

    # Each result has payload["text"], payload["page"], payload["chunk_index"], etc.
    return [
        {
            "score": r.score,
            "text": r.payload.get("text"),
            "page": r.payload.get("page"),
            "chunk_index": r.payload.get("chunk_index"),
            "doc_id": r.payload.get("doc_id"),
        }
        for r in results
    ]


def main() -> None:
    """
    CLI entry point to index the KPI framework PDF as a RAG knowledge base.
    """
    client = connect_qdrant()
    embedder = get_embedder()

    print(f"Indexing '{DEFAULT_PDF_PATH}' into Qdrant collection '{COLLECTION_NAME}'...")
    num_chunks, collection = index_pdf_chunks(client, embedder, pdf_path=DEFAULT_PDF_PATH)
    print(f"Done. Stored {num_chunks} chunks in collection '{collection}'.")


if __name__ == "__main__":
    main()
