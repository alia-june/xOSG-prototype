# Proposed CI contract

Truth state: `GENERATED_SYNTHESIS`  
Authority effect: `NONE`

The required CI behavior is provider-neutral:

1. start from a clean accepted revision;
2. use an explicitly supported Python runtime;
3. install only from the hash-verified offline wheelhouse;
4. provide no production credentials and perform no deployment;
5. verify historical and development manifests before behavior tests;
6. run the ordered baseline and clean-stage checks with bounded output/time;
7. build the successor twice with `SOURCE_DATE_EPOCH=1704067200` and require
   byte-identical wheels;
8. retain reports and hashes without treating them as production acceptance.

The GitHub Actions file under `.github/workflows/ci.yml` implements the locally
verified Python 3.11–3.14 Windows matrix without deployment or credentials. It
is staged in a local repository but has no remote-run evidence.
