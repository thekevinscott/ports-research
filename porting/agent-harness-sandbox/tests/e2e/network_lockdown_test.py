"""What the porting agent may and may not reach from inside a real run.

gbnf is public on GitHub, npm and PyPI, so any of those three hands the agent the
hand-written implementation it is meant to be reproducing. These are the control
that makes the experiment's results mean anything.

Two probes per host, because either alone reads green for the wrong reason. The
direct one proves the container has no route of its own; the CONNECT one proves
the proxy's allowlist is narrow. A proxy that allowed everything would still pass
every direct probe. Nothing is written past the handshake, so no host sees a
request.
"""

import pytest

BLOCKED = ("github.com", "registry.npmjs.org", "pypi.org", "example.com")

ALLOWED = "api.anthropic.com"

IP_LITERAL = "140.82.121.4"

DIRECT = (
    "node -e 'const s = require(\"net\").connect"
    "({ host: process.argv[1], port: 443, timeout: 5000 });"
    " const r = (v) => { console.log(v); process.exit(0) };"
    ' s.on("connect", () => r("reachable"));'
    ' s.on("timeout", () => r("unreachable"));'
    ' s.on("error", () => r("unreachable"))\''
)

CONNECT = (
    "node -e 'const [host, proxy] = process.argv.slice(1);"
    ' const [name, port] = proxy.split(":");'
    ' const s = require("net").connect({ host: name, port: Number(port), timeout: 5000 });'
    " const r = (v) => { console.log(v); process.exit(0) };"
    ' s.on("connect", () => s.write('
    '"CONNECT " + host + ":443 HTTP/1.1\\r\\nHost: " + host + ":443\\r\\n\\r\\n"));'
    ' s.on("data", (d) => r(d.toString().split(" ")[1]));'
    ' s.on("timeout", () => r("timeout"));'
    ' s.on("error", (e) => r("error " + e.code))\''
)

RESOLVE = (
    "node -e 'require(\"dns\").lookup"
    '(process.argv[1], (e) => console.log(e ? "unresolvable" : "resolved"))\''
)

PROXY = '"${HTTPS_PROXY#http://}"'

PROBES = {
    **{f"direct {host}": f"{DIRECT} {host}" for host in (*BLOCKED, ALLOWED)},
    **{
        f"connect {host}": f"{CONNECT} {host} {PROXY}"
        for host in (*BLOCKED, ALLOWED, IP_LITERAL)
    },
    "resolve github.com": f"{RESOLVE} github.com",
}


@pytest.fixture(scope="module")
def session(sandbox):
    return sandbox(PROBES)


def describe_a_direct_connection():
    @pytest.mark.parametrize("host", [*BLOCKED, ALLOWED])
    def it_reaches_nothing_at_all(session, host):
        assert session.report[f"direct {host}"] == "unreachable"

    def it_cannot_resolve_an_external_hostname(session):
        assert session.report["resolve github.com"] == "unresolvable"


def describe_a_connection_through_the_proxy():
    def it_can_reach_the_anthropic_api(session):
        assert session.report[f"connect {ALLOWED}"] == "200"

    @pytest.mark.parametrize("host", BLOCKED)
    def it_is_refused_everywhere_else(session, host):
        assert session.report[f"connect {host}"] == "403"

    def it_is_refused_an_ip_literal(session):
        """The allowlist is an anchored ERE, so no address spells its way past it."""
        assert session.report[f"connect {IP_LITERAL}"] == "403"


def describe_the_denial_log():
    @pytest.mark.parametrize("host", BLOCKED)
    def it_names_the_host_a_refused_connect_was_aimed_at(session, host):
        assert any(host in line for line in session.denials)

    def it_survives_the_run_on_the_host(session):
        assert 'Proxying refused on filtered domain "pypi.org"' in session.proxy_log.read_text()
