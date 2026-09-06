#!/bin/bash

echo "=========================="
echo "  SYSTEM HEALTH MONITOR   "
echo "=========================="

echo ""
echo "Hostname: $(hostname)"
echo "Current Date and Time: $(date)"
echo "System Uptime: $(uptime -p)"

echo ""
echo "DISK USAGE"
echo ""
df -h /

echo ""
echo "MEMORY USAGE"
free -h

echo ""
echo "CPU INFORMATION"
lscpu | grep "Model name"

echo""
echo "TOP 5 PROCESSES BY CPU USAGE"
ps -eo pid,comm,%cpu --sort=%cpu | head -6

echo "Current Date:"
echo "$(date)"

echo "==================================="
echo "   SYSTEM HEALTH CHECK COMPLETED   "
echo "==================================="
