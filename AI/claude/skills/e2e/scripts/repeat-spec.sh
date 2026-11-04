#!/usr/bin/env bash
# Run one test command repeatedly and report the actual pass ratio.
#
# A flake fix is only evidenced by repetition. "I ran it again and it passed" is
# exactly the reasoning this skill tells you not to accept, so this turns it into a
# number you can put in the report.
#
# Runner-agnostic: it runs whatever command you give it.
#
# Usage:
#   repeat-spec.sh -n 20 -- pnpm exec playwright test tests/checkout.spec.ts
#   repeat-spec.sh -n 50 --until-fail -- pnpm test -- --runTestsByPath src/foo.test.ts
#   repeat-spec.sh -n 10 --quiet -- npx cypress run --spec cypress/e2e/login.cy.ts
#
# Exit status: 0 only when every run passed.

set -uo pipefail

RUNS=10
UNTIL_FAIL=0
QUIET=0

usage() {
	sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
	exit "${1:-0}"
}

while [ $# -gt 0 ]; do
	case "$1" in
	-n | --runs)
		[ $# -ge 2 ] || {
			echo "error: $1 requires a value" >&2
			exit 2
		}
		RUNS="$2"
		shift 2
		;;
	--until-fail)
		UNTIL_FAIL=1
		shift
		;;
	-q | --quiet)
		QUIET=1
		shift
		;;
	-h | --help) usage 0 ;;
	--)
		shift
		break
		;;
	*)
		echo "error: unknown option $1 (did you forget -- before the command?)" >&2
		exit 2
		;;
	esac
done

case "$RUNS" in
'' | *[!0-9]*)
	echo "error: --runs must be a positive integer" >&2
	exit 2
	;;
esac
[ "$RUNS" -ge 1 ] || {
	echo "error: --runs must be at least 1" >&2
	exit 2
}
[ $# -ge 1 ] || {
	echo "error: no command given; put it after --" >&2
	exit 2
}

passed=0
failed=0
failed_runs=()
started=$(date +%s)

for i in $(seq 1 "$RUNS"); do
	if [ "$QUIET" -eq 1 ]; then
		"$@" >/dev/null 2>&1
	else
		printf '\n--- run %d/%d ---\n' "$i" "$RUNS"
		"$@"
	fi
	status=$?

	if [ $status -eq 0 ]; then
		passed=$((passed + 1))
		[ "$QUIET" -eq 1 ] && printf 'run %d/%d: pass\n' "$i" "$RUNS"
	else
		failed=$((failed + 1))
		failed_runs+=("$i")
		printf 'run %d/%d: FAIL (exit %d)\n' "$i" "$RUNS" "$status"
		if [ "$UNTIL_FAIL" -eq 1 ]; then
			printf '\nstopping at first failure on run %d\n' "$i"
			break
		fi
	fi
done

elapsed=$(($(date +%s) - started))
total=$((passed + failed))

printf '\n=========================================\n'
printf '%d/%d passed  (%d failed)  in %ds\n' "$passed" "$total" "$failed" "$elapsed"
if [ "$failed" -gt 0 ]; then
	printf 'failing runs: %s\n' "${failed_runs[*]}"
	printf 'A passing retry does not clear a flake. Inspect the FIRST failure.\n'
	exit 1
fi
printf 'No failures observed in %d runs. That bounds the flake rate; it does not\n' "$total"
printf 'prove the cause was fixed — say which you are claiming.\n'
