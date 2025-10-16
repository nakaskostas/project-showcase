
document.getElementById('presentation-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const folderPath = document.getElementById('folder-path').value;
    const statusMessage = document.getElementById('status-message');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');
    const submitButton = this.querySelector('button[type="submit"]');

    // Reset UI
    statusMessage.textContent = '';
    resultContainer.innerHTML = '';
    loadingSpinner.style.display = 'block';
    submitButton.disabled = true;
    statusMessage.textContent = 'Processing... Please wait.';
    statusMessage.style.color = '#005a9e';

    try {
        const response = await fetch('/create-presentation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ folder_path: folderPath })
        });

        if (response.ok) {
            const result = await response.json();
            if (result.presentation_url) {
                statusMessage.textContent = 'Presentation generated successfully!';
                statusMessage.style.color = 'green';

                const viewButton = document.createElement('a');
                viewButton.href = result.presentation_url;
                viewButton.textContent = 'View Presentation';
                viewButton.className = 'result-button';
                viewButton.target = '_blank'; // Open in new tab
                resultContainer.appendChild(viewButton);

            } else {
                statusMessage.textContent = `An issue occurred: ${result.status || 'Unknown status'}`;
                statusMessage.style.color = 'orange';
            }
        } else {
            const error = await response.json();
            statusMessage.textContent = `Error: ${error.error}`;
            statusMessage.style.color = 'red';
        }
    } catch (error) {
        statusMessage.textContent = 'An unexpected error occurred. Please check the console.';
        statusMessage.style.color = 'red';
        console.error('Error:', error);
    } finally {
        loadingSpinner.style.display = 'none';
        submitButton.disabled = false;
    }
});
