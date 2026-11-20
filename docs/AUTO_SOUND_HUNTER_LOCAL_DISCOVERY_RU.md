# AUTO SOUND HUNTER — local discovery phase 1

## Implemented
- Select one local folder and scan it recursively on a worker thread.
- Inventory only `.wav`, `.wave` and `.sfz` files.
- Record root-relative path, file size, SHA-256, file kind and basic WAV container-header status.
- Bound the scan to a fixed maximum number of directory entries.
- Bound hashing to 128 MiB per file and 512 MiB total per scan; larger files or files beyond the budget remain inventoried with an explicit hash-skipped status.
- Display candidates as `NEEDS_REVIEW` and `UNREVIEWED`.

## Safety boundary
- No source file is moved, renamed, deleted, rewritten, extracted, copied or overwritten.
- Symbolic links and paths outside the selected root are skipped.
- ZIP/7z/RAR archives are not extracted.
- SFZ text is not parsed in this phase; WAV content is not classified musically.
- Filename, extension and hash do not prove guitar identity, technique, musical quality, ownership or distribution rights.
- This is a local inventory tool, not an AI sound classifier or licence verifier.
- SHA-256 uses JUCE Cryptography and is capped at 128 MiB per file / 512 MiB per scan; files over budget remain inventoried with a hash-skipped status.

Settings also shows read-only host telemetry: active sample rate, last processed block size and prepared maximum block size. The DAW remains the only place to change buffer settings.

## Curator
Curator remains disabled. It needs persistent review metadata, provenance, manual musical review and explicit licence evidence before factory promotion. The scanner never sets `LICENSE_APPROVED`.

## Tests
`ppgu_library_discovery_contracts` covers extension filtering, relative paths, hashes, deterministic ordering, unreviewed/licence states, scan limits and source immutability.
