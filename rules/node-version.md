---
description: Fleet Node 24 standard — .nvmrc, engines, CI, Lambda runtime
alwaysApply: false
---

# Node.js version (fleet standard)

Personal repos target **Node 24** everywhere the runtime is under our control.

## Pinning

| Surface | Convention |
| --- | --- |
| Local dev | `.nvmrc` with `24` (or `24.x` where a minor pin is intentional) |
| `package.json` | `"engines": { "node": ">=24" }` or `"24.x"` when exact match is required |
| GitHub Actions | `actions/setup-node@v6` + `node-version-file: .nvmrc` |
| AWS Lambda | `Runtime: nodejs24.x` in SAM templates |

## Rationale

- Matches the current local baseline (Node 24 LTS).
- GitHub Actions is deprecating Node 20 for action runtimes; `checkout@v4` / `setup-node@v4` trigger warnings.
- Keeps Lambda, CI, and local dev on one major version so native addons and `engines` checks behave consistently.

## When bumping

1. Update `.nvmrc`, `engines`, CI workflows, and SAM `Runtime` together — not one in isolation.
2. Run the repo smoke suite (`check:ts`, tests, build) after the bump; watch native modules (`canvas`, `sharp`, etc.).
3. Pin cloud-agent snapshots after toolchain changes (`docs/cloud-agents.md` in repos that use Cursor Cloud).

## Exceptions

- Third-party templates or forks may lag; don't bump unless we're actively maintaining the repo.
- Python-only repos (e.g. Django) have no Node pin.
