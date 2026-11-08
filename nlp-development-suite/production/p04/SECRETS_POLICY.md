# Proposed secrets policy

Truth state: `GENERATED_SYNTHESIS`  
Authority effect: `NONE`

The offline staging path requires no application credentials. CI must use no
production secret and must deny network access during installation and tests
once the reviewed wheelhouse is available.

- Never commit `.env` files, private keys, tokens, certificates, or credential
  exports.
- Use short-lived, least-privilege credentials only for an explicitly accepted
  external action.
- Do not expose secrets to pull requests from untrusted forks.
- Treat logs, reports, fixtures, archives, and exception text as possible leak
  surfaces.
- Rotate and revoke a discovered credential; deleting it from the latest tree
  does not remove it from history.
- `SCAN_SECRETS.py` is a high-confidence local guard, not a full security audit.
