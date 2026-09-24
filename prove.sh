set -o pipefail
[ -z "$1" ] && { echo 'Arg1: path to .mlw file' ; exit 1; }
[ "${WHY3_SPLITVC+x}" ] && split_opt='-a split_vc'
why3 prove -P ${WHY3_PROVER:-z3} -t ${WHY3_TIMEOUT:-10} "$1" $split_opt $WHY3_OPTS | tee _"$1".proven
echo '-----------------------------------------------------'
grep -P -B 2 '^Prover result is: (?!Valid)' _"$1".proven | tee _"$1".error
[ $? -eq 0 ] && { echo; echo '*** ERROR: NOT PROVEN! ***'; exit 1; } || exit 0
