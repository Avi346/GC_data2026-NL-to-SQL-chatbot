import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterable, Tuple, Callable

from env_loader import load_project_env

load_project_env()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import (
        Distance,
        VectorParams,
        Filter,
        FieldCondition,
        MatchValue,
    )
except ImportError:  # pragma: no cover - optional dependency
    QdrantClient = None  # type: ignore[assignment]
    Distance = VectorParams = Filter = FieldCondition = MatchValue = None  # type: ignore[assignment]

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore[assignment]

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None  # type: ignore[assignment]


# Qdrant connection
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "chatbot_user_side_kpi_framework_chunks")

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
    if QdrantClient is None:
        raise RuntimeError(
            "Missing dependency: qdrant-client. Install with 'pip install qdrant-client'."
        )
    if not QDRANT_URL:
        raise ValueError("QDRANT_URL is not set in environment variables.")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def get_embedder() -> SentenceTransformer:
    if SentenceTransformer is None:
        raise RuntimeError(
            "Missing dependency: sentence-transformers. Install with 'pip install sentence-transformers'."
        )
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    """
    (Re)create the collection to store RAG chunks for the KPI framework PDF.
    Running multiple times is safe – it will drop and recreate the collection.
    """
    if VectorParams is None or Distance is None:
        raise RuntimeError(
            "qdrant-client models are unavailable. Install with 'pip install qdrant-client'."
        )

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def _extract_pdf_text(pdf_path: str) -> List[str]:
    """
    Extract raw text per page from the PDF.
    """
    if PdfReader is None:
        raise RuntimeError("Missing dependency: pypdf. Install with 'pip install pypdf'.")

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
    if doc_id is not None and Filter is not None and FieldCondition is not None and MatchValue is not None:
        qdrant_filter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        )

    def _query_points(query_filter):
        if hasattr(client, "search"):
            return client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )

        query_response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        return getattr(query_response, "points", []) or []

    try:
        results = _query_points(qdrant_filter)
    except Exception as exc:
        # Some hosted Qdrant plans require explicit payload index for filtered
        # search. If missing, retry without filter.
        err_text = str(exc).lower()
        if "index required" in err_text or "doc_id" in err_text:
            results = _query_points(None)
        else:
            raise

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


def ensure_pdf_indexed(
    client: QdrantClient,
    embedder: SentenceTransformer,
    pdf_path: str = DEFAULT_PDF_PATH,
    min_points: int = 1,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """
    Ensure the KPI PDF is indexed in Qdrant. If collection is missing or empty,
    it builds the index from PDF.
    """

    def _emit(message: str) -> None:
        if progress_callback:
            try:
                progress_callback(message)
            except Exception:
                pass

    try:
        count_result = client.count(collection_name=COLLECTION_NAME, exact=True)
        count = int(getattr(count_result, "count", 0))
        if count >= min_points:
            return {"indexed": True, "count": count, "rebuilt": False}
    except Exception:
        # Collection may not exist yet or count may fail on first run.
        pass

    _emit("KPI vector DB not ready. Building index from PDF...")
    points, _ = index_pdf_chunks(client, embedder, pdf_path=pdf_path)
    _emit(f"KPI vector DB indexed with {points} chunks.")
    return {"indexed": points >= min_points, "count": points, "rebuilt": True}


def retrieve_kpi_context(
    query: str,
    top_k: int = 5,
    min_score: float = 0.33,
    pdf_path: str = DEFAULT_PDF_PATH,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """
    Retrieve KPI knowledge context from the PDF-backed Qdrant vector DB.
    Returns matched chunks and prompt-ready context.
    """

    try:
        client = connect_qdrant()
        embedder = get_embedder()
    except Exception as exc:
        return {"success": False, "error": str(exc), "hits": []}

    try:
        ensure_pdf_indexed(
            client,
            embedder,
            pdf_path=pdf_path,
            progress_callback=progress_callback,
        )
        raw_hits = search_pdf_chunks(client, embedder, query=query, top_k=top_k)
    except Exception as exc:
        return {"success": False, "error": str(exc), "hits": []}

    hits = [hit for hit in raw_hits if float(hit.get("score") or 0.0) >= min_score]
    if not hits:
        return {
            "success": True,
            "hits": [],
            "source_label": "vector_db:qdrant",
            "context_for_prompt": "",
            "source_refs": [],
        }

    context_lines: List[str] = []
    source_refs: List[str] = []
    for hit in hits:
        page = hit.get("page")
        score = float(hit.get("score") or 0.0)
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        clipped_text = text[:900]
        context_lines.append(f"[Page {page} | score={score:.3f}] {clipped_text}")
        source_refs.append(f"User_KPI_Framework_Premium.pdf (page {page}, score={score:.3f})")

    return {
        "success": True,
        "hits": hits,
        "source_label": "vector_db:qdrant",
        "context_for_prompt": "\n".join(context_lines),
        "source_refs": source_refs,
    }


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
