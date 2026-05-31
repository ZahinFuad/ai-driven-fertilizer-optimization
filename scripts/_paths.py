from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_DATA = DATA / "raw"
PROCESSED_DATA = DATA / "processed"
RESULTS = ROOT / "results"
RESULT_FIGURES = RESULTS / "figures"
ARTIFACTS = ROOT / "artifacts"
ARTIFACT_TABLES = ARTIFACTS / "tables"
ARTIFACT_FIGURES = ARTIFACTS / "figures"
ARTIFACT_MODELS = ARTIFACTS / "models"


def ensure_artifact_dirs() -> None:
    for path in (ARTIFACTS, ARTIFACT_TABLES, ARTIFACT_FIGURES, ARTIFACT_MODELS):
        path.mkdir(parents=True, exist_ok=True)


def require_file(path: Path, message: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"{message}\nExpected path: {path}")
    return path

