#!/usr/bin/env bash
# Rebuild every part from its command script. Run from anywhere; paths in the
# scripts are relative to the repo root.
#
#   tools/build.sh                 # all parts  (<product>/cad/<PN>.json -> <PN>.sc + exports)
#   tools/build.sh gripper_tips    # one product (or a version folder, e.g. strandbeest_gripper/v2_dual-finger)
#   tools/build.sh --assemblies    # also run <PN>.check.json overlays (slow: clearance ~10 min)
#
# Part scripts are <PN>_<name>.json (no dot in the stem). Overlays are <PN>_<name>.check.json:
# they run on top of the first part of their product and save <PN>.sc.
set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."

ASSY=0
PRODUCTS=()
for a in "$@"; do
  case "$a" in
    --assemblies) ASSY=1 ;;
    *) PRODUCTS+=("$a") ;;
  esac
done
if [ ${#PRODUCTS[@]} -eq 0 ]; then
  # every folder that holds a cad/ directory (products, or version folders inside a product)
  mapfile -t PRODUCTS < <(find . -path ./.git -prune -o -path '*/cad/*.json' -printf '%h\n' | sed 's#^\./##; s#/cad$##' | sort -u)
fi

fail=0
for p in "${PRODUCTS[@]}"; do
  [ -d "$p/cad" ] || { echo "FAILED: no product '$p'"; fail=1; continue; }
  for s in "$p"/cad/*.json; do
    stem=$(basename "$s" .json)
    case "$stem" in *.*) continue ;; esac          # skip overlays (*.check.json)
    # assemblies built from their own script (e.g. GRIP-9002.json) go through here too
    echo "== $s"
    if ! solidcraft-cli run "$s" --save "$p/cad/$stem.sc" >/dev/null; then
      echo "FAILED: $s"; fail=1
    fi
  done
  if [ "$ASSY" = 1 ]; then
    for s in "$p"/cad/*.check.json; do
      stem=$(basename "$s" .check.json)
      # base = the product's first part design (<PN>.json with no dot, not an assembly 9xxx)
      base=""
      for pj in "$p"/cad/*.json; do
        ps=$(basename "$pj" .json)
        case "$ps" in *.*|*-9[0-9][0-9][0-9]|*-9[0-9][0-9][0-9]_*) continue ;; esac
        base="$p/cad/$ps.sc"; break
      done
      if [ -z "$base" ] || [ ! -e "$base" ]; then echo "FAILED: $s (no part design to run on)"; fail=1; continue; fi
      echo "== $s (on $base)"
      solidcraft-cli run "$s" --in "$base" --save "$p/cad/$stem.sc" --results \
        || { echo "FAILED: $s"; fail=1; }
    done
  fi
done
exit $fail
