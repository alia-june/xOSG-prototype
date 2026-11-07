# Primary technical references and observed limitations

Research date: 2026-11-06.

## Linux

- [`unshare(1)`](https://man7.org/linux/man-pages/man1/unshare.1.html): distinct user, mount and network namespaces; mount propagation handling.
- [Linux kernel Landlock documentation](https://kernel.org/doc/html/next/userspace-api/landlock.html): write-restriction ruleset and restrictions on inherited child tasks. A Landlock ABI version query returned `ENOSYS` in the local test runtime, so Landlock was **not** activated.
- [`landlock(7)`](https://man7.org/linux/man-pages/man7/landlock.7.html): requirement to check actual kernel ABI and known limitations.

## Windows (future target only)

- [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- [Microsoft Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)
- [Microsoft AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)

**Source classification:** these are external technical references, not proof of local execution. All local runtime claims derive from the included commands and captured probe results.
