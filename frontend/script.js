document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('presentation-form');
    const folderPathInput = document.getElementById('folder-path');
    const statusMessage = document.getElementById('status-message');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');
    const submitButton = form.querySelector('button[type="submit"]');
    const stopButton = document.getElementById('stop-btn');

    // Function to set the UI to a processing state
    function setProcessingState(isProcessing) {
        if (isProcessing) {
            loadingSpinner.style.display = 'block';
            statusMessage.textContent = 'Η επεξεργασία βρίσκεται σε εξέλιξη... Παρακαλώ περιμένετε.';
            statusMessage.style.color = '#005a9e';
            submitButton.disabled = true;
            folderPathInput.disabled = true;
            stopButton.disabled = false; // Enable the stop button
            resultContainer.innerHTML = '';
        } else {
            loadingSpinner.style.display = 'none';
            submitButton.disabled = false;
            folderPathInput.disabled = false;
            stopButton.disabled = true; // Disable the stop button
        }
    }

    // --- Event Listener for the main form submission ---
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const folderPath = folderPathInput.value;

        setProcessingState(true);

        try {
            const response = await fetch('/create-presentation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_path: folderPath })
            });

            const result = await response.json();

            if (response.ok) {
                if (result.presentation_url) {
                    statusMessage.textContent = 'Η παρουσίαση δημιουργήθηκε με επιτυχία!';
                    statusMessage.style.color = 'green';
                    const viewButton = document.createElement('a');
                    viewButton.href = result.presentation_url;
                    viewButton.textContent = 'Προβολή Παρουσίασης';
                    viewButton.className = 'result-button';
                    viewButton.target = '_blank';
                    resultContainer.appendChild(viewButton);
                } else {
                    statusMessage.textContent = `Η διαδικασία ακυρώθηκε ή απέτυχε: ${result.status || 'Άγνωστη κατάσταση'}`;
                    statusMessage.style.color = 'orange';
                }
            } else {
                statusMessage.textContent = `Σφάλμα: ${result.detail || 'Άγνωστο σφάλμα από τον server.'}`;
                statusMessage.style.color = 'red';
            }
        } catch (error) {
            statusMessage.textContent = 'Προέκυψε ένα μη αναμενόμενο σφάλμα. Ελέγξτε την κονσόλα.';
            statusMessage.style.color = 'red';
            console.error('Error:', error);
        } finally {
            setProcessingState(false);
        }
    });

    // --- Event Listener for the stop button ---
    stopButton.addEventListener('click', async function() {
        this.disabled = true; // Prevent multiple clicks
        statusMessage.textContent = 'Αποστολή σήματος ακύρωσης...';
        statusMessage.style.color = 'orange';

        try {
            const response = await fetch('/stop-process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (response.ok) {
                statusMessage.textContent = result.status;
            } else {
                statusMessage.textContent = `Σφάλμα κατά την προσπάθεια ακύρωσης: ${result.detail}`;
                this.disabled = false; // Re-enable if stop signal failed
            }
        } catch (error) {
            statusMessage.textContent = 'Αποτυχία αποστολής σήματος ακύρωσης.';
            console.error('Stop Error:', error);
            this.disabled = false; // Re-enable if fetch failed
        }
    });
});