#!/usr/bin/env sh
# Install the Oxagen branding skill's stub into Claude Code.
#
#   skills/install.sh                 install the stub at ~/.claude/skills/oxagen-branding
#   skills/install.sh --project DIR   install the stub at DIR/.claude/skills/oxagen-branding
#   skills/install.sh --check         report whether the installed skill is the current stub
#   skills/install.sh --check --project DIR
#
# The stub is one SKILL.md. It fetches the full skill from macanderson/oxagen-brand
# at the current main commit and follows it, so an installed stub never goes
# stale and nothing needs reinstalling when the brand changes. A project commits
# the stub, which is how cloud sessions get the skill: they load a repository's
# .claude/skills/ but not ~/.claude/skills/.
#
# Both modes replace an older install: the symlink to this checkout, or a full
# copy of skills/oxagen-branding/. Both are idempotent.
#
# ~/.claude/skills/brand-voice-guidelines is an older voice guide from July
# 2026. This skill supersedes it. The installer does not remove it.

set -eu

here=$(cd "$(dirname "$0")" && pwd)
stub="$here/stub/oxagen-branding/SKILL.md"
check=0
project=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check) check=1 ;;
    --project)
      shift
      [ $# -gt 0 ] || { echo "install.sh: --project needs a directory" >&2; exit 2; }
      project=$1
      ;;
    -h|--help) sed -n '2,19p' "$0"; exit 0 ;;
    *) echo "install.sh: unknown argument $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$stub" ] || { echo "install.sh: no stub at $stub" >&2; exit 2; }

if [ -n "$project" ]; then
  dest="$project/.claude/skills/oxagen-branding"
else
  dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/oxagen-branding"
fi

if [ "$check" = 1 ]; then
  if [ -L "$dest" ]; then
    echo "oxagen-branding: $dest is a link from an older install; run $0${project:+ --project $project}"
    exit 1
  fi
  if [ ! -f "$dest/SKILL.md" ]; then
    echo "oxagen-branding: not installed at $dest"
    exit 1
  fi
  extra=$(cd "$dest" && ls -A | sed '/^SKILL\.md$/d; /^\.DS_Store$/d')
  if cmp -s "$stub" "$dest/SKILL.md" && [ -z "$extra" ]; then
    echo "oxagen-branding: $dest is the current stub"
    exit 0
  fi
  echo "oxagen-branding: $dest is not the current stub; run $0${project:+ --project $project}"
  exit 1
fi

# Replace only what an earlier install of this skill left behind.
if [ -L "$dest" ]; then
  rm "$dest"
elif [ -e "$dest" ]; then
  if [ "$(sed -n '2p' "$dest/SKILL.md" 2>/dev/null)" != "name: oxagen-branding" ]; then
    echo "install.sh: $dest exists and is not an oxagen-branding install; move it aside first" >&2
    exit 1
  fi
  rm -rf "$dest"
fi

mkdir -p "$dest"
cp "$stub" "$dest/SKILL.md"
echo "oxagen-branding: installed the stub at $dest"
