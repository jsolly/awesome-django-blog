#!/usr/bin/env bash
# Canonical source: jsolly/dotagents templates/github/ci-verified-tree.sh.
# Run immediately after the default checkout, before validation mutates files.
# Evidence is an artifact name from the latest PR run of this same workflow.
# Any missing/ambiguous evidence means full validation, never an unproven skip.
set -euo pipefail

tree=$(git rev-parse 'HEAD^{tree}')
[[ "$tree" =~ ^[0-9a-f]{40}$ ]]
printf 'tree=%s\n' "$tree" >> "$GITHUB_OUTPUT"
printf '%s\n' "$tree" > "$RUNNER_TEMP/ci-tree-$GITHUB_JOB.txt"

verified_run() {
  [[ "$GITHUB_EVENT_NAME" == push ]] || return 1
  jq -e '.forced == false and .created == false and .deleted == false' \
    "$GITHUB_EVENT_PATH" >/dev/null || return 1
  local repo branch landed prs head workflow runs candidate run_id attempt artifacts expected
  repo=$GITHUB_REPOSITORY
  branch=$(jq -er '.repository.default_branch' "$GITHUB_EVENT_PATH") || return 1
  [[ "$GITHUB_REF" == "refs/heads/$branch" ]] || return 1
  landed=$(git rev-parse HEAD) || return 1
  [[ "$landed" == "$GITHUB_SHA" ]] || return 1

  prs=$(gh api "repos/$repo/commits/$landed/pulls?per_page=100") || return 1
  head=$(jq -er --arg sha "$landed" --arg repo "$repo" --arg branch "$branch" '
    [.[] | select(.merged_at != null and .merge_commit_sha == $sha
      and .base.repo.full_name == $repo and .head.repo.full_name == $repo
      and .base.ref == $branch)]
    | if length == 1 then .[0].head.sha else empty end
    | select(test("^[0-9a-f]{40}$"))' <<< "$prs") || return 1

  workflow=$(gh api "repos/$repo/actions/runs/$GITHUB_RUN_ID" --jq .workflow_id) || return 1
  [[ "$workflow" =~ ^[0-9]+$ ]] || return 1
  runs=$(gh api "repos/$repo/actions/workflows/$workflow/runs?event=pull_request&head_sha=$head&per_page=100") || return 1
  # Choose the newest run BEFORE requiring success. A newer red/pending rerun
  # must not be hidden by an older green run. run_attempt guards retained artifacts.
  candidate=$(jq -ec --arg head "$head" --arg repo "$repo" '
    [.workflow_runs[] | select(.event == "pull_request" and .head_sha == $head
      and .repository.full_name == $repo and .head_repository.full_name == $repo)]
    | sort_by(.id) | last
    | select(.status == "completed" and .conclusion == "success")' <<< "$runs") || return 1
  run_id=$(jq -er '.id' <<< "$candidate") || return 1
  attempt=$(jq -er '.run_attempt' <<< "$candidate") || return 1
  [[ "$run_id" =~ ^[0-9]+$ && "$attempt" =~ ^[1-9][0-9]*$ ]] || return 1
  expected="ci-tree-v1-$GITHUB_JOB-$tree-$attempt"
  artifacts=$(gh api "repos/$repo/actions/runs/$run_id/artifacts?per_page=100") || return 1
  jq -e --arg name "$expected" '
    [.artifacts[] | select(.name == $name and .expired == false)] | length == 1
  ' <<< "$artifacts" >/dev/null || return 1
  printf '%s\n' "$run_id"
}

if run_id=$(verified_run); then
  printf 'run_full=false\n' >> "$GITHUB_OUTPUT"
  message="Reusing validated tree $tree for job $GITHUB_JOB from PR run $run_id."
else
  printf 'run_full=true\n' >> "$GITHUB_OUTPUT"
  message="Running full validation: no matching successful PR tree proof for job $GITHUB_JOB."
fi
printf '%s\n' "$message"
printf '%s\n' "$message" >> "$GITHUB_STEP_SUMMARY"
