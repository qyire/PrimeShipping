# Prime Shipping File Interface (SFI) Web Application

This web application provides a user interface to interact with shipping data encoded using a prime number-based system (Single Fact Index - SFI).

## Features

*   **Generate Data:** Create sample shipment data with SFI encoding.
*   **Filter Data:** Filter the generated SFI data based on shipment attributes (origin, destination, carrier, status).
*   **Decode Data:** Convert an SFI numeric vector back into human-readable shipment details.
*   **View Prime Map:** See the prime numbers assigned to each attribute value.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the Flask development server:**
    ```bash
    python3 app.py
    ```

2.  **Open your web browser** and navigate to `http://127.0.0.1:5000` (or the address provided by Flask).

## How it Works

The web application (`app.py`) acts as a frontend. User actions trigger calls to a backend command-line script (`sfi_cli.py`) which performs the core SFI operations:

*   `sfi_cli.py generate`: Creates `shipments.json` with SFI-encoded data.
*   `sfi_cli.py filter --criteria '{...}'`: Reads `shipments.json` and filters based on the provided JSON criteria.
*   `sfi_cli.py decode --vector <number>`: Decodes the given SFI vector.
*   `sfi_cli.py primes`: Outputs the prime number mapping.

The Flask app uses Python's `subprocess` module to run these commands and display the results in the web interface. 