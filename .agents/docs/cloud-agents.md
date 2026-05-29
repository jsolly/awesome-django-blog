# Cursor Cloud Agents

This repo is configured for **cloud-only development**: agents, skills, and rules are self-contained in git (no `.agents/` on the VM).

## Layout

```text
<repo>/
├── AGENTS.md                         # @.agents/AGENTS.md + ## Project / ## Purpose
├── .agents/                          # git subtree from dotagents (fleet branch)
│   ├── AGENTS.md                     # fleet persona + collaboration
│   ├── agents/                       # review-fix-push subagent prompts
│   ├── skills/                       # review-fix, review-fix-push
│   ├── rules/                        # canonical guideline markdown
│   └── .cursor/rules/                # Cursor auto-apply rules (.mdc symlinks)
├── .cursor/
│   ├── environment.json              # cloud VM install (+ optional terminals)
│   └── rules/                        # fleet symlinks + project-only rules
└── scripts/
    ├── update-agents-subtree.sh      # pull fleet updates from dotagents
    └── link-fleet-rules.sh           # wire .agents rules into .cursor/rules/
```

Cloud agents discover:

- **Skills** at `.agents/skills/`
- **Rules** at `.cursor/rules/` (fleet + project)
- **Instructions** from root `AGENTS.md`

They do **not** see `.agents/`, `~/.cursor/skills/`, or local symlinks outside the repo.

## Environment

See `.cursor/environment.json` in this repo. After a successful cloud run, capture a **`snapshot`** ID in that file (Cursor dashboard) to speed up future sessions.

## Fleet updates (dotagents subtree)

Fleet config is vendored from [dotagents](https://github.com/jsolly/dotagents) `fleet` branch via [git subtree](https://gist.github.com/SKempin/b7857a6ff6bddb05717cc17a44091202).

**Pull latest fleet into this repo:**

```bash
./scripts/update-agents-subtree.sh
```

**Edit fleet canonical copy** (on a machine with `.agents/`):

```bash
cd ~/.agents
# edit agents/, skills/, rules/
./scripts/refresh-fleet.sh
git add fleet/ && git commit -m "..."
./scripts/refresh-fleet.sh --push
```

Then in this repo: `./scripts/update-agents-subtree.sh`

**Push repo edits back to dotagents** (e.g. improved a skill in cloud):

```bash
git subtree push --prefix=.agents dotagents fleet
```

Then merge `origin/fleet` into `fleet/` on dotagents `main` (or re-run `refresh-fleet.sh` there to reconcile).

## Project-only vs fleet

| Asset | Location | Synced from dotagents? |
| --- | --- | --- |
| Fleet persona, review skills, code-style rules | `.agents/` | Yes (subtree) |
| Project-only Cursor rules | `.cursor/rules/*.mdc` (real files) | No |
| Dev environment | `.cursor/environment.json` | No (per-repo) |
| Commands, architecture | `AGENTS.md` sections below `@.agents/` | No |

## References

- [Cursor Cloud Agent setup](https://cursor.com/docs/cloud-agent/setup)
- [Cursor Skills](https://cursor.com/docs/skills)
