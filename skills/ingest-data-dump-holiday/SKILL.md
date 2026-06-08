---
name: ingest-data-dump-holiday
description: Process files in ~/code/family-memory/data-dump/ into family memories attributed to Holiday (John's wife) via the family-memory-holiday MCP. Reads each file, extracts memories, deduplicates against existing memories, stores them, logs ingestion, and deletes the source file.
effort: max
disable-model-invocation: true
---

# Ingest Data Dump (Holiday)

Process files in `~/code/family-memory/data-dump/` into structured memories attributed to **Holiday** (John's wife — legal name Holly, goes by Holiday) via the `family-memory-holiday` MCP namespace.

## Tool namespace

Use the `mcp__family-memory-holiday__*` tools, which are pre-configured to attribute memories to `holiday`:

- `mcp__family-memory-holiday__recall`
- `mcp__family-memory-holiday__remember`
- `mcp__family-memory-holiday__update_memory`
- `mcp__family-memory-holiday__supersede_memory`
- `mcp__family-memory-holiday__list_file_ingestions`
- `mcp__family-memory-holiday__log_file_ingestion`

If these tools aren't available, the `family-memory-holiday` MCP server hasn't been registered yet — stop and tell the user to add it to `~/Library/Application Support/Claude/claude_desktop_config.json` and restart Claude Code.

## Workflow

### 1. Discover files

- List all files in `~/code/family-memory/data-dump/`. Skip hidden files and directories.
- If no files found, report "Nothing to process" and stop.

### 2. Check prior ingestions

- Call `mcp__family-memory-holiday__list_file_ingestions` to get already-processed files.
- For each file in `data-dump/`, compute its SHA-256 hash (`shasum -a 256`).
- **Skip** files whose filename AND hash match a prior ingestion (already processed, unchanged).
- **Flag** files whose filename matches but hash differs (content changed since last ingestion) — process these as changed files.

### 3. Process each file

For each new or changed file:

1. **Read** the file contents.
2. **Recall** — call `mcp__family-memory-holiday__recall` (no args) to load the current memory index — orient on existing tags and types.
3. **Extract memories** — read through the content and identify distinct facts, events, preferences, or knowledge worth remembering. For each candidate:
   - Call `mcp__family-memory-holiday__recall` with relevant keywords to check for duplicates or near-matches. Scope dedup to Holiday's memories with `contributors: "holiday"` so you don't conflate her memories with John's.
   - If a near-match exists: use `mcp__family-memory-holiday__update_memory` or `mcp__family-memory-holiday__supersede_memory` instead of creating a duplicate.
   - If new: use `mcp__family-memory-holiday__remember` with appropriate type, tags (reuse existing when possible), importance, and summary.
4. **Log the ingestion** — call `mcp__family-memory-holiday__log_file_ingestion` with the filename, SHA-256 hash, and count of memories created.
5. **Delete the source file** — `rm` the file from `~/code/family-memory/data-dump/`.

### 4. Report

Summarize what was processed:

- Files processed (with memory counts per file)
- Files skipped (already ingested, unchanged)
- Files flagged (hash changed — note what was updated)
- Total memories added/updated

## Guidelines

- **Quality over quantity.** Don't create a memory for every sentence. Extract meaningful, distinct facts.
- **Importance calibration:** 1=mundane, 5=notable, 10=life event. Most extracted memories land 3-6.
- **Dedup aggressively.** Always `recall` before `remember`. Update existing memories rather than creating near-duplicates.
- **Preserve context.** If a file contains dates or attributions, capture them in `valid_at`.
- **Large files.** For files over ~5000 words, process in logical sections rather than all at once.
- **First-person perspective.** Files in data-dump/ that come from Holiday should be read as her own notes/experiences, not as John talking about her.
