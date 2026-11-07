# Landlock exploration — non-wired candidate

Attempted the Linux Landlock ABI >= 3 with the `landlock_create_ruleset` syscall during v0.4 implementation. The running container returned **ENOSYS (errno 38)** for the ABI version query. Consequently the Landlock approach was **not** activated or claimed as enforced. A non-wired reference fragment is preserved as `landlock_guard_UNWIRED.py`; its correctness has not been established in an environment with Landlock available. No fallback was performed inside that attempted implementation.

The exercised v0.4 boundary is instead: `unshare` user/mount/network namespaces -> read-only remount all existing writable mountpoints -> `setpriv` drop all capabilities and set `no_new_privs` -> verify boundary -> import bounded worker. It is separate from Landlock and requires independent analysis of namespace behavior.
