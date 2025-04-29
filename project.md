# SFI Web Application - Technical Blueprint

**Version:** 1.0

## 1. Core Architecture

The application follows a two-tier architecture:

1.  **Frontend:** A web interface built using Flask, HTML, CSS, and JavaScript. It provides the user interface (UI) and handles user interactions.
2.  **Backend:** A command-line interface (CLI) script (`sfi_cli.py`) written in Python. This script encapsulates the core Single Fact Index (SFI) logic, including prime number assignment, data generation, filtering based on divisibility, and decoding.

**Interaction Model:** The Flask web application (`app.py`) acts as a controller. When a user performs an action (e.g., generate data, filter, decode), the Flask backend executes the appropriate command in `sfi_cli.py` using Python's `subprocess` module. The CLI script performs the requested operation and returns results (typically as JSON strings) via standard output, which Flask then parses and presents to the user in the web interface.

**Data Flow:**
*   User Action (Web UI) -> Flask Route (`app.py`)
*   Flask Route -> `subprocess.run(['python3', 'sfi_cli.py', 'command', '--args'])`
*   `sfi_cli.py` -> Executes logic (e.g., reads/writes `shipments.json`) -> Prints JSON to stdout
*   Flask Route -> Captures stdout -> Processes JSON -> Renders HTML Template
*   HTML Template -> Display Results (Web UI)

## 2. Tech Stack

*   **Backend Language:** Python (3.9.6+)
*   **Web Framework:** Flask (>=2.2.3)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API for AJAX)
*   **Data Format (Internal):** JSON (for communication between Flask and CLI, and for storing generated data in `shipments.json`)
*   **CLI Argument Parsing:** `argparse` (Python standard library)
*   **Process Management:** `subprocess` (Python standard library)

## 3. API Patterns

*   **Web API:** Standard Flask RESTful-like patterns. Specific endpoints (`/`, `/primes`, `/generate`, `/filter`, `/decode`) handle GET/POST requests from the frontend JavaScript. Requests typically trigger backend CLI commands.
*   **CLI API:** `sfi_cli.py` uses command-line arguments (`argparse`) to define its interface:
    *   `primes`: No arguments needed.
    *   `generate [--count N]`: Optional count of shipments.
    *   `filter --criteria 'JSON_STRING'`: Requires a JSON string defining filter criteria.
    *   `decode --vector NUMBER`: Requires the SFI vector to decode.
    *   **Output:** CLI commands output results primarily as JSON strings to standard output for easy parsing by the Flask application. Errors are written to standard error.

## 4. Database Schema Overview

*   **N/A (Version 1.0):** This version does not use a persistent database.
*   **Temporary Data Storage:** Generated shipment data (including SFI vectors) is stored temporarily in a file named `shipments.json` in the project's root directory. This file is overwritten each time the `generate` command is run. 