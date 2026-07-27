# Security Policy

## Reporting a vulnerability

If you discover a security issue, please do **not** open a public issue with exploit details.

Instead:

1. Open a private security advisory in GitHub Security for this repository, or
2. Contact the maintainer directly through the repository owner profile.

Please include:

- affected files/components
- reproduction steps
- impact assessment
- suggested mitigation (if available)

## Supported scope

Current focus areas:

- repository automation and scripts
- schema validation tooling
- documentation and generated artifacts integrity

## Security hygiene expectations

- no secrets in source control
- no unsafe script defaults for destructive operations
- dependency/tooling updates should be reviewed
- CI gates should remain enabled on `main`
