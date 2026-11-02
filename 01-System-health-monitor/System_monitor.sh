#!/bin/bash

check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERROR: Required command '$1' is not installed."
        return 1
    fi
}



echo "=========================="
echo "  SYSTEM HEALTH MONITOR   "
echo "=========================="

echo ""
if check_command hostname; then
    echo "Hostname: $(hostname)"
else
    echo "Hostname: Unavailable"
fi
# Current date and time
if check_command date; then
    echo "Current Date and Time: $(date)"
else
    echo "Current Date and Time: Unavailable"
fi

# System uptime
if check_command uptime; then
    echo "System Uptime: $(uptime -p)"
else
    echo "System Uptime: Unavailable"
fi

echo ""
echo "DISK USAGE"
echo ""

if check_command df; then
    df -h /
else
    echo "Disk usage information: Unavailable"
fi

echo ""
echo "MEMORY USAGE"

if check_command free; then
    free -h
else
    echo "Memory usage information: Unavailable"
fi

echo ""
echo "CPU INFORMATION"

if check_command lscpu && check_command grep; then
    lscpu | grep "Model name"
else
    echo "CPU information: Unavailable"
fi

echo ""
echo "TOP 5 PROCESSES BY CPU USAGE"

if check_command ps && check_command head; then
    ps -eo pid,comm,%cpu --sort=%cpu | head -6
else
    echo "Process information: Unavailable"
fi

echo "==================================="
echo "   SYSTEM HEALTH CHECK COMPLETED   "
echo "==================================="
