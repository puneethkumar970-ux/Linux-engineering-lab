# Linux System Health Monitor

A lightweight Bash-based monitoring tool that collects essential Linux system information and displays it in a structured, easy-to-read report.

## Overview

The Linux System Health Monitor provides a quick snapshot of a system's current status using standard Linux command-line utilities.

It includes command availability checks and graceful fallback messages to ensure that missing utilities do not interrupt the entire monitoring process.

## Features

- **System Information:** Displays the hostname.
- **Date and Time:** Displays the current system date and time.
- **System Uptime:** Reports how long the system has been running.
- **Disk Usage:** Displays filesystem capacity and available space.
- **Memory Usage:** Reports total, used, free and available memory.
- **CPU Information:** Identifies the CPU model.
- **Process Monitoring:** Lists the top five processes by CPU usage.
- **Error Handling:** Detects unavailable system utilities and displays appropriate fallback messages.
- **Execution Continuity:** Continues collecting other system information when an individual utility is unavailable.

## Technologies Used

- Linux
- Bash Shell Scripting
- Linux command-line utilities
- Git and GitHub

## Requirements

- A Linux environment or compatible WSL distribution.
- Bash shell.
- Standard Linux utilities: `hostname`, `date`, `uptime`, `df`, `free`, `lscpu`, `grep`, `ps` and `head`.

## How to Run

Clone the repository:

```bash
git clone https://github.com/puneethkumar970-ux/Linux-engineering-lab.git
```

Navigate to the project directory:

```bash
cd Linux-engineering-lab/01-System-health-monitor
```

Make the script executable:

```bash
chmod +x System_monitor.sh
```

Run the monitoring script:

```bash
./System_monitor.sh
```

## Validation and Testing

The script has been checked using:

- **Bash syntax validation:** `bash -n System_monitor.sh`
- **Static analysis:** ShellCheck
- **Functional testing:** Verified normal execution.
- **Failure handling:** Simulated an unavailable `free` utility and verified that the script displayed a fallback message while continuing the remaining checks.

## Project Structure

```text
01-System-health-monitor/
├── README.md
└── System_monitor.sh
```

## Future Improvements

- Add CPU and memory threshold monitoring.
- Introduce structured logging.
- Add automated shell script tests.
- Integrate the project into a GitHub Actions CI/CD pipeline.

## Author

Puneeth Kumar

**Part of the Linux Engineering Lab portfolio.**
