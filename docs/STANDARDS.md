# Standards and External References

The tool is designed around standards and established research infrastructure rather than inventing replacements for them.

## NIST post-quantum cryptography

- FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM):
  https://csrc.nist.gov/pubs/fips/203/final
- FIPS 204 — Module-Lattice-Based Digital Signature Standard (ML-DSA):
  https://csrc.nist.gov/pubs/fips/204/final
- FIPS 205 — Stateless Hash-Based Digital Signature Standard (SLH-DSA):
  https://csrc.nist.gov/pubs/fips/205/final
- NIST Post-Quantum Cryptography project:
  https://csrc.nist.gov/projects/post-quantum-cryptography

These references define the standardized PQC algorithms that the software models in inventory, migration and provenance workflows.

## Merkle transparency

- RFC 9162 — Certificate Transparency Version 2.0:
  https://www.rfc-editor.org/rfc/rfc9162.html
- RFC 6962 — Certificate Transparency:
  https://www.rfc-editor.org/rfc/rfc6962.html

The provenance layer uses the same general Merkle-domain-separation and inclusion/consistency-proof ideas. It is an application-specific research log, not a Certificate Transparency service.

## Cryptographic bills of materials

- CycloneDX CBOM authoritative guide:
  https://cyclonedx.org/guides/OWASP_CycloneDX-Authoritative-Guide-to-CBOM-en.pdf
- CycloneDX specification:
  https://cyclonedx.org/specification/overview/

The inventory exporter is designed to produce a CycloneDX-style cryptographic inventory that can be extended into a complete CBOM for a controlled estate.

## Cryptographic agility

- NIST CSWP 39 — Considerations for Achieving Cryptographic Agility:
  https://csrc.nist.gov/pubs/cswp/39/final

This informs the repository's separation of discovery, verification, migration and repeatable audit operations.

## Important qualification

External standards define algorithms, formats and security guidance. They do not automatically validate the empirical hypotheses of the ECA-PQFA research program. The repository's own experiments and verification outputs must still be evaluated under their declared scope.
