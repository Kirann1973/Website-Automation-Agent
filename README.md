# Intelligent Website Automation Agent

An asynchronous, modular website automation agent built in Python using the Playwright framework. This project demonstrates a decoupled tool calling architecture, structured logging, configuration management, and resilient element detection algorithms designed to automate dynamic, modern web frontends (e.g., Shadcn UI).

## Objectives
- **Decoupled Architecture**: Abstract low-level browser commands into clean, asynchronous, reusable tool APIs.
- **Robust Selection Heuristics**: Dynamically target and fill form elements on pages containing modern, randomly generated styling frameworks (dynamic classes, CSS modules) by leveraging ARIA labels, relationships, and attributes.
- **Fail-Safe Orchestration**: Ensure complete browser context tear-down and logging output persistence upon encountering run-time errors or network exceptions.

---

## Folder Structure

```text
Website-Automation-Agent/
├── .env                  # Local environment configuration file (ignored by Git)
├── config.py             # Parses environment parameters and configures loggers
├── tools.py              # Modular browser interaction tools (Playwright Async API)
├── agent.py              # Core orchestration and intelligent element resolver script
├── verify_agent.py       # Sandbox verification script
├── test_page.html        # Local HTML layout used for tool verification
├── automation.log        # Formatted execution logs (persisted output)
└── screenshots/          # Viewport snapshots captured during automation runs
    ├── test_verification.png
    └── shadcn_form_success.png
```

---

## Prerequisites

Ensure you have Python 3.8+ installed on your system.

### Install Package Dependencies
Install the required packages (`playwright` and `python-dotenv`):
```bash
pip install playwright python-dotenv
```

### Install Playwright Browser Binaries
Deploy the required browser engine components (specifically Chromium):
```bash
playwright install chromium
```

---

## Configuration

The agent reads configuration from environment variables or a local `.env` file. You can customize the settings by creating a `.env` file in the root directory:

```env
# Toggle headless mode (True or False)
BROWSER_HEADLESS=False

# Default timeout in milliseconds (e.g. 30000 = 30 seconds)
DEFAULT_TIMEOUT=30000

# Directory to save captured screenshots
SCREENSHOT_DIR=screenshots

# Path to output execution logs
LOG_FILE=automation.log
```

---

## Running the Agent

To execute the intelligent agent workflow, which navigates to the Shadcn documentation, dynamically identifies the react-hook-form fields, inputs data, captures a screenshot, and closes cleanly:

```bash
python3 agent.py
```

### Reviewing Executions
- **Log Outputs**: Check the generated `automation.log` file in the project root directory.
- **Screenshots**: Look inside the `screenshots/` directory for the captured viewport images (e.g., `shadcn_form_success.png`).
