# Security Policy

## Supported Versions

Security fixes are provided for the current maintained release line and the active development branch. Older versions may not receive security updates unless the maintainers decide that the issue is critical and a backport is practical.

| Version | Supported |
| ------- | --------- |
| `main` / development branch | :white_check_mark: |
| `>= 0.4.14` | :white_check_mark: |
| `< 0.4.14` | :x: |

## Reporting a Vulnerability

Please report security vulnerabilities through the Pardus request portal:

<https://talep.pardus.org.tr/>

Do not open a public issue, pull request, discussion, or forum post for a vulnerability before the maintainers have had a reasonable opportunity to triage and remediate it.

When possible, include the following information in your report:

- affected package, component, file, or feature;
- affected version and operating system release;
- vulnerability type and expected impact;
- clear reproduction steps;
- proof-of-concept details using the least destructive method available;
- relevant logs, screenshots, package versions, or command output;
- whether the issue requires local access, authentication, administrator approval, user interaction, network positioning, or a specific desktop/session configuration;
- any suggested mitigation or patch guidance;
- your preferred contact method for follow-up.

Reports involving privilege boundaries, authentication bypasses, local privilege escalation, arbitrary command execution, unsafe `polkit`/`pkexec` helpers, unauthorized desktop/session access, sensitive information disclosure, or integrity-check bypasses are considered in scope.

## Triage Process

After receiving a report, the maintainers will attempt to:

1. acknowledge the report;
2. reproduce and validate the issue;
3. assess severity, affected versions, and exploit conditions;
4. prepare a fix, mitigation, or documented rationale if the report is declined;
5. coordinate advisory publication when appropriate.

A report may be declined if it is not reproducible, does not cross a security boundary, affects only unsupported versions, requires unrealistic attacker capabilities, duplicates a known issue, or describes expected behavior without a security impact.

## Coordinated Disclosure

Please keep vulnerability details private until a fix, mitigation, or advisory is available. If disclosure timelines are needed, include your requested timeline in the initial report so the maintainers can coordinate expectations.

The maintainers may request additional technical details, a reduced proof of concept, environment information, or validation against a patched build.

## Safe Harbor Expectations

Good-faith security research is welcome when it avoids unnecessary harm. Do not use testing techniques that intentionally destroy data, degrade service availability, persist unauthorized access, access unrelated user data, or exfiltrate secrets beyond what is strictly necessary to prove impact.

## Public Credit

Researchers may request public credit in the advisory or release notes. Include the preferred name or handle in the vulnerability report.
