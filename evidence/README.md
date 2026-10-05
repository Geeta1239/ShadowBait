# Evidence Output Layout

All runtime artifacts are saved inside this repository under `evidence/`.

## Standalone scanner

From the repository root:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 python3 scripts/member1_inspection.py
```

The scanner creates a timestamped run:

```text
evidence/scans/SCAN-<UTC-timestamp>/
├── screenshots/       # PNG screenshots
├── dom/               # HTML, visible text JSON, and element-state JSON
└── scan.json          # Complete scanner output
```

Reports are written to:

```text
evidence/reports/SCAN-<UTC-timestamp>/response.json
evidence/reports/response.json       # latest report convenience copy
```

Use `SHADOWBAIT_SCAN_ID=SCAN-001` when a stable scan ID is required.
Use `SHADOWBAIT_EVIDENCE_DIR=/absolute/path/to/evidence` only when intentionally overriding the repository default.

## Live inspection page

Start the API from the repository root:

```bash
SHADOWBAIT_TARGET_URL=http://127.0.0.1:3000 python3 backend/inspection_server.py
```

Then open `/inspect` and click **Start Inspection**. Each run is saved to:

```text
evidence/live-scans/live-<UTC-timestamp>/
├── screenshots/
├── dom/
├── scan.json
├── report.json
└── response.json
```

`response.json` is now produced by both scanner paths. Generated scan folders are ignored by Git so local evidence does not accidentally get committed.

## Important

Do not run the scanner with the old hard-coded `/home/ubuntu/projects/ShadowBaitRemote/...` path. The fixed script resolves its default output relative to the repository containing `scripts/member1_inspection.py`.

## Automated verification

The repository includes `scripts/verify_scan_outputs.py`.

To run a fresh scan and verify it automatically:

```bash
python scripts/verify_scan_outputs.py --run-scan --url http://127.0.0.1:3000
```

On Windows, run this after activating `.venv` and installing Chromium with `python -m playwright install chromium`.

To verify the newest existing scan without starting another scan:

```bash
python scripts/verify_scan_outputs.py
```

To verify one specific scan:

```bash
python scripts/verify_scan_outputs.py --scan-dir evidence/scans/SCAN-20261005T120000Z
```

The verifier exits with code `1` if `scan.json`, `response.json`, screenshots, DOM files, or referenced artifacts are missing/invalid, or if the scan summary does not match the generated data.

A successful run prints `PASS: scan output is complete`. In PowerShell, you can fail a command sequence when verification fails:

```powershell
python scripts\verify_scan_outputs.py --run-scan --url http://127.0.0.1:3000
if ($LASTEXITCODE -ne 0) { throw "ShadowBait evidence verification failed" }
```
