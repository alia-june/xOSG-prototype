# Omnifact Reference v0.8.0 — release sanitization summary

**Date:** 2026-11-10  
**Status:** documentation-only staging record; source ZIP not uploaded here.  
**Basis:** operator-supplied reference archive and local sanitized copy.

| Measure | Original source | Sanitized projection |
| --- | ---: | ---: |
| ZIP byte size | 174,096 | 173,207 |
| Archive entries | 103 | 99 |
| Original entries excluded | — | 6 |
| Original entries qualified | — | 2 |
| Newly added internal records | — | 2 |

**Sanitized SHA-256:** `a8ef4a25661c4bc6cd9f60b916337914682f08418fe42e49ec05ad74e8d121ed`

## Checks recorded

1. ZIP CRC, member safety, size bounds, non-duplication, and manifest checks on the input.
2. Original manifest: 102 of 102 declared member digests and lengths matched.
3. Bounded direct identifier, credential-marker, and local user-directory pattern scan of the sanitized contents: no direct matches.
4. Python static AST parsing, JSON parsing, TOML parsing, new manifest byte correspondence, and ZIP CRC checks passed.
5. No Omnifact source or tests were executed. Historical test totals remain unverified claims in this publication.

## Exclusions and qualifications

Six source entries were omitted because they were historical generated results or a manifest no longer valid after sanitization. Two documentation files received scope qualifications; a release notice and a new manifest were added.

The **private** file-by-file exclusion ledger is not released and should not be embedded, linked, or copied into this repository.

## Limitations and controls

The original source is unchanged. Pattern matching does not prove anonymity. No package-level redistribution license was established by the sanitization procedure. No program correctness, authority, security, resilience, production fitness, or general interoperability was attested.

**Release gate:** do not label a GitHub ZIP download as present until actual public ZIP bytes are uploaded and their SHA-256 matches the value above.
