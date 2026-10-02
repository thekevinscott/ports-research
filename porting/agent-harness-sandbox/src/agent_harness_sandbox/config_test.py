from .config import (
    DOCKERFILE,
    PROXY_DIR,
    PROXY_IMAGE,
    PROXY_PORT,
    SANDBOX_DIR,
)


def describe_config():
    def it_points_at_the_packages_own_sandbox_directory():
        assert SANDBOX_DIR.name == "sandbox"

    def it_reads_the_agent_images_from_the_sandbox_root():
        assert DOCKERFILE == SANDBOX_DIR / "Dockerfile"

    def it_keeps_the_proxy_in_its_own_subdirectory():
        assert PROXY_DIR == SANDBOX_DIR / "proxy"

    def it_tags_the_proxy_image():
        assert PROXY_IMAGE == "agent-harness-sandbox-proxy:latest"

    def it_fixes_the_proxy_port():
        assert PROXY_PORT == 8888
