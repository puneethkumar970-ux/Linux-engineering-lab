from fastapi import FastAPI
import platform
import subprocess
import psutil
import re
import time
import os
import requests
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Infrastructure Incident Platform is running"
    }


@app.get("/health")
def health_check():
    return {
        "Status": "Healthy",
        "Service": "Infrastructure-Incident-Platform" 
    }

@app.get("/system")
def system_info():
    return {
        "Operating_system": platform.system(),
	"Hostname": platform.node(),
	"Architecture": platform.machine(),
	"Python_version": platform.python_version()
    }

@app.get("/system/cpu")
def cpu_info():
    return {
        "CPU_usage_percent": psutil.cpu_percent(interval=2)
    }

def evaluate_cpu(cpu_usage):
    if cpu_usage >= 90:
        return "CRITICAL"
    elif cpu_usage >= 75:
        return "WARNING"
    else:
        return "HEALTHY"

@app.get("/health/cpu")
def cpu_health():
    cpu_usage = psutil.cpu_percent(interval=2)
    status = evaluate_cpu(cpu_usage)

    return {
        "CPU_usage_percent": cpu_usage,
        "Status": status
    }

@app.get("/system/memory")
def memory_info():
    memory = psutil.virtual_memory()
    return {
	"Total_GB": round(memory.total / (1024 ** 3), 2),
	"Used_GB": round(memory.used / (1024 ** 3), 2),
	"Available_GB": round(memory.available / (1024 ** 3), 2),
	"Usage_percent": memory.percent
    }

def evaluate_memory(memory_usage):
    if memory_usage >= 90:
        return "CRITICAL"
    elif memory_usage >= 75:
        return "WARNING"
    else:
        return "HEALTHY"

@app.get("/health/memory")
def memory_health():
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    status = evaluate_memory(memory_usage)

    return {
        "Memory_usage_percent": memory_usage,
        "Status": status
    }


@app.get("/system/disk")
def disk_info():
    disk = psutil.disk_usage("/")
    return {
	"Total_GB": round(disk.total / (1024 ** 3), 2),
	"Used_GB": round(disk.used / (1024 ** 3), 2),
	"Free_GB": round(disk.free / (1024 ** 3), 2),
	"Usage_percent": disk.percent
    }

def evaluate_disk(disk_usage):
    if disk_usage >= 90:
        return "CRITICAL"
    elif disk_usage >= 75:
        return "WARNING"
    else:
        return "HEALTHY"

@app.get("/health/disk")
def disk_health():
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    status = evaluate_disk(disk_usage)
    return {
        "Disk_usage_percent": disk_usage,
        "Status": status
    }

@app.get("/system/processes")
def process_info():
    process_list = []

    for process in psutil.process_iter():
        try:
            process_list.append({
                "PID": process.pid,
                "Name": process.name(),
                "CPU_percent": process.cpu_percent(interval=0.1),
                "Memory_percent": process.memory_percent()
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    process_list = sorted(
	process_list,
        key=lambda process: process["CPU_percent"],
        reverse=True
    )
    memory_processes = sorted(
        process_list,
        key=lambda process: process["Memory_percent"],
        reverse=True
    )
    return {
	"Process_count": len(process_list),
	"Top_CPU_processes": process_list[:5],
        "Top_Memory_processes":memory_processes[:5]
    }

def evaluate_process_cpu(cpu_percent):
    if cpu_percent >= 90:
        return "CRITICAL"
    elif cpu_percent >= 75:
        return "WARNING"
    else:
        return "HEALTHY"

@app.get("/health/processes")
def process_health():
    process_list = []

    for process in psutil.process_iter():
        try:
            process_list.append({
                "PID": process.pid,
                "Name": process.name(),
                "CPU_percent": process.cpu_percent(interval=0.1)
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    process_list = sorted(
        process_list,
        key=lambda process: process["CPU_percent"],
        reverse=True
    )

    top_processes = process_list[:5]

    for process in top_processes:
        process["Status"] = evaluate_process_cpu(
            process["CPU_percent"]
        )

    return {
        "Top_CPU_processes": top_processes
    }

@app.get("/system/network")
def network_info():
    network_list = []

    stats = psutil.net_if_stats()
    traffic = psutil.net_io_counters(pernic=True)

    for interface, details in stats.items():
        network_list.append({
            "Interface": interface,
            "Is_up": details.isup,
	    "Bytes_sent_MB": round(traffic[interface].bytes_sent / (1024 ** 2), 2),
	    "Bytes_received_MB": round(traffic[interface].bytes_recv / (1024 ** 2), 2)
    })

    return {
	"Interfaces": network_list
    }
def evaluate_network(is_up):
    if is_up:
        return "HEALTHY"
    else:
        return "CRITICAL"

@app.get("/health/network")
def network_health():
    network_list = []

    stats = psutil.net_if_stats()

    for interface, details in stats.items():
        status = evaluate_network(details.isup)
        network_list.append({
            "Interface": interface,
            "Is_up": details.isup,
            "Status": status
        })
    return {
        "Interfaces": network_list
    }
@app.get("/system/uptime")
def uptime_info():
    boot_time = psutil.boot_time()
    current_time = time.time()
    uptime_seconds = current_time - boot_time

    return {
        "Boot_time": datetime.fromtimestamp(boot_time).isoformat(),
        "Uptime_seconds": round(uptime_seconds, 2),
        "Uptime_hours": round(uptime_seconds / 3600, 2)
    }

def read_logs(log_file="/var/log/auth.log"):
    with open(log_file, "r") as file:
        lines = file.readlines()
    return lines[-10:]

def read_journal_logs():

    result = subprocess.run(
        ["journalctl", "-n", "100", "--no-pager"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().splitlines()

def read_service_logs(service):

    result = subprocess.run(
        ["journalctl", "-u", service, "-n", "10", "--no-pager"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip().splitlines()

def classify_log(line):

    # Detect journalctl timestamp
    journal_match = re.match(
        r"^(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+([^:]+):\s+(.*)$",
        line
    )

    if journal_match:
        timestamp = journal_match.group(1)
        source = journal_match.group(3).strip()
        message = journal_match.group(4).strip()
    else:
        timestamp_match = re.match(r"^(\S+)", line)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        source = None
        message = line.strip()

    text = message.lower()

    service_match = re.search(
        r"\b[\w@.-]+\.service\b",
        line
    )

    service = service_match.group(0) if service_match else None

    if "critical" in text or "fatal" in text:
        severity = "CRITICAL"
        reason = "Critical system condition detected"

    elif "authentication failure" in text or "failed password" in text:
        severity = "ERROR"
        reason = "Authentication failure detected"

    elif "error" in text or "failed" in text:
        severity = "ERROR"
        reason = "Error or failure detected"

    elif "warning" in text or "warn" in text:
        severity = "WARNING"
        reason = "Warning detected"

    elif "accepted password" in text or "accepted publickey" in text:
        severity = "INFO"
        reason = "Successful authentication detected"

    else:
        severity = "INFO"
        reason = "Normal log entry"

    return {
        "Timestamp": timestamp,
        "Service": service,
        "Message": message,
        "Severity": severity,
        "Reason": reason
    }

def get_incident_key(message):

    text = message.lower()

    recovery_words = [
        "critical",
        "error",
        "warning",
        "info",
        "failed",
        "failure",
        "restored",
        "recovered",
        "successfully",
        "started",
        "active"
    ]

    for word in recovery_words:
        text = text.replace(word, "")

    return " ".join(text.split())

def get_correlation_key(incident):

    message = incident.get("Message", "").lower()
    service = incident.get("Service")

    # WSL / Windows Agent connectivity issue
    if (
        "windows agent" in message
        or "ubuntupro" in message
        or "wsl-pro-service" in message
        or "getaddrinfo() failed" in message
    ):
        return "wsl-windows-agent-connectivity"

    # Service-specific incidents
    if service:
        return service

    # Generic incident fallback
    return get_incident_key(message)


def group_incidents(incidents):

    grouped = {}

    for incident in incidents:

        correlation_key = get_correlation_key(incident)

        if correlation_key not in grouped:

            grouped[correlation_key] = {
                "Correlation_key": correlation_key,
                "Service": incident["Service"],
                "Severity": incident["Severity"],
                "Message": incident["Message"],
                "Reason": incident["Reason"],
                "Occurrences": 1,
                "First_seen": incident["Timestamp"],
                "Last_seen": incident["Timestamp"],
                "Related_events": [
                    incident
                ]
            }

        else:

            grouped[correlation_key]["Occurrences"] += 1

            grouped[correlation_key]["Last_seen"] = (
                incident["Timestamp"]
            )

            grouped[correlation_key]["Related_events"].append(
                incident
            )

            # Preserve the highest severity
            severity_priority = {
                "INFO": 1,
                "WARNING": 2,
                "ERROR": 3,
                "CRITICAL": 4
            }

            current_severity = grouped[correlation_key]["Severity"]
            new_severity = incident["Severity"]

            if (
                severity_priority[new_severity]
                > severity_priority[current_severity]
            ):
                grouped[correlation_key]["Severity"] = new_severity

    return list(grouped.values())

def evaluate_incident_context(incidents):

    if not incidents:
        return "HEALTHY"

    severities = []

    for incident in incidents:
        severities.append(
            incident["Severity"]
        )

    latest_incident = incidents[-1]
    latest_message = latest_incident["Message"].lower()

    # Check whether the latest event indicates recovery
    if (
        "recovered" in latest_message
        or "restored" in latest_message
        or "connection established" in latest_message
        or "connection restored" in latest_message
        or "started successfully" in latest_message
        or "active (running)" in latest_message
    ):
        if (
            "CRITICAL" in severities
            or "ERROR" in severities
            or "WARNING" in severities
        ):
            return "RECOVERED"

    # Determine the highest active severity
    if "CRITICAL" in severities:
        return "CRITICAL"

    elif "ERROR" in severities:
        return "CRITICAL"

    elif "WARNING" in severities:
        return "WARNING"

    return "HEALTHY"


@app.get("/incident/classify")
def classify_incident(log: str):
    return classify_log(log)

@app.get("/incident/logs")
def incident_logs():

    logs = read_logs()
    journal_logs = read_journal_logs()

    all_logs = logs + journal_logs

    incidents = []
    context_events = []

    for line in all_logs:

        result = classify_log(line)
        text = result["Message"].lower()

    # Keep all actual incidents
        if result["Severity"] != "INFO":
            context_events.append(result)

    # Keep only INFO messages that indicate recovery
        elif (
            "recovered" in text
            or "restored" in text
            or "connection established" in text
            or "connection restored" in text
            or "started successfully" in text
            or "active (running)" in text
        ):
            context_events.append(result)

        if result["Severity"] != "INFO":
            incidents.append(result)

    grouped_incidents = group_incidents(incidents)

    for incident in grouped_incidents:

        related_events = []

        incident_key = get_incident_key(
            incident["Message"]
        )

        for event in context_events:

            event_key = get_incident_key(
                event["Message"]
            )

            if (
                event["Service"] == incident["Service"]
                and event_key == incident_key
            ):
                related_events.append(event)

        incident["Context_status"] = evaluate_incident_context(
            related_events
        )

    return {
        "Log_count": len(grouped_incidents),
        "Raw_incident_count": len(incidents),
        "Incidents": grouped_incidents
    }

@app.get("/incident/journal")
def incident_journal():

    logs = read_journal_logs()

    return {
        "Log_count": len(logs),
        "Logs": logs
    }



def classify_service_log(line):

    text = line.lower()

    if (
        "error" in text
        or "failed" in text
        or "failure" in text
        or "can't synchronise" in text
        or "unable to" in text
        or "connection refused" in text
        or "timeout" in text
        or "unreachable" in text
        or "could not step system clock" in text
    ):
        return "CRITICAL"

    elif (
        "warning" in text
        or "warn" in text
        or "forward time jump" in text
        or "clock wrong" in text
    ):
        return "WARNING"

    else:
        return "HEALTHY"

def evaluate_service_log_context(logs):

    statuses = []

    for log in logs:
        statuses.append(
            classify_service_log(log)
        )

    if not statuses:
        return "HEALTHY"

    latest_status = statuses[-1]

    # Explicit recovery messages
    recovery_detected = False

    for log in logs:
        text = log.lower()

        if (
            "selected source" in text
            or "started successfully" in text
            or "active (running)" in text
            or "finished successfully" in text
        ):
            recovery_detected = True

    if latest_status == "CRITICAL":
        return "CRITICAL"

    elif latest_status == "WARNING":
        return "WARNING"

    elif recovery_detected:
        if "CRITICAL" in statuses or "WARNING" in statuses:
            return "RECOVERED"

        return "HEALTHY"

    return "HEALTHY"

def check_service(service):

    active_result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True
    )

    enabled_result = subprocess.run(
        ["systemctl", "is-enabled", service],
        capture_output=True,
        text=True
    )

    logs_result = subprocess.run(
        ["journalctl", "-u", service, "-n", "5", "--no-pager"],
        capture_output=True,
        text=True
    )

    active_status = active_result.stdout.strip()
    enabled_status = enabled_result.stdout.strip()
    service_logs = logs_result.stdout.strip().splitlines()

    if service_logs == ["-- No entries --"]:
        service_logs = []
    service_log_statuses = []

    for log in service_logs:
        service_log_statuses.append(
            classify_service_log(log)
        )
    service_context_status = evaluate_service_log_context(
        service_logs
    )
    return {
        "Service": service,
        "Status": active_status,
        "Enabled": enabled_status,
        "Logs": service_logs,
        "Log_statuses": service_log_statuses,
        "Log_context_status": service_context_status
    }

def evaluate_service(service_status, log_statuses, log_context_status):

    if log_context_status == "CRITICAL":
        return "CRITICAL"

    elif log_context_status == "WARNING":
        return "WARNING"

    elif log_context_status == "RECOVERED":
        return "RECOVERED"

    elif service_status == "active":
        return "HEALTHY"

    else:
        return "CRITICAL"

@app.get("/system/services")
def services_info(service: str = None):

    if service:
        result = check_service(service)

        return {
            "Service": service,
            "Status": result["Status"],
            "Enabled": result["Enabled"],
            "Logs": result["Logs"],
            "Log_statuses": result["Log_statuses"],
            "Log_context_status": result["Log_context_status"]
        }

    result = subprocess.run(
        ["systemctl", "list-unit-files", "--type=service", "--no-pager"],
        capture_output=True,
        text=True
    )

    services = []

    for line in result.stdout.splitlines():

        if ".service" in line:
            service_name = line.split()[0]
            services.append(service_name)

    return {
        "Services": services
    }

@app.get("/health/services")
def services_health(service: str):
    result = check_service(service)

    return {
        "Service": result["Service"],
        "Service_status": result["Status"],
        "Enabled": result["Enabled"],
        "Health_status": evaluate_service(
            result["Status"],
            result["Log_statuses"],
            result["Log_context_status"]
        )
    }

@app.get("/health/overall")
def overall_health(service: str = None):

    cpu_usage = psutil.cpu_percent(interval=2)
    cpu_status = evaluate_cpu(cpu_usage)

    memory = psutil.virtual_memory()
    memory_status = evaluate_memory(memory.percent)

    disk = psutil.disk_usage("/")
    disk_status = evaluate_disk(disk.percent)

    process_list = []

    for process in psutil.process_iter():
        try:
            process_list.append({
                "CPU_percent": process.cpu_percent(interval=0.1)
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    process_list = sorted(
        process_list,
        key=lambda process: process["CPU_percent"],
        reverse=True
    )

    top_processes = process_list[:5]

    process_statuses = []

    for process in top_processes:
        process_statuses.append(
            evaluate_process_cpu(process["CPU_percent"])
        )

    if "CRITICAL" in process_statuses:
       process_status = "CRITICAL"
    elif "WARNING" in process_statuses:
       process_status = "WARNING"
    else:
       process_status = "HEALTHY"

    network_statuses = []

    stats = psutil.net_if_stats()

    for interface, details in stats.items():
        status = evaluate_network(details.isup)
        network_statuses.append(status)

    if "CRITICAL" in network_statuses:
       network_status = "CRITICAL"
    elif "WARNING" in network_statuses:
       network_status = "WARNING"
    else:
       network_status = "HEALTHY"

# Incident health
    logs = read_logs()
    journal_logs = read_journal_logs()

    logs = logs + journal_logs

    detected_incidents = []
    detected_services = set()

    for line in logs:
        result = classify_log(line)
        if result["Severity"] != "INFO":
            detected_incidents.append(result)

            if result["Service"]:
                detected_services.add(result["Service"])
    grouped_detected_incidents = group_incidents(
        detected_incidents
    )
    incident_context_statuses = []

    for incident in grouped_detected_incidents:

        correlation_key = incident["Correlation_key"]
        related_events = []

        for event in logs:

            event_result = classify_log(event)
            event_text = event_result["Message"].lower()

            if (
                event_result["Severity"] != "INFO"
                or "recovered" in event_text
                or "restored" in event_text
                or "connection established" in event_text
                or "connection restored" in event_text
                or "started successfully" in event_text
                or "active (running)" in event_text
            ):

                event_correlation_key = get_correlation_key(
                    event_result
                )

                if event_correlation_key == correlation_key:
                    related_events.append(event_result)

        context_status = evaluate_incident_context(
            related_events
        )

        incident_context_statuses.append(
            context_status
        )
        incident["Context_status"] = context_status
# Service journal detection
    detected_service_statuses = {}
    detected_service_context_statuses = {}

    service_list_result = subprocess.run(
        [
            "systemctl",
            "list-units",
            "--type=service",
            "--state=running",
            "--no-pager"
        ],
        capture_output=True,
        text=True
    )

    running_services = []

    for line in service_list_result.stdout.splitlines():

        if ".service" in line:

            service_name = line.split()[0]

            running_services.append(service_name)


    for service_name in running_services:

        service_result = check_service(service_name)

        service_log_statuses = service_result["Log_statuses"]

        service_context_status = service_result["Log_context_status"]

        if "CRITICAL" in service_log_statuses:

            detected_service_statuses[service_name] = "CRITICAL"

        elif "WARNING" in service_log_statuses:

            detected_service_statuses[service_name] = "WARNING"

        detected_service_context_statuses[service_name] = service_context_status

#Service health
    if not service and len(detected_services) == 1:
        service = next(iter(detected_services))
    if service:
        service_result = check_service(service)
        service_runtime_status = service_result["Status"]
        service_status = evaluate_service(
            service_runtime_status,
            service_result["Log_statuses"],
            service_result["Log_context_status"]
        )
    else:
        service_result = {
            "Service": None,
            "Status": None,
            "Enabled": None,
            "Logs": [],
            "Log_statuses": [],
            "Log_statuses": []
        }
        service_status = "HEALTHY"
        service_runtime_status = None

    if "CRITICAL" in incident_context_statuses:

        incident_status = "CRITICAL"

    elif "WARNING" in incident_context_statuses:

        incident_status = "WARNING"

    else:

        incident_status = "HEALTHY"

    statuses = [
        cpu_status,
        memory_status,
        disk_status,
        service_status,
        network_status,
        process_status,
        incident_status
    ]
# Include automatically detected service conditions
    for detected_status in detected_service_context_statuses.values():

        if detected_status == "CRITICAL":
            statuses.append("CRITICAL")

        elif detected_status == "WARNING":
            statuses.append("WARNING")

    if "CRITICAL" in statuses:
            overall_status = "CRITICAL"
    elif "WARNING" in statuses:
             overall_status = "WARNING"
    else:
        overall_status = "HEALTHY"
    boot_time = psutil.boot_time()
    current_time = time.time()
    uptime_seconds = current_time - boot_time
    uptime_hours = round(uptime_seconds / 3600,2)

    health_data = {
        "Overall_status": overall_status,
        "CPU_usage_percent": cpu_usage,
        "CPU_status": cpu_status,
        "Memory_usage_percent": memory.percent,
        "Memory_status": memory_status,
        "Disk_usage_percent": disk.percent,
        "Disk_status": disk_status,
        "Process_status": process_status,
        "Top_CPU_processes": top_processes,
        "Network_status": network_status,
        "Uptime_hours": uptime_hours,
        "Service": service,
        "Service_status": service_status,
        "Service_runtime_status": service_runtime_status,
        "Service_enabled": service_result["Enabled"],
        "Service_logs": service_result["Logs"],
        "Detected_services": list(detected_services),
        "Detected_service_statuses": detected_service_statuses,
        "Detected_service_context_statuses": detected_service_context_statuses,
        "Incident_status": incident_status,
        "Detected_incidents": grouped_detected_incidents,
        "Incident_context_statuses": incident_context_statuses
    }

    return health_data

@app.get("/diagnostics")
def diagnostics(service: str = None):

    health_data = overall_health(service)

    diagnoses = diagnose_health(health_data)

    for diagnosis in diagnoses:
        diagnosis["Root_cause"] = analyze_root_cause(diagnosis, health_data)

    return {
        "Overall_status": health_data["Overall_status"],
        "Diagnoses": diagnoses
    }

def diagnose_health(health_data):

    diagnoses = []

    if health_data["CPU_status"] != "HEALTHY":

        if health_data["CPU_usage_percent"] >= 90:
            diagnosis = {
                "Component": "CPU",
                "Severity": "CRITICAL",
                "Diagnosis": "CPU utilization is critically high",
                "Recommended_action": "Identify the processes consuming the most CPU and investigate the workload"
            }

        else:
            diagnosis = {
                "Component": "CPU",
                "Severity": "WARNING",
                "Diagnosis": "CPU utilization is elevated",
                "Recommended_action": "Monitor CPU usage and investigate the top CPU-consuming processes"
            }

        diagnosis["Evidence"] = {
            "CPU_usage_percent": health_data["CPU_usage_percent"]
        }

        diagnoses.append(diagnosis)

    if health_data["Memory_status"] != "HEALTHY":
        if health_data["Memory_usage_percent"] >= 90:
            diagnosis = {
                "Component": "Memory",
                "Severity": "CRITICAL",
                "Diagnosis": "Memory utilization is critically high",
                "Recommended_action": "Identify processes consuming the most memory and investigate for excessive memory usage"
            }

        else:
            diagnosis = {
                "Component": "Memory",
                "Severity": "WARNING",
                "Diagnosis": "Memory utilization is elevated",
                "Recommended_action": "Monitor memory usage and investigate the top memory-consuming processes"
            }

        diagnosis["Evidence"] = {
            "Memory_usage_percent": health_data["Memory_usage_percent"]
        }

        diagnoses.append(diagnosis)

    if health_data["Disk_status"] != "HEALTHY":
        if health_data["Disk_usage_percent"] >= 90:
            diagnosis = {
                "Component": "Disk",
                "Severity": "CRITICAL",
                "Diagnosis": "Disk utilization is critically high",
                "Recommended_action": "Identify large files or directories and free disk space immediately"
            }

        else:
            diagnosis = {
                "Component": "Disk",
                "Severity": "WARNING",
                "Diagnosis": "Disk utilization is elevated",
                "Recommended_action": "Monitor disk usage and identify files or directories consuming significant space"
            }

        diagnosis["Evidence"] = {
            "Disk_usage_percent": health_data["Disk_usage_percent"]
        }

        diagnoses.append(diagnosis)

    if health_data["Process_status"] != "HEALTHY":
        if health_data["Process_status"] == "CRITICAL":
            diagnosis = {
                "Component": "Processes",
                "Severity": "CRITICAL",
                "Diagnosis": "One or more processes are consuming critically high CPU",
                "Recommended_action": "Identify the highest CPU-consuming process and investigate whether it is causing excessive system load"
            }

        else:
            diagnosis = {
                "Component": "Processes",
                "Severity": "WARNING",
                "Diagnosis": "One or more processes are consuming elevated CPU",
                "Recommended_action": "Monitor the highest CPU-consuming processes and investigate unusual resource usage"
            }

        diagnosis["Evidence"] = {
            "Top_CPU_processes": health_data["Top_CPU_processes"]
        }

        diagnoses.append(diagnosis)

    if health_data["Network_status"] != "HEALTHY":
        if health_data["Network_status"] == "CRITICAL":
            diagnosis = {
                "Component": "Network",
                "Severity": "CRITICAL",
                "Diagnosis": "One or more network interfaces are down",
                "Recommended_action": "Identify the affected network interface and investigate its connectivity or configuration"
            }

        else:
            diagnosis = {
                "Component": "Network",
                "Severity": "WARNING",
                "Diagnosis": "Network connectivity requires monitoring",
                "Recommended_action": "Monitor network interfaces and investigate any unstable or unavailable interfaces"
            }

        diagnosis["Evidence"] = {
            "Network_status": health_data["Network_status"]
        }

        diagnoses.append(diagnosis)

    if health_data["Service_status"] != "HEALTHY":

        if health_data["Service_status"] == "CRITICAL":

            if health_data["Service_runtime_status"] == "active":
                diagnosis = {
                    "Component": "Service",
                    "Severity": "CRITICAL",
                    "Diagnosis": "The monitored service is active but recent service logs indicate a critical condition",
                    "Recommended_action": "Review the recent service logs and investigate the critical condition affecting the service"
                }

            else:
                diagnosis = {
                    "Component": "Service",
                    "Severity": "CRITICAL",
                    "Diagnosis": "The monitored service is not active",
                    "Recommended_action": "Check the service status and review the recent service logs to investigate why the service is not running"
                }

        else:
            diagnosis = {
                "Component": "Service",
                "Severity": "WARNING",
                "Diagnosis": "The monitored service is active but recent service logs indicate warning conditions",
                "Recommended_action": "Review the recent service logs and investigate the warning conditions affecting the service"
            }

        diagnosis["Evidence"] = {
            "Service": health_data["Service"],
            "Service_status": health_data["Service_status"],
            "Service_runtime_status": health_data["Service_runtime_status"],
            "Service_enabled": health_data["Service_enabled"],
            "Service_logs": health_data["Service_logs"]
        }

        diagnoses.append(diagnosis)

# Automatically detected service conditions
    detected_service_context_statuses = health_data["Detected_service_context_statuses"]

    for detected_service, detected_status in detected_service_context_statuses.items():

        if detected_status == "CRITICAL":

            diagnoses.append({
                "Component": "Service",
                "Severity": "CRITICAL",
                "Diagnosis": (
                    f"An active critical condition was detected for "
                    f"{detected_service}"
                ),
                "Recommended_action": (
                    f"Review the recent journal logs for {detected_service} "
                    f"and investigate the active critical condition"
                ),
                "Evidence": {
                    "Service": detected_service,
                    "Context_status": detected_status,
                    "Recent_log_statuses": health_data["Detected_service_statuses"].get(
                        detected_service
                    ),
                    "Logs": read_service_logs(detected_service)
                }
            })

        elif detected_status == "WARNING":

            diagnoses.append({
                "Component": "Service",
                "Severity": "WARNING",
                "Diagnosis": (
                    f"An active warning condition was detected for "
                    f"{detected_service}"
                ),
                "Recommended_action": (
                    f"Review the recent journal logs for {detected_service} "
                    f"and investigate the warning condition"
                ),
                "Evidence": {
                    "Service": detected_service,
                    "Context_status": detected_status,
                    "Recent_log_statuses": health_data["Detected_service_statuses"].get(
                        detected_service
                    ),
                    "Logs": read_service_logs(detected_service)
                }
            })

    if health_data["Incident_status"] != "HEALTHY":

        if health_data["Incident_status"] == "CRITICAL":
            diagnosis = {
                "Component": "Incidents",
                "Severity": "CRITICAL",
                "Diagnosis": "Critical or error-level log events were detected",
                "Recommended_action": (
                    "Review the detected log events and investigate the affected "
                    "component using the available incident evidence"
                )
            }

        else:
            diagnosis = {
                "Component": "Incidents",
                "Severity": "WARNING",
                "Diagnosis": "Warning-level log events were detected",
                "Recommended_action": (
                    "Review the warning log events and monitor the affected component"
                )
            }

        diagnosis["Evidence"] = {
            "Incident_status": health_data["Incident_status"],
            "Detected_incidents": health_data["Detected_incidents"],
            "Detected_services": health_data["Detected_services"]
        }

        diagnoses.append(diagnosis)

    return diagnoses

def analyze_incident_evidence(incident):

    message = incident.get("Message", "").lower()

    if "authentication failure" in message:
        return {
            "Evidence_type": "Authentication",
            "Finding": "Authentication failure detected in system logs"
        }

    elif "failed password" in message:
        return {
            "Evidence_type": "Authentication",
            "Finding": "A failed password authentication attempt was detected"
        }

    elif "connection refused" in message:
        return {
            "Evidence_type": "Connectivity",
            "Finding": "A connection attempt was refused"
        }

    elif "connection timeout" in message or "timeout" in message:
        return {
            "Evidence_type": "Connectivity",
            "Finding": "A connection attempt timed out"
        }

    elif "connection failed" in message:
        return {
            "Evidence_type": "Connectivity",
            "Finding": "A connection attempt failed"
        }

    elif "report already exists" in message:
        return {
            "Evidence_type": "Application",
            "Finding": "The application reported that a report already exists for the requested period"
        }

    elif (
        "windows agent" in message
        and "no such file or directory" in message
    ):
        return {
            "Evidence_type": "WSL / Windows Agent",
            "Finding": (
                "WSL could not connect to the Windows Agent because "
                "the agent address file was not found"
            )
        }

    elif "could not connect" in message:
        return {
            "Evidence_type": "Connectivity",
            "Finding": (
                "The system could not establish a connection "
                "to the required component"
            )
        }

    elif "getaddrinfo() failed" in message:
        return {
            "Evidence_type": "Network",
            "Finding": "Hostname or address resolution failed"
        }

    elif "no such file or directory" in message:
        return {
            "Evidence_type": "File or Configuration",
            "Finding": "A required file or path could not be found"
        }

    else:
        return {
            "Evidence_type": "Unknown",
            "Finding": "The incident message contains an error or warning that requires further investigation"
        }



def analyze_root_cause(diagnosis, health_data):

    component = diagnosis["Component"]
    evidence = diagnosis["Evidence"]

    # CPU root cause analysis
    if component == "CPU":

        cpu_usage = evidence["CPU_usage_percent"]

        if cpu_usage >= 90:
            return (
                "High CPU utilization may be caused by a "
                "resource-intensive process"
            )

        else:
            return (
                "CPU utilization is elevated and should be monitored"
            )

    # Memory root cause analysis
    elif component == "Memory":

        memory_usage = evidence["Memory_usage_percent"]

        if memory_usage >= 90:
            return (
                "High memory utilization may be caused by one or more "
                "memory-intensive processes"
            )

        else:
            return (
                "Memory utilization is elevated and should be monitored"
            )

    # Disk root cause analysis
    elif component == "Disk":

        disk_usage = evidence["Disk_usage_percent"]

        if disk_usage >= 90:
            return (
                "High disk utilization may be caused by large files, "
                "logs, or insufficient available storage"
            )

        else:
            return (
                "Disk utilization is elevated and should be monitored"
            )

    # Incident root cause analysis
    elif component == "Incidents":

        incidents = evidence["Detected_incidents"]

        if not incidents:
            return (
                "An incident was detected but additional log analysis "
                "is required"
            )

        # Find currently active critical incidents
        active_critical_incidents = []

        for incident in incidents:

            if incident.get("Context_status") == "CRITICAL":
                active_critical_incidents.append(incident)

        # Analyze an active critical incident first
        if active_critical_incidents:

            incident = active_critical_incidents[0]

            incident_evidence = analyze_incident_evidence(
                incident
            )

            return (
                f"{incident_evidence['Finding']}. "
                f"Occurrences: {incident['Occurrences']}. "
                f"First seen: {incident['First_seen']}. "
                f"Last seen: {incident['Last_seen']}."
            )

        # If there is no active critical incident,
        # look for an active warning condition
        active_warning_incidents = []

        for incident in incidents:

            if incident.get("Context_status") == "WARNING":
                active_warning_incidents.append(incident)

        if active_warning_incidents:

            incident = active_warning_incidents[0]

            incident_evidence = analyze_incident_evidence(
                incident
            )

            return (
                f"{incident_evidence['Finding']}. "
                f"Occurrences: {incident['Occurrences']}. "
                f"First seen: {incident['First_seen']}. "
                f"Last seen: {incident['Last_seen']}."
            )

        # If incidents exist but all are recovered
        recovered_incidents = []

        for incident in incidents:

            if incident.get("Context_status") == "RECOVERED":
                recovered_incidents.append(incident)

        if recovered_incidents:

            incident = recovered_incidents[0]

            incident_evidence = analyze_incident_evidence(
                incident
            )

            return (
                f"{incident_evidence['Finding']}. "
                "The incident has recovered and does not "
                "currently indicate an active failure. "
                f"Occurrences: {incident['Occurrences']}. "
                f"First seen: {incident['First_seen']}. "
                f"Last seen: {incident['Last_seen']}."
            )

        return (
            "An incident was detected but additional log analysis "
            "is required"
        )

    # Service root cause analysis
    elif component == "Service":

        # Automatically detected service condition
        if "Context_status" in evidence:

            context_status = evidence["Context_status"]
            service_name = evidence.get("Service")

            if context_status == "CRITICAL":

                return (
                    f"Recent journal logs for {service_name} "
                    "contain an active critical condition"
                )

            elif context_status == "WARNING":

                return (
                    f"Recent journal logs for {service_name} "
                    "contain an active warning condition"
                )

            elif context_status == "RECOVERED":

                return (
                    f"Recent journal logs for {service_name} "
                    "indicate that a previous condition has recovered"
                )

            elif context_status == "HEALTHY":

                return (
                    f"Recent journal logs for {service_name} "
                    "do not indicate an active critical or warning "
                    "condition"
                )

        # Manually monitored service condition
        service_status = evidence.get("Service_status")
        service_enabled = evidence.get("Service_enabled")
        service_logs = evidence.get("Service_logs", [])

        log_statuses = []

        for log in service_logs:

            log_statuses.append(
                classify_service_log(log)
            )

        if service_status != "active":

            if service_enabled == "disabled":

                return (
                    "The service is not running and is configured "
                    "as disabled"
                )

            elif service_enabled == "enabled":

                if service_logs:

                    return (
                        "The service is not running even though it is "
                        "configured to start automatically; recent "
                        "service logs are available for investigation"
                    )

                return (
                    "The service is not running even though it is "
                    "configured to start automatically"
                )

            else:

                return (
                    "The service is not running and its startup "
                    "configuration requires investigation"
                )

        if "CRITICAL" in log_statuses:

            return (
                "The service is active, but recent service logs "
                "contain critical conditions that require investigation"
            )

        elif "WARNING" in log_statuses:

            return (
                "The service is active, but recent service logs "
                "contain warning conditions that require investigation"
            )

        return (
            "The service is active and recent service logs do not "
            "contain known warning or critical conditions"
        )

    # Unknown diagnostic component
    return (
        "The component was identified, but additional root cause "
        "analysis is required"
    )
def prepare_ai_analysis(incident):

    evidence = analyze_incident_evidence(incident)

    return {
        "Incident": incident.get("Correlation_key"),
        "Service": incident.get("Service"),
        "Severity": incident.get("Severity"),
        "Context_status": incident.get("Context_status"),

        "Evidence": {
            "Evidence_type": evidence["Evidence_type"],
            "Finding": evidence["Finding"]
        },

        "Occurrences": incident.get("Occurrences"),
        "First_seen": incident.get("First_seen"),
        "Last_seen": incident.get("Last_seen"),

        "Related_events": incident.get(
            "Related_events",
            []
        )
    }

@app.get("/ai/analyze")
def ai_analyze():

    health_data = overall_health()

    diagnoses = diagnose_health(
        health_data
    )

    for diagnosis in diagnoses:

        diagnosis["Root_cause"] = analyze_root_cause(
            diagnosis,
            health_data
        )

    if not diagnoses:

        return {
            "AI_status": "OLLAMA",
            "Analysis": {
                "Summary": "No health issues or incidents were detected.",
                "Evidence": {}
            }
        }

    analyses = []

    for diagnosis in diagnoses:

        if diagnosis["Component"] == "Incidents":

            incidents = diagnosis["Evidence"].get(
                "Detected_incidents",
                []
            )

            if not incidents:
                continue

            incident = incidents[0]

            ai_input = prepare_ai_analysis(
                incident
            )

            ai_response = call_ollama_ai(
                ai_input
            )

            analyses.append({
                "Component": "Incidents",
                "Deterministic_root_cause": diagnosis[
                    "Root_cause"
                ],
                "AI_analysis": ai_response,
                "Evidence": {
                    "Incident": ai_input["Incident"],
                    "Severity": ai_input["Severity"],
                    "Context_status": ai_input["Context_status"],
                    "Evidence": ai_input["Evidence"],
                    "Occurrences": ai_input["Occurrences"],
                    "First_seen": ai_input["First_seen"],
                    "Last_seen": ai_input["Last_seen"]
                }
            })

        elif diagnosis["Component"] == "Service":

            evidence = diagnosis["Evidence"]

            if "Context_status" in evidence:

                ai_input = {
                    "Incident": evidence.get(
                        "Service"
                    ),
                    "Service": evidence.get(
                        "Service"
                    ),
                    "Severity": evidence.get(
                        "Context_status"
                    ),
                    "Context_status": evidence.get(
                        "Context_status"
                    ),
                    "Evidence": {
                        "Evidence_type": "Service",
                        "Finding": (
                            f"Service {evidence.get('Service')} "
                            f"has a detected "
                            f"{evidence.get('Context_status')} condition."
                        )
                    },
                    "Occurrences": None,
                    "First_seen": None,
                    "Last_seen": None
                }

            else:

                ai_input = {
                    "Incident": evidence.get(
                        "Service"
                    ),
                    "Service": evidence.get(
                        "Service"
                    ),
                    "Severity": diagnosis.get(
                        "Severity"
                    ),
                    "Context_status": diagnosis.get(
                        "Severity"
                    ),
                    "Evidence": {
                        "Evidence_type": "Service",
                        "Finding": (
                            f"Service {evidence.get('Service')} "
                            f"status is "
                            f"{evidence.get('Service_runtime_status')}."
                        )
                    },
                    "Occurrences": None,
                    "First_seen": None,
                    "Last_seen": None
                }

            ai_response = call_ollama_ai(
                ai_input
            )

            analyses.append({
                "Component": "Service",
                "Deterministic_root_cause": diagnosis[
                    "Root_cause"
                ],
                "AI_analysis": ai_response,
                "Evidence": ai_input["Evidence"]
            })

        else:

            analyses.append({
                "Component": diagnosis["Component"],
                "Deterministic_root_cause": diagnosis[
                    "Root_cause"
                ],
                "AI_analysis": (
                    f"The deterministic health engine identified "
                    f"a {diagnosis['Component']} condition. "
                    f"Further AI analysis is not yet enabled "
                    f"for this component."
                ),
                "Evidence": diagnosis["Evidence"]
            })

    return {
        "AI_status": "OLLAMA",
        "Analysis": analyses
    }


def call_ollama_ai(ai_input):

    ollama_base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    ollama_url = f"{ollama_base_url}/api/generate"

    prompt = f"""
You are an infrastructure incident response assistant.

Analyze the incident using ONLY the evidence explicitly supplied below.

INCIDENT DATA

Incident: {ai_input["Incident"]}
Service: {ai_input["Service"]}
Severity: {ai_input["Severity"]}
Context: {ai_input["Context_status"]}

Evidence type: {ai_input["Evidence"]["Evidence_type"]}
Evidence finding: {ai_input["Evidence"]["Finding"]}

Occurrences: {ai_input["Occurrences"]}
First seen: {ai_input["First_seen"]}
Last seen: {ai_input["Last_seen"]}

STRICT EVIDENCE RULES

1. The supplied incident data is the ONLY source of truth.

2. Do not introduce any fact, component, service, file, dependency,
   server, device, configuration, permission, port, protocol,
   environment, infrastructure element, or operational condition
   that is not explicitly present in the supplied incident data.

3. Do not use general technical knowledge to create incident-specific
   facts.

4. A technical term appearing in an error message does NOT prove the
   existence, state, health, configuration, or behavior of another
   component.

5. Do not infer a root cause from a symptom.

6. Only describe a root cause as confirmed when the supplied evidence
   explicitly proves it.

7. If the root cause is not explicitly established, write exactly:
   "Root cause not confirmed."

8. Possible explanations may be mentioned only when clearly labelled:
   "Possible explanation:"
   They must never be presented as confirmed facts.

9. Preserve timestamps exactly as supplied. Do not add dates or years.

10. Do not infer production, development, test, staging, or any other
    environment unless explicitly stated.

11. Do not infer business impact or service criticality unless
    explicitly stated.

12. Do not explain the purpose or behavior of a file, service,
    component, or configuration unless that information appears
    explicitly in the supplied evidence.

DIAGNOSTIC RULES

13. Every diagnostic check must examine ONLY something explicitly
    identified in the supplied incident data.

14. Do not introduce a new diagnostic target.

15. Do not recommend checking DNS, firewalls, ports, dependencies,
    configuration files, permissions, network devices, servers,
    processes, updates, patches, or other components unless that
    exact item is explicitly identified in the supplied evidence.

16. If the evidence identifies a file, you may recommend checking
    whether that exact file exists or can be read, but do not assume
    anything about its permissions, contents, ownership, or purpose.

17. If the evidence identifies a service, you may recommend checking
    the status or logs of that exact service.

18. If the evidence identifies a specific log message, you may
    recommend reviewing that exact log message or collecting additional
    occurrences of the same message.

19. Do not claim that a diagnostic check has been performed.

20. A diagnostic check is a proposed action, not a result.

21. Never write a diagnostic check followed by a fabricated result.

22. Never state that something is reachable, configured correctly,
    functioning correctly, healthy, unhealthy, verified, confirmed,
    or working unless the supplied evidence explicitly establishes it.

23. Do not convert timestamps, occurrence counts, or error messages
    into conclusions that are not directly supported.

24. Prefer safe, read-only diagnostic checks.

REMEDIATION RULES

25. Diagnosis must come before remediation.

26. If the root cause is not confirmed, write exactly:
    "Additional diagnosis is required before remediation."

27. Do not recommend restarting, stopping, starting, creating,
    deleting, reinstalling, replacing, modifying, or reconfiguring
    anything unless the supplied evidence explicitly establishes
    sufficient justification.

28. Do not claim that remediation has been performed.

RESPONSE FORMAT

1. Incident Summary

State only what the supplied evidence directly establishes.

2. Evidence Analysis

List only confirmed facts from the supplied evidence.

3. Likely Cause

If the cause is not explicitly established, write:

"Root cause not confirmed."

If mentioning a possible explanation, clearly label it:

"Possible explanation:"

4. Potential Impact

Describe only impacts directly supported by the evidence.

If impact cannot be established, write:

"Impact not confirmed from the supplied evidence."

5. Step-by-Step Diagnosis

Provide 3 to 5 ordered diagnostic checks.

Every check must reference an exact item explicitly present in the
supplied evidence.

Do not introduce new components or assumptions.

Do not include a result after a proposed diagnostic check.

6. Step-by-Step Remediation

If the root cause is not confirmed, write:

"Additional diagnosis is required before remediation."

7. Verification

Describe only evidence-based verification.

Do not claim that verification has already occurred.

8. Safety / Rollback Considerations

If no system change is justified, write:

"No system change is justified from the supplied evidence."

Do not add additional sections.
"""

    response = requests.post(
        ollama_url,
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 400,
                "temperature": 0.2
            }
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]

