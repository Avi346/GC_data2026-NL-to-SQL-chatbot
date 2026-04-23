from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ENV_PATH = PROJECT_ROOT / ".env"


def load_project_env() -> None:
    """Load the shared parent-project .env file for the user-side app."""
    load_dotenv(dotenv_path=PROJECT_ENV_PATH)
