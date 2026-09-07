#!/bin/bash

LOG_FILE="/var/log/auth.log"
LOG_FILE2="/var/log/syslog"
echo ""
echo "========================="
echo "   LINUX LOG ANALYZER"
echo "========================="

#check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Log file not found"
    exit 1
fi


#Count failed login attempts
FAILED_LOGINS=$( sudo grep -ci "Failed password" "$LOG_FILE")

#Count sucessful logins
SUCESSFUL_LOGINS=$( sudo grep -ci "Accepted" "$LOG_FILE")

#count invalid user login attempts
INVALID_USERS=$( sudo grep -ci "Invalid user" "$LOG_FILE")

ERROR_COUNT=$( sudo grep -ci "error" "$LOG_FILE2")
WARNING_COUNT=$( sudo grep -ci "warning" "$LOG_FILE2")
INFO_COUNT=$( sudo grep -ci "info" "$LOG_FILE2")
echo""
echo "Failed Login Attempts: $FAILED_LOGINS"
echo "Sucessful Logins: $SUCESSFUL_LOGINS"
echo "Invaild User Attempts: $INVALID_USERS"
echo "Erros: $ERROR_COUNT"
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
echo "   ERROR DETILS"
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
