import re
from collections.abc import Generator, Iterable
from contextlib import contextmanager, suppress
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from python_on_whales import docker, utils as docker_utils

from ..config import PROXY_DIR, PROXY_IMAGE, PROXY_PORT


class Lockdown:
    """The network a sandboxed container joins, and what the proxy refused it."""

    def __init__(self, network: str, envs: dict[str, str]):
        self.network = network
        self.envs = envs
        self.log = ""


@contextmanager
def lockdown(
    allow: Iterable[str],
    *,
    debug: bool,
    log_path: str | Path,
) -> Generator[Lockdown]:
    """Yield the network and proxy env a locked-down container runs under.

    The container joins an `--internal` network: no gateway, no route out, no
    external DNS. Its only way out is a CONNECT to the sidecar, which sits on a
    second network and refuses anything outside `allow`.
    """
    docker.build(PROXY_DIR, tags=PROXY_IMAGE, progress="tty" if debug else False)

    run_id = uuid4().hex[:12]
    proxy_name = f"agent-harness-sandbox-proxy-{run_id}"
    url = f"http://{proxy_name}:{PROXY_PORT}"
    jail = Lockdown(
        network=f"agent-harness-sandbox-jail-{run_id}",
        envs={
            "HTTP_PROXY": url,
            "HTTPS_PROXY": url,
            "http_proxy": url,
            "https_proxy": url,
            "NO_PROXY": "localhost,127.0.0.1",
        },
    )
    egress = f"agent-harness-sandbox-egress-{run_id}"

    proxy = None
    networks = []
    try:
        # python-on-whales' network.create wraps no --internal, and --internal is the point.
        # Reached through the module, not bound by name, so a test can patch it
        # where it lives instead of reaching into this one.
        docker_utils.run(
            [*docker.network.docker_cmd, "network", "create", "--internal", jail.network]
        )
        networks.append(jail.network)
        docker.network.create(egress)
        networks.append(egress)

        with TemporaryDirectory() as staging:
            allowlist = Path(staging) / "filter"
            allowlist.write_text("".join(f"^{re.escape(host)}$\n" for host in allow))
            allowlist.chmod(0o644)
            proxy = docker.run(
                PROXY_IMAGE,
                detach=True,
                name=proxy_name,
                networks=[egress],
                volumes=[(str(allowlist), "/etc/tinyproxy/filter", "ro")],
                cap_drop=["ALL"],
                security_options=["no-new-privileges"],
            )
            docker.network.connect(jail.network, proxy)
            yield jail
    finally:
        captured = False
        gone = False
        if proxy is not None:
            with suppress(Exception):
                jail.log = docker.logs(proxy)
                captured = True
            with suppress(Exception):
                docker.container.remove(proxy, force=True)
                gone = True
        for network in networks:
            if proxy is not None and not gone:
                with suppress(Exception):
                    docker.network.disconnect(network, proxy, force=True)
            with suppress(Exception):
                docker.network.remove(network)
        # An unread log is not an empty one: writing "" would erase the refusals.
        if captured:
            with suppress(Exception):
                Path(log_path).write_text(jail.log)
