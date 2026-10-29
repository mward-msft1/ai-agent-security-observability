# Security and data handling

This is a reference implementation, not a managed collector or a universal DLP
engine. Report issues privately to the repository owner; do not paste live
tokens, customer prompts or tenant exports into public issues.

Content recording is **off by default**. Collectors persist a metadata allowlist;
`--include-content` plus `CONTENT_CAPTURE_APPROVED=true` stores the *complete raw
record*, including body, cards, attachments, resource references and identifiers
when the source returns them. It is not a selective prompt-only export.
Metadata can still be personal/sensitive data. Hashes of low-entropy values are
not anonymization. Do not assume the allowlist is a compliance certification.

Use separate databases and destinations for content vs metadata. This code does
not provide encryption-at-rest, RBAC, TTL deletion, key management, a distributed
lease, or SIEM receipt confirmation. Put `.local` on an access-restricted,
encrypted volume; restrict database/export backups and host access, set an
approved deletion schedule, and test deletion including backups. SQLite is for
a single worker per database; do not share it between concurrent collectors.
Never upload real content as CI artifacts.

The transport refuses redirects and non-allowlisted HTTPS hosts before sending
tokens. Use trusted configuration, not URLs supplied by a model or transcript.
The sink hostname is an explicit operator approval boundary, not an SSRF sandbox
for an untrusted caller. Require outbound firewall restrictions, TLS trust and
private networking where applicable. Commercial-cloud endpoints are the default;
do not simply change a hostname to claim sovereign-cloud support.

Use workload federation/managed credentials, not client secrets in code. The
examples never apply tenant policies, invoke an actual agent tool, or provision
cloud infrastructure automatically. SDK console demos can display synthetic
content only with explicit flags; use a clean environment with no ambient OTLP
exporter configuration unless you intend that egress. Sensitive logging through
other SDKs or model middleware must be reviewed independently.
