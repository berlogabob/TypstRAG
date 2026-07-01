from git import Repo
from rich import print

from .config import RAW_DIR, TYPST_REPO_DIR, TYPST_REPO_URL, TYPST_VERSION


def fetch_typst(version: str = TYPST_VERSION) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if TYPST_REPO_DIR.exists():
        repo = Repo(TYPST_REPO_DIR)
        repo.remotes.origin.fetch(tags=True)
    else:
        repo = Repo.clone_from(TYPST_REPO_URL, TYPST_REPO_DIR)
        repo.remotes.origin.fetch(tags=True)
    repo.git.checkout(version)
    print(f"Typst ready: {TYPST_REPO_DIR} @ {version}")
