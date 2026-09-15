#!/usr/bin/env sh
# Install the Oxagen branding skill into Claude Code from this checkout.
#
#   skills/install.sh                 link ~/.claude/skills/oxagen-branding to this checkout
#   skills/install.sh --project DIR   copy the skill into DIR/.claude/skills/oxagen-branding
#   skills/install.sh --check         report whether the installed skill matches this checkout
#   skills/install.sh --check --project DIR
#
# The per-user install is a symlink, so `git pull` in this repo updates the
# skill in every project on the machine. A project install is a copy, for a
# repo that vendors the skill and commits it (the oxagen monorepo does this
# through its own sync script; do not point this at it). Both are idempotent.
#
# ~/.claude/skills/brand-voice-guidelines is an older voice guide from July
# 2026. This skill supersedes it. The installer does not remove it.

set -eu

here=$(cd "$(dirname "$0")" && pwd)
src="$here/oxagen-branding"
mode=user
check=0
project=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check) check=1 ;;
    --project)
      shift
      [ $# -gt 0 ] || { echo "install.sh: --project needs a directory" >&2; exit 2; }
      mode=project
      project=$1
      ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "install.sh: unknown argument $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$src/SKILL.md" ] || { echo "install.sh: no skill at $src" >&2; exit 2; }

if [ "$mode" = user ]; then
  dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/oxagen-branding"
else
  dest="$project/.claude/skills/oxagen-branding"
fi

# Compare two trees by content, ignoring OS droppings. Exit 0 when identical.
same_tree() {
  diff -rq --exclude .DS_Store "$1" "$2" >/dev/null 2>&1
}

if [ "$check" = 1 ]; then
  if [ ! -e "$dest" ]; then
    echo "oxagen-branding: not installed at $dest"
    exit 1
  fi
  if [ "$mode" = user ] && [ -L "$dest" ]; then
    target=$(cd "$dest" 2>/dev/null && pwd -P || true)
    if [ "$target" = "$(cd "$src" && pwd -P)" ]; then
      echo "oxagen-branding: linked, $dest -> $src"
      exit 0
    fi
    echo "oxagen-branding: linked elsewhere, $dest -> ${target:-?}"
    exit 1
  fi
  if same_tree "$src" "$dest"; then
    echo "oxagen-branding: installed copy at $dest matches this checkout"
    exit 0
  fi
  echo "oxagen-branding: installed copy at $dest is stale; run $0${project:+ --project $project}"
  diff -rq --exclude .DS_Store "$src" "$dest" || true
  exit 1
fi

mkdir -p "$(dirname "$dest")"

if [ "$mode" = user ]; then
  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ]; then
    echo "install.sh: $dest exists and is not a link; move it aside first" >&2
    exit 1
  fi
  ln -s "$src" "$dest"
  echo "oxagen-branding: linked $dest -> $src"
else
  rm -rf "$dest"
  mkdir -p "$dest"
  (cd "$src" && tar cf - --exclude .DS_Store .) | (cd "$dest" && tar xf -)
  echo "oxagen-branding: copied into $dest"
fi
