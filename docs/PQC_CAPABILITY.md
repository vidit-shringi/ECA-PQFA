# PQC Capability

The provenance signer can use ML-DSA-65 through the system OpenSSL executable when that installation exposes the algorithm.

Check:

```bash
openssl version
openssl list -signature-algorithms | grep -i 'ML-DSA'
```

The tool reports `CLASSICAL_ONLY_PQC_UNAVAILABLE` when the local environment cannot perform the PQ signature step. It does not silently label a classical signature as PQC.

For long-term/high-assurance deployments, signing-key lifecycle, algorithm agility, re-signing/archival policy, and external trusted timestamping must be engineered separately.
