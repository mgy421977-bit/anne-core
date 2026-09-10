# ANNE Core — Threat Model

## Assets

- API credentials
- GitHub credentials
- cognitive memory contents
- local files and repositories
- telemetry metadata

## Attack surface

- provider responses
- GitHub installer inputs
- environment variables
- telemetry endpoint
- persisted CognitiveStructure data

## Primary threats

1. Credential leakage into logs or memory.
2. Prompt/provider content influencing external actions.
3. Unauthorized GitHub writes.
4. Telemetry collecting sensitive cognitive content.
5. Memory poisoning causing inappropriate reuse.

## Mitigations

- credentials are environment-only
- telemetry is minimal and opt-out
- telemetry failures are fail-open
- GitHub installation is dry-run by default
- external writes require Agency Gate approval
- no force push
- semantic reuse is a candidate, not authority; confidence remains a separate gate
- provenance and contradictions are retained in CognitiveStructure

## Residual risks

The MVP does not provide complete sandboxing or cryptographic provenance. Memory poisoning and malicious provider output remain research concerns and require stronger validation before production deployment.
