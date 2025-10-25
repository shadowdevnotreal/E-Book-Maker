#!/usr/bin/env bash
set -euo pipefail

### User-specific (you gave these) ####################################
: "${GIT_NAME:=shadowdevnotreal}"
: "${GIT_EMAIL:=43219706+shadowdevnotreal@users.noreply.github.com}"

### Behavior knobs (override via env if needed) #######################
: "${REPO_DIR:=E-Book-Maker}"                # original repo name
: "${BRANCH:=main}"                          # target default branch
: "${SIZE_THRESHOLD_BYTES:=100000000}"       # 100 MB
: "${EXCLUDE_PATTERNS:="setup/ *.exe"}"      # excluded from Git history
: "${TAG:=fresh-$(date +%Y%m%d-%H%M%S)}"     # release tag & clean dir suffix
: "${RELEASE_TITLE:=Fresh start}"            # release title
: "${RELEASE_NOTES:=Clean repo; binaries moved to release assets.}"
: "${NUKE_REMOTE_BRANCHES:=1}"               # delete all remote branches except $BRANCH
: "${NUKE_REMOTE_TAGS:=1}"                   # delete all remote tags
: "${YES:=1}"                                # auto-confirm destructive steps

### Helpers ############################################################
err(){ echo "ERROR: $*" >&2; exit 1; }
have(){ command -v "$1" >/dev/null 2>&1; }
confirm(){ [[ "${YES}" = "1" ]] && return 0; read -r -p "$1 [y/N] " a; [[ $a =~ ^[Yy]$ ]]; }

### Start in parent folder containing ${REPO_DIR}
[[ -d "${REPO_DIR}" ]] || err "Repo folder '${REPO_DIR}' not found in $(pwd)"
cd "${REPO_DIR}"

have git || err "git not found"

# Ensure origin exists
ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
[[ -n "${ORIGIN_URL}" ]] || err "No 'origin' remote. Set it first: git remote add origin <URL>"

# Set identity (repo-local so we don't touch global config)
git config user.name  "${GIT_NAME}"
git config user.email "${GIT_EMAIL}"

echo "Identity: $(git config user.name) <$(git config user.email)>"
echo "Origin:   ${ORIGIN_URL}"

# Paths
REPO_ROOT="$(pwd)"
PARENT_DIR="$(cd .. && pwd)"
CLEAN_DIR="${PARENT_DIR}/${REPO_DIR}-src-${TAG}"
BIG_DIR="${PARENT_DIR}/_big_${REPO_DIR}_${TAG}"

mkdir -p "${BIG_DIR}"
[[ ! -e "${CLEAN_DIR}" ]] || err "Clean dir already exists: ${CLEAN_DIR}"

echo "==> Scanning for large files and patterns to move to release assets..."
# Find >100MB
mapfile -t BIG_BY_SIZE < <(find . -type f -size +"$((SIZE_THRESHOLD_BYTES/1024))"k -print 2>/dev/null | sed 's|^\./||')
# Find by patterns
PATTERN_FILES=()
for pat in ${EXCLUDE_PATTERNS}; do
  while IFS= read -r -d '' f; do
    f="${f#./}"; PATTERN_FILES+=("$f")
  done < <(find . -type f -path "./.git/*" -prune -o -name "$pat" -print0 2>/dev/null)
done

# Unique union
declare -A seen; ALL_BIG=()
for f in "${BIG_BY_SIZE[@]:-}"; do [[ -f "$f" && -z "${seen[$f]:-}" ]] && ALL_BIG+=("$f") && seen[$f]=1; done
for f in "${PATTERN_FILES[@]:-}"; do [[ -f "$f" && -z "${seen[$f]:-}" ]] && ALL_BIG+=("$f") && seen[$f]=1; done

if ((${#ALL_BIG[@]})); then
  echo "Will move ${#ALL_BIG[@]} file(s) to release assets:"
  printf '  - %s\n' "${ALL_BIG[@]}"
  echo "Copying to: ${BIG_DIR}"
  for f in "${ALL_BIG[@]}"; do
    mkdir -p "${BIG_DIR}/$(dirname "$f")"
    cp -f -- "$f" "${BIG_DIR}/$f"
  done
else
  echo "No large files found by threshold/patterns."
fi

echo "==> Creating a clean, historyless copy at: ${CLEAN_DIR}"
mkdir -p "${CLEAN_DIR}"
if have rsync; then
  RSYNC_EXCLUDES=(--exclude='.git')
  for pat in ${EXCLUDE_PATTERNS}; do RSYNC_EXCLUDES+=(--exclude="$pat"); done
  rsync -a "${RSYNC_EXCLUDES[@]}" "./" "${CLEAN_DIR}/"
else
  echo "rsync not found; using tar"
  TAR_EXCLUDES=(--exclude=.git)
  for pat in ${EXCLUDE_PATTERNS}; do TAR_EXCLUDES+=(--exclude="$pat"); done
  ( tar -cf - "${TAR_EXCLUDES[@]}" . ) | ( cd "${CLEAN_DIR}" && tar -xf - )
fi

# Size-based cleanup pass in the clean copy
if ((${#BIG_BY_SIZE[@]:-0})); then
  for f in "${BIG_BY_SIZE[@]}"; do
    [[ -f "${CLEAN_DIR}/${f}" ]] && rm -f -- "${CLEAN_DIR}/${f}" || true
  done
fi

echo "==> Initializing fresh Git repo in clean copy and pushing (force)..."
cd "${CLEAN_DIR}"
git init
git checkout -b "${BRANCH}"

# Add robust .gitignore
{
  echo "# Added by reset script ${TAG}"
  for pat in ${EXCLUDE_PATTERNS}; do echo "${pat}"; done
  echo "*.zip"
  echo "*.7z"
} >> .gitignore

git add .
git -c user.name="${GIT_NAME}" -c user.email="${GIT_EMAIL}" \
  commit -m "Fresh start (${TAG}): source-only; binaries moved to release assets."
git remote add origin "${ORIGIN_URL}"

echo "About to OVERWRITE remote history on '${ORIGIN_URL}' (${BRANCH})"
confirm "Proceed with force-push?" || err "Aborted"

git fetch origin || true
git push --force -u origin "${BRANCH}"

# Optional: delete ALL other remote branches
if [[ "${NUKE_REMOTE_BRANCHES}" = "1" ]]; then
  echo "==> Deleting remote branches except '${BRANCH}'"
  mapfile -t REMOTE_BRANCHES < <(git ls-remote --heads origin | awk '{print $2}' | sed 's|refs/heads/||')
  for rb in "${REMOTE_BRANCHES[@]:-}"; do
    [[ "$rb" == "${BRANCH}" ]] && continue
    git push origin --delete "$rb" || true
  done
fi

# Optional: delete ALL remote tags
if [[ "${NUKE_REMOTE_TAGS}" = "1" ]]; then
  echo "==> Deleting all remote tags"
  mapfile -t REMOTE_TAGS < <(git ls-remote --tags origin | awk '{print $2}' | sed 's|refs/tags/||')
  for t in "${REMOTE_TAGS[@]:-}"; do
    git push origin ":refs/tags/${t}" || true
  done
fi

# Make a fresh release with the big files
if ((${#ALL_BIG[@]})); then
  if have gh; then
    echo "==> Creating GitHub Release '${TAG}' with assets from: ${BIG_DIR}"
    # shellcheck disable=SC2086
    gh release create "${TAG}" "${BIG_DIR}"/** \
      --title "${RELEASE_TITLE}" \
      --notes "${RELEASE_NOTES}" || err "Release creation failed"
  else
    echo "==> 'gh' CLI not found; skipping automatic release."
    echo "   To upload manually after installing gh and logging in:"
    echo "   gh release create ${TAG} \"${BIG_DIR}\"/** --title \"${RELEASE_TITLE}\" --notes \"${RELEASE_NOTES}\""
  fi
else
  echo "==> No large assets to release."
fi

echo "==> Done."
echo "Clean repo: ${CLEAN_DIR}"
echo "Release tag: ${TAG}"
echo "Assets dir:  ${BIG_DIR}"
