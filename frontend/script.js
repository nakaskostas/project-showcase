
document.getElementById('presentation-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const folderPath = document.getElementById('folder-path').value;
    const statusMessage = document.getElementById('status-message');

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
            statusMessage.textContent = `Successfully started processing for: ${result.folder_path}`;
            statusMessage.style.color = 'green';
        } else {
            const error = await response.json();
            statusMessage.textContent = `Error: ${error.error}`;
            statusMessage.style.color = 'red';
        }
    } catch (error) {
        statusMessage.textContent = 'An unexpected error occurred. Please check the console.';
        statusMessage.style.color = 'red';
        console.error('Error:', error);
    }
});
