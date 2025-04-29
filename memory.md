# SFI Web Application - Implementation Log

**Date:** $(date +%Y-%m-%d)

## Initial Setup & Architecture

*   **Decision:** Adopted a Flask frontend + Python CLI backend architecture as specified in the PRD.
    *   **Rationale:** Meets the requirement of demonstrating the SFI concept via a web interface while leveraging an existing or easily implementable CLI for the core logic. Allows separation of concerns between UI and SFI processing.
    *   **Rejected:** Direct integration of SFI logic into Flask (`app.py`). While possible, using a separate CLI script adheres closer to the PRD's description and potentially allows the CLI to be used independently.
*   **Decision:** Use `subprocess` module in Flask to call `sfi_cli.py`.
    *   **Rationale:** Standard Python library for process execution, suitable for invoking the CLI backend.
*   **Decision:** CLI (`sfi_cli.py`) will communicate results back to Flask by printing JSON strings to standard output.
    *   **Rationale:** Simple, robust method for inter-process communication. JSON is easily parseable by Python.
*   **Decision:** Generated shipment data will be stored temporarily in `shipments.json`.
    *   **Rationale:** Simple file-based storage for this demonstration application. Meets the PRD requirement (no persistent DB needed for v1.0). The file acts as a shared resource between `generate` and `filter` commands.
    *   **Edge Case:** Concurrent access to `shipments.json` is not handled, but unlikely to be an issue in this single-user, local-run context.
*   **Decision:** Implemented `project.md` and `memory.md` for documentation.
    *   **Rationale:** User request to maintain technical documentation and decision logs alongside the codebase.

## `sfi_cli.py` Implementation Notes (Initial)

*   *(To be added as implementation progresses)* 