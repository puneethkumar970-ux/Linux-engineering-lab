#!/bin/bash

LOG_FILE="${1:-/var/log/auth.log}"
LOG_FILE2="${2:-/var/log/syslog}"
echo ""
echo "========================="
echo "   LINUX LOG ANALYZER"
echo "========================="

# Validate authentication log
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Authentication log not found: $LOG_FILE"
    exit 1
fi

if [ ! -r "$LOG_FILE" ]; then
    echo "ERROR: Authentication log is not readable: $LOG_FILE"
    exit 1
fi

# Validate system log
if [ ! -f "$LOG_FILE2" ]; then
    echo "ERROR: System log not found: $LOG_FILE2"
    exit 1
fi

if [ ! -r "$LOG_FILE2" ]; then
    echo "ERROR: System log is not readable: $LOG_FILE2"
    exit 1
fi


#Count failed login attempts
FAILED_LOGINS=$(grep -ci "Failed password" "$LOG_FILE")

#Count Successful Logins
SUCCESSFUL_LOGINS=$(grep -ci "Accepted" "$LOG_FILE")

#count invalid user login attempts
INVALID_USERS=$(grep -ci "Invalid user" "$LOG_FILE")

ERROR_COUNT=$(grep -ci "error" "$LOG_FILE2")
WARNING_COUNT=$(grep -ci "warning" "$LOG_FILE2")
INFO_COUNT=$(grep -ci "info" "$LOG_FILE2")
echo ""
echo "Failed Login Attempts: $FAILED_LOGINS"
echo "Successful Logins: $SUCCESSFUL_LOGINS"
echo "Invalid User Attempts: $INVALID_USERS"
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"
echo "Info: $INFO_COUNT"

echo ""
if [ "$FAILED_LOGINS" -gt 0 ]; then
    echo "STATUS: Failed logins detected!"
else
    echo ""
fi
echo ""

echo ""
echo "==========================="
echo "   FAILED LOGIN DETAILS"
echo "==========================="

if [ "$FAILED_LOGINS" -gt 0 ]; then
    grep -i "failed password" "$LOG_FILE" | tail -n 10 | \
    sed 's/^[^:]*: //' | \
    nl -w2 -s'. '
else
    echo ""
fi
echo ""
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "STATUS: Errors detected!"
else
    echo "STATUS: No errors detected!"
fi

echo ""
echo "==================="
echo "   ERROR DETAILS"
echo "==================="

if [ "$ERROR_COUNT" -gt 0 ]; then
    grep -i "error" "$LOG_FILE2" | tail -n 10 | \
    sed 's/^[^:]*: //' | \
    nl -w2 -s'. '
else
    echo ""
fi

echo ""
echo "=================================="
echo "   Analysis Completed: $(date)"
echo "=================================="
