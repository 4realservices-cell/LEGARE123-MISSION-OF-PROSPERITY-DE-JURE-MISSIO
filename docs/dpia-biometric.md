# Biometric Data Protection Impact Assessment (DPIA) Outline

## Purpose
The Sentinel ecosystem handles sensitive biometric signals and protected templates. These assets must be treated as special-category personal data.

## Controls
- Store only protected templates and hashes, not raw biometric data.
- Keep biometric material on-device or in encrypted edge storage when possible.
- Use revocable template generation so a compromised biometric can be rotated with a new protected template.
- Enforce proof before claim by verifying the holder DID, signature, and revocation status before accepting any claim.
- Maintain audit records that reference the proof and template hash without exposing raw biometric content.

## Retention
- Short retention periods for raw samples and temporary buffers.
- Delete or destroy biometric material when no longer needed, and mark the prior protected template as revoked.

## User Rights
- Consent capture and explicit notification required before enrollment.
- User should be able to request template revocation and re-enrollment.
- Logs and proofs must remain auditable while respecting data minimization.
