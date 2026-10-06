# Blockchain + Biometrics Integration

This repository now includes the first pass of the blockchain/biometric architecture described for the Sentinel ecosystem.

Implemented components
- `app/identity/did.py`: DID creation and resolution helpers
- `app/identity/vc.py`: verifiable presentation creation and verification
- `app/biometrics/base.py`: biometric provider abstraction
- `app/biometrics/webauthn.py`: WebAuthn-oriented provider logic
- `app/biometrics/cancellable.py`: cancellable protected-template generation
- `app/storage/ipfs.py`: lightweight IPFS upload wrapper
- `app/chain/revocation.py`: in-memory revocation registry pattern
- `app/claims/proof_before_claim.py`: proof-before-claim enforcement service
- `contracts/RevocationRegistry.sol`: Solidity contract skeleton

Notes
- These are implementation primitives intended for local development and proof-of-concept integration.
- Production deployment should replace the in-memory registry with an actual blockchain-backed registry and a secure W3C VC stack.
