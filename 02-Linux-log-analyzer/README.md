# Linux Log Analyzer

A Bash-based Linux log analysis tool that examines authentication and system logs, identifies important events, and generates a structured diagnostic summary.

## Features

- Analyzes Linux authentication and system logs.
- Counts failed login attempts.
- Counts successful login attempts.
- Identifies invalid user attempts.
- Counts system errors, warnings, and informational messages.
- Displays detailed error entries.
- Handles missing log files.
- Detects unreadable log files.
- Handles empty authentication logs.
- Provides automated test coverage.

## Technologies

- Linux
- Bash Shell Scripting
- grep
- sed
- Git

## Project Structure

```text
02-Linux-log-analyzer/
├── Log_analyzer.sh
├── README.md
├── test_logs/
│   ├── auth.log
│   ├── syslog
│   ├── empty.log
│   └── unreadable.log
└── tests/
    └── test_log_analyzer.sh
```

## Prerequisites

- Linux environment
- Bash shell
- Standard Linux utilities

## How to Run

Navigate into the project directory:

```bash
cd 02-Linux-log-analyzer
```

Make the script executable:

```bash
chmod +x Log_analyzer.sh
```

Run the analyzer with the authentication and system log paths:

```bash
./Log_analyzer.sh test_logs/auth.log test_logs/syslog
```

## Automated Testing

Run the automated test suite:

```bash
bash tests/test_log_analyzer.sh
```

### Test Scenarios

1. Correct log counts.
2. Missing authentication log.
3. Missing system log.
4. Unreadable authentication log.
5. Empty authentication log.

### Test Results

**5 tests passed | 0 tests failed**

## Skills Demonstrated

Linux Administration | Bash Scripting | Log Analysis | Troubleshooting | File Permissions | Error Handling | Test Automation | Git
