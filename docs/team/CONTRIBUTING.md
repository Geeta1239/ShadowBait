# Team Contribution Rules

## Branches

Use one branch per member:

```text
member-1-scanner
member-2-detection
member-3-backend
member-4-frontend-demo
```

`main` must remain demo-ready.

## Commit style

Use short, clear commits:

```text
feat(scanner): extract checkbox states
feat(detection): add false urgency baseline
feat(backend): add scan orchestration
feat(frontend): add results dashboard
fix(scanner): handle navigation timeout
```

## Integration rule

Members communicate through the frozen scanner JSON, finding JSON, evidence paths, and API contracts. Do not duplicate another member's module.

## First integration gate

The first complete flow must be:

```text
DarkShop
→ scanner
→ checked donation checkbox
→ DP01 finding
→ API result
→ frontend display
```
