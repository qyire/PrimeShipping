#!/usr/bin/env python3

import argparse
import json
import random
import sys
import math
import time
import os

# --- Constants ---
SHIPMENTS_FILE = "shipments.json"
LOG_FILE = "sfi_cli.log" # Added basic logging

# --- Logging Setup ---
def log_message(message):
    """Appends a timestamped message to the log file."""
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Error writing to log file {LOG_FILE}: {e}", file=sys.stderr)

# --- Prime Number Generation ---
def get_primes(count):
    """Generates a list of the first 'count' prime numbers."""
    primes = []
    num = 2
    while len(primes) < count:
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
        num += 1
    return primes

# --- SFI Core Data ---
ATTRIBUTE_GROUPS = {
    "origin": ["New York", "Los Angeles", "Chicago", "Houston", "Miami"],
    "destination": ["London", "Tokyo", "Paris", "Sydney", "Berlin"],
    "carrier": ["PrimeShip", "SwiftLog", "GlobalEx", "CargoFast"],
    "status": ["Pending", "In Transit", "Delivered", "Delayed", "Customs Hold"],
    "priority": ["Standard", "Express", "Overnight"]
}

# --- Prime Map Generation ---
def generate_prime_map():
    """Assigns unique prime numbers to each attribute value."""
    prime_map = {}
    reverse_prime_map = {}
    total_values = sum(len(values) for values in ATTRIBUTE_GROUPS.values())
    primes = get_primes(total_values)
    prime_idx = 0

    for group, values in ATTRIBUTE_GROUPS.items():
        prime_map[group] = {}
        for value in values:
            prime = primes[prime_idx]
            prime_map[group][value] = prime
            reverse_prime_map[prime] = {"group": group, "value": value}
            prime_idx += 1

    return prime_map, reverse_prime_map

PRIME_MAP, REVERSE_PRIME_MAP = generate_prime_map()

# --- SFI Encoding ---
def encode_shipment(shipment_details):
    """Encodes shipment details into an SFI vector (product of primes)."""
    sfi_vector = 1
    try:
        for group, value in shipment_details.items():
            if group in PRIME_MAP and value in PRIME_MAP[group]:
                sfi_vector *= PRIME_MAP[group][value]
            else:
                # Handle unknown attribute/value gracefully if needed, or raise error
                log_message(f"Warning: Unknown attribute/value during encoding: {group}={value}")
                pass # Or assign a default prime, or raise error
    except Exception as e:
        log_message(f"Error during encoding shipment {shipment_details}: {e}")
        return None # Indicate encoding failure
    return sfi_vector

# --- SFI Decoding ---
def decode_sfi_vector(sfi_vector):
    """Decodes an SFI vector back into human-readable attributes."""
    if not isinstance(sfi_vector, int) or sfi_vector <= 0:
        return {"error": "Invalid SFI vector provided. Must be a positive integer."}

    decoded_attributes = {}
    temp_vector = sfi_vector

    # Iterate through primes in reverse map (efficiency might depend on map size vs vector size)
    # A more robust approach for large vectors might involve trial division with known primes.
    sorted_primes = sorted(REVERSE_PRIME_MAP.keys())

    for prime in sorted_primes:
        if temp_vector % prime == 0:
            attribute_info = REVERSE_PRIME_MAP[prime]
            decoded_attributes[attribute_info["group"]] = attribute_info["value"]
            # Keep dividing by the prime factor until it's no longer divisible
            while temp_vector % prime == 0:
                 temp_vector //= prime
            if temp_vector == 1:
                 break # All factors found

    if temp_vector != 1:
        # This indicates the vector had factors not in our prime map
        # or was not formed correctly.
        decoded_attributes["warning"] = f"Vector {sfi_vector} contains unrecognized factors or is incomplete. Remainder: {temp_vector}"
        log_message(f"Decoding warning for vector {sfi_vector}: Remainder {temp_vector}")


    # Ensure all attribute groups are present, filling missing ones with 'Unknown'
    for group in ATTRIBUTE_GROUPS.keys():
        if group not in decoded_attributes:
            decoded_attributes[group] = "Unknown"


    return decoded_attributes

# --- Data Generation ---
def generate_shipment_data(count=100):
    """Generates a specified number of random shipments and their SFI vectors."""
    shipments = []
    log_message(f"Starting generation of {count} shipments.")
    start_time = time.time()
    for i in range(count):
        shipment_id = f"SHP{random.randint(10000, 99999):05d}{i:03d}"
        details = {
            group: random.choice(values)
            for group, values in ATTRIBUTE_GROUPS.items()
        }
        sfi_vector = encode_shipment(details)
        if sfi_vector is not None:
            shipments.append({
                "id": shipment_id,
                "sfi_vector": sfi_vector,
                # Optionally include details for easier debugging/verification
                # "details": details
            })
        else:
             log_message(f"Failed to encode shipment {i+1}, skipping.")

    try:
        with open(SHIPMENTS_FILE, "w") as f:
            json.dump(shipments, f, indent=2)
        end_time = time.time()
        duration = end_time - start_time
        log_message(f"Successfully generated {len(shipments)} shipments to {SHIPMENTS_FILE}. Took {duration:.2f}s.")
        return {"success": True, "count": len(shipments), "file": SHIPMENTS_FILE, "duration_seconds": duration}
    except IOError as e:
        log_message(f"Error writing shipments to {SHIPMENTS_FILE}: {e}")
        return {"success": False, "error": f"Could not write to {SHIPMENTS_FILE}: {e}"}
    except Exception as e:
        log_message(f"An unexpected error occurred during shipment generation: {e}")
        return {"success": False, "error": f"An unexpected error occurred: {e}"}


# --- Data Filtering ---
def filter_shipment_data(criteria_json):
    """Filters shipments from SHIPMENTS_FILE based on SFI criteria."""
    log_message(f"Starting filtering with criteria: {criteria_json}")
    start_time = time.time()

    if not os.path.exists(SHIPMENTS_FILE):
        log_message(f"Error: Shipments file '{SHIPMENTS_FILE}' not found for filtering.")
        return {"success": False, "error": f"Shipments file '{SHIPMENTS_FILE}' not found. Please generate data first."}

    try:
        criteria = json.loads(criteria_json)
    except json.JSONDecodeError as e:
        log_message(f"Error decoding filter criteria JSON: {e}")
        return {"success": False, "error": f"Invalid JSON in filter criteria: {e}"}

    filter_vector = 1
    valid_criteria = {}
    for group, value in criteria.items():
        if group in PRIME_MAP and value in PRIME_MAP[group]:
            prime = PRIME_MAP[group][value]
            filter_vector *= prime
            valid_criteria[group] = value
        else:
            log_message(f"Warning: Invalid filter criterion ignored: {group}={value}")
            # Optionally return an error if strict criteria matching is needed

    if filter_vector == 1 and valid_criteria:
         log_message("Filter vector is 1, but valid criteria were provided. This shouldn't happen.")
         # This case might indicate an issue, or just criteria that map to non-existent primes (which shouldn't happen with current setup)
         return {"success": False, "error": "Internal error creating filter vector from valid criteria."}
    elif filter_vector == 1:
        log_message("No valid filter criteria provided.")
        return {"success": False, "error": "No valid filter criteria provided."}


    log_message(f"Calculated filter vector: {filter_vector} for criteria: {valid_criteria}")

    matching_shipments = []
    try:
        with open(SHIPMENTS_FILE, "r") as f:
            all_shipments = json.load(f)

        for shipment in all_shipments:
            if "sfi_vector" in shipment and isinstance(shipment["sfi_vector"], int):
                 # The core SFI filtering logic: check divisibility
                 if shipment["sfi_vector"] % filter_vector == 0:
                     matching_shipments.append(shipment)
            else:
                log_message(f"Warning: Skipping shipment with missing or invalid 'sfi_vector': {shipment.get('id', 'Unknown ID')}")


        end_time = time.time()
        duration = end_time - start_time
        log_message(f"Filtering complete. Found {len(matching_shipments)} matching shipments out of {len(all_shipments)}. Took {duration:.2f}s.")
        return {
            "success": True,
            "criteria_used": valid_criteria,
            "filter_vector": filter_vector,
            "total_checked": len(all_shipments),
            "matches_found": len(matching_shipments),
            "results": matching_shipments, # Return matching shipment objects (id + sfi_vector)
            "duration_seconds": duration
        }
    except IOError as e:
        log_message(f"Error reading shipments from {SHIPMENTS_FILE}: {e}")
        return {"success": False, "error": f"Could not read {SHIPMENTS_FILE}: {e}"}
    except json.JSONDecodeError as e:
        log_message(f"Error parsing JSON from {SHIPMENTS_FILE}: {e}")
        return {"success": False, "error": f"Invalid JSON in {SHIPMENTS_FILE}: {e}"}
    except Exception as e:
        log_message(f"An unexpected error occurred during filtering: {e}")
        return {"success": False, "error": f"An unexpected error occurred during filtering: {e}"}


# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="SFI CLI - Manage and process SFI encoded shipment data.")
    subparsers = parser.add_subparsers(dest="command", required=True, help='Available commands')

    # Primes command
    parser_primes = subparsers.add_parser("primes", help="Show the prime number mapping for attributes.")

    # Generate command
    parser_generate = subparsers.add_parser("generate", help="Generate sample shipment data.")
    parser_generate.add_argument("-c", "--count", type=int, default=100, help="Number of shipments to generate.")

    # Filter command
    parser_filter = subparsers.add_parser("filter", help="Filter shipments based on criteria.")
    parser_filter.add_argument("-cr", "--criteria", type=str, required=True, help='JSON string of filter criteria (e.g., '{"origin": "New York", "status": "In Transit"}')')

    # Decode command
    parser_decode = subparsers.add_parser("decode", help="Decode an SFI vector.")
    parser_decode.add_argument("-v", "--vector", type=int, required=True, help="The SFI numeric vector to decode.")

    args = parser.parse_args()

    result = {}
    log_message(f"Command '{args.command}' initiated with args: {vars(args)}")

    try:
        if args.command == "primes":
            # Prepare prime map for clean JSON output
            output_map = {"attributes": ATTRIBUTE_GROUPS, "prime_map": PRIME_MAP}
            result = {"success": True, "data": output_map}
        elif args.command == "generate":
            result = generate_shipment_data(args.count)
        elif args.command == "filter":
            result = filter_shipment_data(args.criteria)
        elif args.command == "decode":
            decoded_data = decode_sfi_vector(args.vector)
            if "error" in decoded_data:
                 result = {"success": False, "error": decoded_data["error"], "vector": args.vector}
            else:
                 result = {"success": True, "vector": args.vector, "decoded": decoded_data}
        else:
             # Should not happen because subparsers are required
             result = {"success": False, "error": f"Unknown command: {args.command}"}
             log_message(f"Error: Unknown command '{args.command}' encountered.")

    except Exception as e:
        # Catch-all for unexpected errors during command execution
        error_msg = f"An unexpected error occurred executing command '{args.command}': {e}"
        log_message(f"FATAL ERROR: {error_msg}")
        result = {"success": False, "error": error_msg}
        # Optionally print to stderr as well for immediate visibility if stdout is captured
        print(f"Error: {error_msg}", file=sys.stderr)
        # Exit with a non-zero status code to indicate failure to the caller (Flask)
        sys.exit(1) # Important for subprocess error checking


    # Print result as JSON to stdout for Flask app
    print(json.dumps(result, indent=2)) # Use indent for easier debugging if run manually
    log_message(f"Command '{args.command}' finished. Success: {result.get('success', False)}")

if __name__ == "__main__":
    main()