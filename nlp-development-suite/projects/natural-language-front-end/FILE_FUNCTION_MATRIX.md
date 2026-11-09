# File-function matrix for the omni front end

Research date: 2026-09-16. Status: research and generated design proposal, not an adopted sister-machine specification. The matrix inventories interactive file operations from PowerShell 7, GNU/Linux shell utilities, and Windows Command Prompt. “GNU” names utilities normally launched from a shell; these are not all Bash builtins. Representative commands establish that a function exists, not identical behavior across platforms. This is a functional inventory, not a claim to cover every switch or filesystem feature.

Scope includes direct file and directory operations, search, metadata, security, archives, and storage queries. It excludes shell programming: variables, loops, conditionals, functions, pipelines as a language feature, redirection syntax, command substitution, batch files, and script execution. File content editing remains in scope as a file operation, with controlled literal inputs rather than generated code.

**Status legend:** `Live` = a bounded capability exists in `omni_cli.py`; `Partial` = the capability exists but lacks common shell options; `Gap` = researched, not implemented. `P0` = next read-only foundation; `P1` = common writes after preview/validation; `P2` = advanced/file-system-specific; `P3` = specialized or platform-dependent. A shell command shown here is evidence of a function, never a command to pass through or execute verbatim.

| ID | Function / proposed capability | PowerShell example | GNU/Linux example | CMD / Windows example | Front end | Priority |
|---|---|---|---|---|---|---|
| F01 | Show workspace / `workspace` | `Get-Location` | `pwd` | `cd` | Live | — |
| F02 | Change current directory / `change_directory` | `Set-Location` | `cd` | `cd` | Gap | P0 |
| F03 | Resolve, join, split path / `inspect_path` | `Resolve-Path`, `Join-Path`, `Split-Path` | `realpath`, `dirname`, `basename` | no direct complete equivalent | Gap | P0 |
| F04 | Test existence and kind / `test_path` | `Test-Path`, `Get-Item` | `test`, `stat` | `dir` lookup; `if exist` is a scripting form | Gap | P0 |
| F05 | List one directory / `list_files` | `Get-ChildItem` | `ls` | `dir` | Partial: names and kind, 500 entries | P0 |
| F06 | Show recursive tree / `list_tree` | `Get-ChildItem -Recurse` | `find` | `tree`, `dir /s` | Gap | P0 |
| F07 | Inspect size, times, type, attributes / `file_info` | `Get-Item` | `stat` | `dir`, `attrib` | Gap | P0 |
| F08 | Filter files by name / `find_files` | `Get-ChildItem -Filter` | `find -name` | `dir /s`, `where /r` | Partial: substring only | P0 |
| F09 | Filter by size, age, type, depth / `filter_files` | `Get-ChildItem` properties | `find -size`, `-mtime`, `-type`, `-maxdepth` | `dir /a`, `/t`; `robocopy` filters | Gap | P0 |
| F10 | Literal text search / `search_text` | `Select-String -SimpleMatch` | `grep -F` | `findstr /l`, `find` | Partial: bounded UTF-8, case-insensitive | P0 |
| F11 | Pattern text search / `search_pattern` | `Select-String` | `grep` | `findstr /r` | Gap | P1 |
| F12 | Read text file / `read_file` | `Get-Content` | `cat` | `type` | Partial: bounded UTF-8 only | P0 |
| F13 | Read start/end or line range / `read_lines` | `Get-Content -TotalCount`, `-Tail` | `head`, `tail`, `sed` | `more` (paging) | Gap | P0 |
| F14 | Count lines, words, bytes / `count_content` | `Get-Content`, `Measure-Object` | `wc` | `find /c` (matching lines) | Gap | P0 |
| F15 | Inspect binary bytes / `inspect_bytes` | `Format-Hex` | `od`, `xxd` where installed | `certutil -encodehex` creates a hex output file | Gap | P2 |
| F16 | Compute/check hash / `hash_file` | `Get-FileHash` | `cksum`, `sha256sum` | `certutil -hashfile` | Gap | P0 |
| F17 | Compare bytes / `compare_files` | `Compare-Object` over bytes, hash | `cmp` | `comp`, `fc /b` | Gap | P0 |
| F18 | Compare text or directory trees / `diff_files` | `Compare-Object` | `diff` | `fc`; `robocopy /l` for tree differences | Gap | P1 |
| F19 | Show disk usage of path / `path_size` | `Get-ChildItem` with length aggregation | `du` | `dir /s` | Gap | P1 |
| F20 | Show free space / `free_space` | `Get-PSDrive` | `df` | `fsutil volume diskfree` | Gap | P1 |
| F21 | Create directory / `create_directory` | `New-Item -ItemType Directory` | `mkdir` | `mkdir` | Gap | P1 |
| F22 | Create empty file / `create_file` | `New-Item -ItemType File` | `touch` | `type nul > file` (redirection) | Gap | P1 |
| F23 | Write, append, clear literal content / `write_file` | `Set-Content`, `Add-Content`, `Clear-Content` | `tee`, `truncate` | `copy con`, redirection | Gap | P1 |
| F24 | Copy file or tree / `copy_path` | `Copy-Item` | `cp` | `copy`, `xcopy`, `robocopy` | Gap | P1 |
| F25 | Move or rename / `move_path`, `rename_path` | `Move-Item`, `Rename-Item` | `mv` | `move`, `ren` | Gap | P1 |
| F26 | Delete file or directory / `remove_path` | `Remove-Item` | `rm`, `rmdir` | `del`, `rmdir` | Gap | P1 |
| F27 | Change timestamp / `set_time` | `Get-Item` timestamp properties | `touch` | no direct general equivalent | Gap | P2 |
| F28 | Read/change file attributes / `file_attributes` | `Get-Item`, `Set-ItemProperty` | `stat`, `chattr` where supported | `attrib` | Gap | P2 |
| F29 | Create or inspect links / `file_link` | `New-Item -ItemType SymbolicLink` | `ln`, `readlink` | `mklink` | Gap | P2 |
| F30 | Read permissions / `read_permissions` | `Get-Acl` | `stat`, `getfacl` | `icacls` | Gap | P2 |
| F31 | Set permissions/owner / `set_permissions` | `Set-Acl` | `chmod`, `chown`, `setfacl` | `icacls`, `takeown` | Gap | P2 |
| F32 | Inspect alternate streams/extended attributes / `extended_metadata` | `Get-Item -Stream` | `getfattr` where supported | `dir /r`, `fsutil` | Gap | P3 |
| F33 | List archive members / `list_archive` | `tar -t` where available; ZIP API | `tar -t` | `tar -t` where available | Gap | P2 |
| F34 | Create archive / `create_archive` | `Compress-Archive` | `tar -c` | `tar -c` where available | Gap | P2 |
| F35 | Extract archive / `extract_archive` | `Expand-Archive` | `tar -x` | `tar -x` where available | Gap | P2 |
| F36 | Check archive readability and extracted content / `verify_archive` | ZIP API inspection and CRC | `tar -t`; `tar -d` compares with disk | tool-dependent | Gap | P2 |
| F37 | Mirror/synchronize directory / `sync_tree` | `Copy-Item` composition | `rsync` where installed | `robocopy /mir` | Gap | P2 |
| F38 | Inspect compressed/encrypted state / `storage_attributes` | item/volume properties | filesystem-specific tools | `compact`, `cipher` | Gap | P3 |
| F39 | Open file with associated app / `open_file` | `Invoke-Item` | `xdg-open` where installed | `start` | Gap | P3 |
| F40 | Read mounted drives/volumes / `list_volumes` | `Get-PSDrive`, storage module | `df`, `mount` | `fsutil fsinfo drives` | Gap | P3 |

## Source ledger

Primary documentation consulted for the function classes above:

- PowerShell file operations: [Microsoft.PowerShell.Management cmdlet index](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/?view=powershell-7.5), [Select-String](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string?view=powershell-7.6), [Get-FileHash](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash?view=powershell-7.5), [Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-7.5), [Expand-Archive](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/expand-archive?view=powershell-7.6).
- GNU/Linux utilities: [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/coreutils.html), [GNU Findutils manual](https://www.gnu.org/software/findutils/manual/html_mono/find.html), [GNU Grep manual](https://www.gnu.org/s/grep/manual/grep.html), [GNU Diffutils manual](https://www.gnu.org/software/diffutils/manual/diffutils.html), [GNU tar manual](https://www.gnu.org/software/tar/manual/tar.html).
- Windows command shell: [Microsoft Windows commands index](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands), [dir](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/dir), [findstr](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/findstr), [robocopy](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy), [mklink](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mklink), [icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls), [certutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil), [fsutil volume](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-volume).
- Optional synchronization utility: [rsync manpage](https://rsync.samba.org/ftp/rsync/rsync.1.html).

## Interpretation limits

Some representative commands require optional packages, operating-system-specific filesystems, or elevated rights. For example, `rsync`, `getfacl`, and `getfattr` are not universal GNU/Linux base utilities, and archive verification is not a single equivalent operation across tools. CMD rows that require redirection or `if` show a shell mechanism for comparison; the NLP front end would expose a typed file operation, not implement that shell syntax. No feature in this matrix is marked live unless its current behavior was verified in `omni_cli.py`.
