# 0.3-E Baseline — Verification Record

The file `PRJGENUI_Workforce_0.3-E_APPROVED.html` in this directory is the
approved baseline (schema 10) handover package supplied by Marizilena Silva
Fortes on 20 October 2026. It is a read-only reference copy: it must never be
edited, and reconciliation work happens in `docs/baseline-register.md`, not
here.

Verified at receipt (original filename:
`PRJGENUI_Workforce_0.3-E_APPROVED_a612d51e6d8e09b7707246f2e06a9db3.html`):

| Check | Expected | Verified | Result |
|---|---|---|---|
| MD5 | `a612d51e6d8e09b7707246f2e06a9db3` | `a612d51e6d8e09b7707246f2e06a9db3` | match |
| SHA-256 | `106a9c535d76bbc72d0e1875e0f10a2f65443da445dcd3057d2c5a83a1d0db71` | `106a9c535d76bbc72d0e1875e0f10a2f65443da445dcd3057d2c5a83a1d0db71` | match |
| Line count | 5,969 | 5,969 | match |

The file's read-only attribute is set at the filesystem level as an additional
guard. Re-verify before relying on this copy:

```powershell
Get-FileHash -Algorithm SHA256 .\PRJGENUI_Workforce_0.3-E_APPROVED.html
```

Note: line counts must include blank lines. PowerShell's
`Measure-Object -Line` skips blanks and under-reports; use
`(Get-Content <file>).Count`.
