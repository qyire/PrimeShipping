document.addEventListener('DOMContentLoaded', () => {
    const primeMapDisplay = document.getElementById('prime-map-display');
    const viewPrimesBtn = document.getElementById('view-primes-btn');
    const filterControlsContainer = document.getElementById('filter-controls');
    const filterForm = document.getElementById('filter-form');
    const filterButton = filterForm.querySelector('button[type="submit"]');

    const generateForm = document.getElementById('generate-form');
    const generateOutput = document.getElementById('generate-output');
    const generateStatus = document.getElementById('generate-status');

    const filterOutput = document.getElementById('filter-output');
    const filterStatus = document.getElementById('filter-status');

    const decodeForm = document.getElementById('decode-form');
    const decodeOutput = document.getElementById('decode-output');
    const decodeStatus = document.getElementById('decode-status');

    let primeMapData = null; // Store fetched prime map

    // --- Helper Functions ---
    function showLoading(statusElement) {
        statusElement.textContent = 'Processing...';
        statusElement.className = 'status-indicator';
    }

    function showSuccess(statusElement, message = 'Done.') {
        statusElement.textContent = message;
        statusElement.className = 'status-indicator success-message';
    }

    function showError(statusElement, message = 'Error.') {
        statusElement.textContent = message;
        statusElement.className = 'status-indicator error-message';
    }

    function displayOutput(outputElement, data) {
        outputElement.innerHTML = ''; // Clear previous output
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(data, null, 2);
        outputElement.appendChild(pre);
    }

    function displayErrorOutput(outputElement, errorMessage, details = null) {
        outputElement.innerHTML = ''; // Clear previous output
        const errorP = document.createElement('p');
        errorP.className = 'error-message';
        errorP.textContent = `Error: ${errorMessage}`;
        outputElement.appendChild(errorP);
        if (details) {
            const detailsPre = document.createElement('pre');
            detailsPre.textContent = `Details: ${details}`;
            outputElement.appendChild(detailsPre);
        }
    }

    // --- Prime Map Handling ---
    async function fetchAndDisplayPrimeMap() {
        viewPrimesBtn.disabled = true;
        primeMapDisplay.style.display = 'block';
        primeMapDisplay.innerHTML = 'Loading Prime Map...';
        filterButton.disabled = true; // Disable filter btn while loading

        try {
            const response = await fetch('/primes');
            const result = await response.json();

            if (result.success && result.data) {
                primeMapData = result.data; // Store the data
                displayOutput(primeMapDisplay, primeMapData);
                populateFilterControls(primeMapData.attributes);
                filterButton.disabled = false; // Enable filter button
            } else {
                primeMapDisplay.innerHTML = `<p class="error-message">Error loading prime map: ${result.error || 'Unknown error'}</p>`;
            }
        } catch (error) {
            console.error("Fetch error for primes:", error);
            primeMapDisplay.innerHTML = `<p class="error-message">Failed to fetch prime map from server.</p>`;
        } finally {
            viewPrimesBtn.disabled = false;
        }
    }

    function populateFilterControls(attributeGroups) {
        filterControlsContainer.innerHTML = '<p>Select filter criteria (based on Prime Map):</p>'; // Clear existing

        for (const group in attributeGroups) {
            const values = attributeGroups[group];
            if (values.length > 0) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'filter-group';

                const label = document.createElement('label');
                label.htmlFor = `filter-${group}`;
                label.textContent = `${group.charAt(0).toUpperCase() + group.slice(1)}:`;

                const select = document.createElement('select');
                select.id = `filter-${group}`;
                select.name = group;

                // Add a default "any" option
                const defaultOption = document.createElement('option');
                defaultOption.value = "";
                defaultOption.textContent = "-- Any --";
                select.appendChild(defaultOption);

                // Add options for each value
                values.forEach(value => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = value;
                    select.appendChild(option);
                });

                groupDiv.appendChild(label);
                groupDiv.appendChild(select);
                filterControlsContainer.appendChild(groupDiv);
            }
        }
    }

    // --- Event Listeners ---
    viewPrimesBtn.addEventListener('click', fetchAndDisplayPrimeMap);

    // Generate Data Form Submission
    generateForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        showLoading(generateStatus);
        generateOutput.innerHTML = '';
        generateForm.querySelector('button').disabled = true;

        const formData = new FormData(generateForm);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                showSuccess(generateStatus, `Generated ${result.count} shipments in ${result.duration_seconds.toFixed(2)}s.`);
                displayOutput(generateOutput, { message: "Generation successful", details: result });
            } else {
                showError(generateStatus, result.error || 'Generation failed');
                displayErrorOutput(generateOutput, result.error || 'Unknown error', result.details);
            }
        } catch (error) {
            console.error("Generate fetch error:", error);
            showError(generateStatus, 'Network error or server unreachable.');
            displayErrorOutput(generateOutput, 'Could not communicate with the server.');
        } finally {
            generateForm.querySelector('button').disabled = false;
        }
    });

    // Filter Data Form Submission
    filterForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!primeMapData) {
            showError(filterStatus, "Prime map not loaded yet.");
            return;
        }
        showLoading(filterStatus);
        filterOutput.innerHTML = '';
        filterButton.disabled = true;

        const criteria = {};
        const selects = filterControlsContainer.querySelectorAll('select');
        selects.forEach(select => {
            if (select.value) { // Only include if a value is selected
                criteria[select.name] = select.value;
            }
        });

        if (Object.keys(criteria).length === 0) {
             showError(filterStatus, "Please select at least one filter criterion.");
             filterButton.disabled = false;
             return;
        }

        const formData = new FormData();
        formData.append('criteria', JSON.stringify(criteria));

        try {
            const response = await fetch('/filter', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                showSuccess(filterStatus, `Found ${result.matches_found} matches in ${result.duration_seconds.toFixed(2)}s.`);
                displayOutput(filterOutput, result.results.length > 0 ? result.results : { message: "No matching shipments found." });
            } else {
                showError(filterStatus, result.error || 'Filtering failed');
                displayErrorOutput(filterOutput, result.error || 'Unknown error', result.details);
            }
        } catch (error) {
            console.error("Filter fetch error:", error);
            showError(filterStatus, 'Network error or server unreachable.');
            displayErrorOutput(filterOutput, 'Could not communicate with the server.');
        } finally {
            filterButton.disabled = false;
        }
    });

    // Decode Vector Form Submission
    decodeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        showLoading(decodeStatus);
        decodeOutput.innerHTML = '';
        decodeForm.querySelector('button').disabled = true;

        const formData = new FormData(decodeForm);

        try {
            const response = await fetch('/decode', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                showSuccess(decodeStatus);
                displayOutput(decodeOutput, result.decoded);
            } else {
                showError(decodeStatus, result.error || 'Decoding failed');
                displayErrorOutput(decodeOutput, result.error || 'Unknown error', result.details);
            }
        } catch (error) {
            console.error("Decode fetch error:", error);
            showError(decodeStatus, 'Network error or server unreachable.');
            displayErrorOutput(decodeOutput, 'Could not communicate with the server.');
        } finally {
            decodeForm.querySelector('button').disabled = false;
        }
    });

    // --- Initial Load ---
    fetchAndDisplayPrimeMap(); // Load prime map when the page loads

}); 