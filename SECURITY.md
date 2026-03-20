# Security Policy

OSS Maintainer Copilot aims to reduce maintainer load without hiding risk. If you find a security issue, please report it privately and give maintainers time to investigate before public disclosure.

## Supported Versions

| Version | Supported |
| --- | --- |
| `main` | Yes |
| Latest tagged release | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please do not open a public GitHub issue for security reports.

Preferred reporting path:

1. Use GitHub's private vulnerability reporting flow in the repository Security tab if it is enabled.
2. If private reporting is unavailable, contact the maintainers through a private channel before sharing details publicly.

Please include:

- a short description of the issue
- affected versions or commits if known
- reproduction steps or a proof of concept
- impact assessment
- any suggested mitigation

## Response Expectations

- Initial acknowledgment target: within 3 business days
- Triage or status update target: within 7 business days after acknowledgment
- Coordinated disclosure preferred until a fix or mitigation is available

## Security Scope

This repository currently focuses on maintainer workflow automation. Reports are especially helpful when they involve:

- GitHub Action permission scope
- unsafe automation behavior
- data exposure in maintainer comments or release flows
- dependency or supply-chain risks
