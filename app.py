import os
import subprocess
import json
import secrets
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='flask_app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# --- Configuration ---
# Use environment variable or generate a random key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))
# Path to the backend CLI script
SFI_CLI_PATH = os.path.join(os.path.dirname(__file__), "sfi_cli.py")
# Python interpreter to use
PYTHON_EXECUTABLE = "python3" # Or specify absolute path if needed

# --- Helper Function to Run CLI ---
def run_cli_command(command_args):
    """Runs a command in the sfi_cli.py script and returns parsed JSON output."""
    full_command = [PYTHON_EXECUTABLE, SFI_CLI_PATH] + command_args
    app.logger.info(f"Executing CLI command: {' '.join(full_command)}")
    try:
        # Increased timeout to 60 seconds for potentially long operations like large generations/filters
        process = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=False, # Don't raise exception on non-zero exit code, handle it manually
            timeout=60
        )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if stderr:
            app.logger.error(f"CLI Error Output: {stderr}")

        if process.returncode != 0:
            app.logger.error(f"CLI command failed with exit code {process.returncode}")
            # Try to parse stdout for JSON error message from CLI, otherwise use stderr
            try:
                cli_result = json.loads(stdout)
                if isinstance(cli_result, dict) and not cli_result.get('success', True):
                    return cli_result # Return the error structure from CLI
            except json.JSONDecodeError:
                 pass # Ignore if stdout isn't valid JSON
            # Fallback error message
            return {"success": False, "error": f"CLI script failed. Error: {stderr or 'Unknown error'}", "details": stdout}

        # Try parsing the JSON output from stdout
        try:
            result = json.loads(stdout)
            app.logger.info(f"CLI command successful. Result: {result}")
            return result
        except json.JSONDecodeError as e:
            app.logger.error(f"Failed to decode JSON from CLI output: {e}")
            app.logger.error(f"CLI stdout was: {stdout}")
            return {"success": False, "error": "Failed to parse response from backend script.", "details": stdout}

    except subprocess.TimeoutExpired:
        app.logger.error(f"CLI command timed out: {' '.join(full_command)}")
        return {"success": False, "error": "Operation timed out."}
    except FileNotFoundError:
        app.logger.error(f"Error: {PYTHON_EXECUTABLE} or {SFI_CLI_PATH} not found.")
        return {"success": False, "error": f"Backend script or Python interpreter not found."}
    except Exception as e:
        app.logger.exception(f"An unexpected error occurred running CLI command: {e}")
        return {"success": False, "error": f"An internal server error occurred: {e}"}

# --- Flask Routes ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    app.logger.info("Rendering index page.")
    return render_template('index.html')

@app.route('/primes', methods=['GET'])
def get_primes_map():
    """Endpoint to get the prime map from the CLI."""
    app.logger.info("Received request for /primes")
    result = run_cli_command(["primes"])
    return jsonify(result)

@app.route('/generate', methods=['POST'])
def generate_data():
    """Endpoint to trigger data generation via the CLI."""
    app.logger.info("Received request for /generate")
    count = request.form.get('count', '100') # Get count from form data
    if not count.isdigit() or int(count) <= 0:
        app.logger.warning(f"Invalid count received for generation: {count}")
        return jsonify({"success": False, "error": "Invalid count specified. Must be a positive integer."}), 400

    result = run_cli_command(["generate", "--count", count])
    return jsonify(result)

@app.route('/filter', methods=['POST'])
def filter_data():
    """Endpoint to trigger data filtering via the CLI."""
    app.logger.info("Received request for /filter")
    criteria_json = request.form.get('criteria')
    if not criteria_json:
        app.logger.warning("Filter request received with no criteria.")
        return jsonify({"success": False, "error": "No filter criteria provided."}), 400

    # Basic validation: Check if it's likely JSON
    try:
        json.loads(criteria_json) # Test if it parses
    except json.JSONDecodeError:
        app.logger.warning(f"Invalid JSON received for filter criteria: {criteria_json}")
        return jsonify({"success": False, "error": "Invalid JSON format for criteria."}), 400

    result = run_cli_command(["filter", "--criteria", criteria_json])
    return jsonify(result)

@app.route('/decode', methods=['POST'])
def decode_vector():
    """Endpoint to trigger SFI vector decoding via the CLI."""
    app.logger.info("Received request for /decode")
    vector_str = request.form.get('vector')
    if not vector_str:
        app.logger.warning("Decode request received with no vector.")
        return jsonify({"success": False, "error": "No SFI vector provided."}), 400

    if not vector_str.isdigit() or int(vector_str) <= 0:
        app.logger.warning(f"Invalid vector received for decoding: {vector_str}")
        return jsonify({"success": False, "error": "Invalid vector specified. Must be a positive integer."}), 400

    result = run_cli_command(["decode", "--vector", vector_str])
    return jsonify(result)

# --- Main Execution Guard ---
if __name__ == '__main__':
    app.logger.info("Starting Flask development server.")
    # Use host='0.0.0.0' to make it accessible on the network if needed
    # Debug=True is useful for development, but should be False in production
    app.run(debug=True, host='0.0.0.0') 