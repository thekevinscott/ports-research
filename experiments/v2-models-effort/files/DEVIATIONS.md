# Deviations

- 2026-10-26: botbox 0.0.20 to 0.1.1 (PR #236). The Claude agent Dockerfile adds `socat` and copies in `botbox-relay`. port_codebase pastes that Dockerfile into the prompt, so runs from here on see two extra Dockerfile lines and run in a different image. The proxy is now reached through the relay on loopback. Kevin accepted the change rather than pinning 0.0.20.
