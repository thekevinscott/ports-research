from .config import (
    BASE_DOCKERFILE,
    BASE_IMAGE,
    PROXY_DIR,
    PROXY_IMAGE,
    PROXY_PORT,
    SANDBOX_DIR,
)


def describe_config():
    def it_points_at_the_packages_own_sandbox_directory():
        assert SANDBOX_DIR.name == "sandbox"

    def it_reads_the_base_image_from_the_sandbox_root():
        assert BASE_DOCKERFILE == SANDBOX_DIR / "Dockerfile"

    def it_keeps_the_proxy_in_its_own_subdirectory():
        assert PROXY_DIR == SANDBOX_DIR / "proxy"

    def it_tags_the_two_images_apart():
        assert BASE_IMAGE == "agent-harness-sandbox-base:latest"
        assert PROXY_IMAGE == "agent-harness-sandbox-proxy:latest"
        assert BASE_IMAGE != PROXY_IMAGE

    def it_fixes_the_proxy_port():
        assert PROXY_PORT == 8888
