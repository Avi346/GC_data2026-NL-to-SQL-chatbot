import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(script_path: Path) -> None:
    script_abs = (ROOT / script_path).resolve()
    if not script_abs.exists():
        raise FileNotFoundError(f"Initializer not found: {script_abs}")

    print(f"\n=== Running: {script_abs} ===")
    result = subprocess.run(
        [sys.executable, str(script_abs.name)],
        cwd=str(script_abs.parent),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Step failed ({result.returncode}): {script_abs}")


def main() -> None:
    steps = [
        Path("admin_backend/services/create_duckdb_schema.py"),
        Path("admin_backend/core/chroma_db.py"),
        Path("admin_backend/core/kpi_injection.py"),
        Path("ChatBot_user_side/services/create_duckdb_schema.py"),
        Path("ChatBot_user_side/core/chroma_db.py"),
        Path("ChatBot_user_side/core/kpi_injection.py"),
    ]

    print("Starting all data initializers...")
    for step in steps:
        run_step(step)
    print("\nAll initializers completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)
