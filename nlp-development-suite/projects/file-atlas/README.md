# File Atlas

A browser front end for the deterministic read-only file command slice in `omni_cli.py`.

File Atlas loads the same `omni-alias/0.1` catalog and supports workspace display, directory listing, bounded UTF-8 file reading, filename search, and literal text search. Parsing and execution remain separate. Every collision displays all ranked meanings and requires an explicit choice.

The interface starts with a built-in demonstration workspace. A user can choose a local folder through the browser's File System Access API; a directory-input fallback is provided when that API is unavailable. File contents are processed in the browser session and are not sent to an application backend.

Run `build_data.py` after changing `../command_aliases.json`, then serve `dist/` with a static web server.

## Bounds

- 500 entries per directory listing.
- 128 KiB per text file; UTF-8 only, with NUL bytes rejected.
- 1,000 files and 200 directories per recursive search.
- 8 MiB total text-search input.
- 50 filename or matching-line results.
- `.git`, `.venv`, `.wn_data`, and `__pycache__` are skipped during recursive search.

No mutation capability, shell, subprocess, WordNet execution, web provider, or LLM provider is present in this browser slice.
