## Summary
- [ ] Scope and motivation are clearly described.
- [ ] Related docs/spec updates are included when behavior changed.

## Validation Checklist
- [ ] ✅ Unit tests passed (required)
- [ ] ✅ API tests passed **or** ⚠️ skipped with explicit environment reason
- [ ] ✅ Optional tests reviewed (`ragas-optional`) and status documented
- [ ] ✅ New/updated env vars documented

## Test Evidence
Paste exact commands and results:

```bash
# ex) cd backend && pytest -q -m "not api and not ragas_optional"
```

## Environment Constraints (if any)
- [ ] None
- [ ] Present (describe exact limitation and impact)

If present, use one standard sentence:
> API tests were skipped due to missing FastAPI runtime dependency in the current environment.
