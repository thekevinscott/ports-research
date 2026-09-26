from pathlib import Path

SANDBOX_DIR = Path(__file__).resolve().parents[2] / "sandbox"
BASE_IMAGE = "agent-harness-sandbox-base:latest"
BASE_DOCKERFILE = SANDBOX_DIR / "Dockerfile"
PROXY_IMAGE = "agent-harness-sandbox-proxy:latest"
PROXY_DIR = SANDBOX_DIR / "proxy"
PROXY_PORT = 8888
