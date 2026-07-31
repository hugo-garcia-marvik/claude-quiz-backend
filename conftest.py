"""Root conftest – ensures test dependencies are available."""
import subprocess
import sys


def pytest_configure(config):
    """Install httpx if missing (needed by FastAPI TestClient)."""
    try:
        import httpx  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "httpx>=0.27.0"],
        )
