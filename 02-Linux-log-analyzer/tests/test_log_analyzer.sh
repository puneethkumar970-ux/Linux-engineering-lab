#!/bin/bash
# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANALYZER="$SCRIPT_DIR/Log_analyzer.sh"
AUTH_LOG="$SCRIPT_DIR/test_logs/auth.log"
SYS_LOG="$SCRIPT_DIR/test_logs/syslog"
MISSING_LOG="$SCRIPT_DIR/test_logs/missing.log"
UNREADABLE_LOG="$SCRIPT_DIR/test_logs/unreadable.log"

# Test result counters
PASSED=0
FAILED=0

echo "================================"
echo "   LOG ANALYZER AUTOMATED TESTS"
echo "================================"

# Function to report test results
check_result() {
    if [ "$1" -eq 0 ]; then
        echo "PASS: $2"
        ((PASSED++))
    else
        echo "FAIL: $2"
        ((FAILED++))
    fi
}

# Test 1: Verify expected log counts
OUTPUT=$("$ANALYZER" "$AUTH_LOG" "$SYS_LOG" 2>&1)


if [[ "$OUTPUT" == *"Failed Login Attempts: 2"* ]] &&
   [[ "$OUTPUT" == *"Successful Logins: 2"* ]] &&
   [[ "$OUTPUT" == *"Invalid User Attempts: 1"* ]] &&
   [[ "$OUTPUT" == *"Errors: 2"* ]] &&
   [[ "$OUTPUT" == *"Warnings: 2"* ]] &&
   [[ "$OUTPUT" == *"Info: 2"* ]]; then
    check_result 0 "Correct log counts"
else
    check_result 1 "Correct log counts"
fi

OUTPUT=$("$ANALYZER" "$MISSING_LOG" "$SYS_LOG" 2>&1)
EXIT_CODE=$?

if [[ "$OUTPUT" == *"Authentication log not found"* ]] && [ "$EXIT_CODE" -eq 1 ]; then
    check_result 0 "Missing authentication log handled correctly"
else
    check_result 1 "Missing authentication log handled correctly"
fi

OUTPUT=$("$ANALYZER" "$AUTH_LOG" "$SCRIPT_DIR/test_logs/missing_syslog.log" 2>&1)
EXIT_CODE=$?

if [[ "$OUTPUT" == *"System log not found"* ]] && [ "$EXIT_CODE" -eq 1 ]; then
    check_result 0 "Missing system log handled correctly"
else
    check_result 1 "Missing system log handled correctly"
fi

chmod 000 "$UNREADABLE_LOG"

OUTPUT=$("$ANALYZER" "$UNREADABLE_LOG" "$SYS_LOG" 2>&1)
EXIT_CODE=$?

if [[ "$OUTPUT" == *"Authentication log is not readable"* ]] && [ "$EXIT_CODE" -eq 1 ]; then
    check_result 0 "Unreadable authentication log handled correctly"
else
    check_result 1 "Unreadable authentication log handled correctly"
fi

chmod 644 "$UNREADABLE_LOG"

OUTPUT=$("$ANALYZER" "$SCRIPT_DIR/test_logs/empty.log" "$SYS_LOG" 2>&1)
EXIT_CODE=$?

if [[ "$OUTPUT" == *"Failed Login Attempts: 0"* ]] && [[ "$OUTPUT" == *"Successful Logins: 0"* ]] && [[ "$OUTPUT" == *"Invalid User Attempts: 0"* ]] && [[ "$OUTPUT" == *"Errors: 2"* ]] && [[ "$OUTPUT" == *"Warnings: 2"* ]] && [[ "$OUTPUT" == *"Info: 2"* ]] && [ "$EXIT_CODE" -eq 0 ]; then

    check_result 0 "Empty authentication log handled correctly"
else
    check_result 1 "Empty authentication log handled correctly"
fi

echo ""
echo "================================"
echo "          TEST SUMMARY"
echo "================================"
echo "Tests Passed: $PASSED"
echo "Tests Failed: $FAILED"

if [ "$FAILED" -gt 0 ]; then
    exit 1
else
    exit 0
fi
