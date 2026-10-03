# Infrastructure Incident Platform

A Linux infrastructure monitoring and incident analysis platform built with Python and FastAPI.

The platform combines system health monitoring, service monitoring, log analysis, incident correlation, deterministic diagnostics, and local AI-assisted incident analysis.

## Architecture


CPU ────────┐
Memory ─────┤
Disk ───────┤
Processes ──┤
Network ────┤──> Health Engine ──> Troubleshooting
Services ───┤
Logs ───────┤
Uptime ─────┘
                         │
                         ▼
                    Incidents
                         │
                         ▼
                 Automated Diagnostics
                         │
                         ▼
                    AI Analysis
                         │
                         ▼
                Ollama / Qwen 2.5 3B

## Key Capabilities

* CPU, memory, and disk monitoring
* Process monitoring using `psutil`
* Network health monitoring
* Linux service discovery using `systemd`
* Service status and journal log analysis
* System and journal log classification
* Incident severity classification
* Incident correlation and deduplication
* Detection of active and recovered incidents
* Evidence-based deterministic diagnostics
* Deterministic root-cause analysis
* Local AI-assisted incident analysis using Ollama
* Structured troubleshooting and verification guidance
* Environment-configurable Ollama endpoint

## Technology Stack

* Python
* FastAPI
* Uvicorn
* psutil
* Requests
* Linux
* systemd
* journalctl
* Ollama
* Qwen 2.5 3B

## Incident Analysis Flow


System / Journal Logs
        │
        ▼
   Log Classification
        │
        ▼
 Incident Detection
        │
        ▼
Correlation & Deduplication
        │
        ▼
 Context Evaluation
        │
        ▼
Evidence Extraction
        │
        ▼
Deterministic Diagnosis
        │
        ▼
   AI Analysis


## API Endpoints

### System Monitoring

GET /system
GET /system/cpu
GET /system/memory
GET /system/disk
GET /system/processes
GET /system/network
GET /system/services
GET /system/uptime

### Health:
GET /health
GET /health/cpu
GET /health/memory
GET /health/disk
GET /health/processes
GET /health/network
GET /health/services
GET /health/overall

### Incident Analysis

GET /incident/classify
GET /incident/logs
GET /incident/journal

### Diagnostics

GET /diagnostics

### AI Analysis

GET /ai/analyze

## AI Integration

The platform uses Ollama to run the Qwen 2.5 3B model locally.

The AI layer receives structured incident information including:

* Incident correlation key
* Service
* Severity
* Context status
* Evidence type
* Evidence finding
* Occurrence count
* First-seen timestamp
* Last-seen timestamp

The deterministic layer establishes the observed evidence before AI analysis is performed.

The AI layer is instructed to:

* Use only the supplied evidence
* Distinguish confirmed evidence from possible explanations
* Avoid unsupported root-cause claims
* Avoid inventing infrastructure components or environmental details
* Prefer read-only diagnostic checks
* Avoid unsupported system-changing actions
* State when the root cause is not confirmed
* Provide verification and safety considerations

## Example Incident

The platform detected a repeated WSL / Windows Agent connectivity incident.

The deterministic analysis identified evidence indicating that the Windows Agent address file was not found.

The incident was correlated under:

wsl-windows-agent-connectivity

The platform tracked repeated occurrences and recorded the first and last observed timestamps.

The AI analysis then used the structured evidence to provide:

* Incident summary
* Evidence analysis
* Root-cause assessment
* Potential impact assessment
* Diagnostic checks
* Remediation guidance
* Verification steps
* Safety considerations

The AI does not replace the deterministic monitoring layer. It operates on structured evidence produced by the monitoring, correlation, and diagnostic components.

## Running the Application

Create a Python virtual environment:

python3 -m venv .venv


Activate the virtual environment:


source .venv/bin/activate

Install the project dependencies:


pip install -r requirements.txt


Start the FastAPI application:

uvicorn app.main:app --reload

The API will be available at:


http://127.0.0.1:8000

FastAPI interactive documentation:


http://127.0.0.1:8000/docs

## Ollama Configuration

The application reads the Ollama endpoint from the `OLLAMA_BASE_URL` environment variable.

Example:

export OLLAMA_BASE_URL="http://<ollama-host>:11434"

If the variable is not provided, the application defaults to:

http://localhost:11434

The model used by the project is:

qwen2.5:3b

## Design Principles

### Evidence First

The deterministic monitoring and diagnostic layers establish what the system actually observed before AI analysis is performed.

### Correlation Before Diagnosis

Repeated log entries describing the same underlying issue are grouped before root-cause analysis.

### Context-Aware Incident Status

The platform evaluates incident context so that historical events and recovery-related events can be considered separately from active conditions.

### Deterministic + AI Analysis

Deterministic logic is used for monitoring, classification, correlation, evidence extraction, and root-cause analysis.

AI is then used as an additional analysis and troubleshooting layer.

### Safe Troubleshooting

When evidence is insufficient, the AI is instructed to avoid unsupported system changes and recommend additional diagnosis first.

## Project Structure

03-Infrastructure-incident-platform/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── main.py
│
├── tests/
│   └── __init__.py
│
├── .gitignore
├── README.md
└── requirements.txt

## Future Improvements

* Expand automated test coverage
* Improve multi-service incident correlation
* Add persistent incident storage
* Add incident history and reporting
* Add API authentication and security
* Containerize the application
* Add CI/CD integration
* Add cloud deployment
* Add Kubernetes deployment
* Expand AI analysis for CPU, memory, process, and network incidents
* Improve structured incident reporting
* Add automated incident lifecycle management
