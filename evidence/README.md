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
