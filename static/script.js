document.addEventListener('DOMContentLoaded', function() {
    const serverForm = document.getElementById('server-form');
    const startServersBtn = document.getElementById('start-servers');
    const stopServersBtn = document.getElementById('stop-servers');
    const statusDiv = document.getElementById('status');
    const configFilenameSelect = document.getElementById('config-filename');

    // Fetch TFTP files and populate the dropdown
    fetch('/get_tftp_files')
        .then(response => response.json())
        .then(files => {
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                configFilenameSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching TFTP files:', error);
            statusDiv.textContent = 'Error loading TFTP files. Please try again.';
            statusDiv.className = 'status error';
        });

    startServersBtn.addEventListener('click', function() {
        const formData = new FormData(serverForm);
        fetch('/start_servers', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = data.message;
            statusDiv.className = data.status === 'success' ? 'status' : 'status error';
        })
        .catch(error => {
            console.error('Error:', error);
            statusDiv.textContent = 'An error occurred. Please try again.';
            statusDiv.className = 'status error';
        });
    });

    stopServersBtn.addEventListener('click', function() {
        fetch('/stop_servers', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = data.message;
            statusDiv.className = data.status === 'success' ? 'status' : 'status error';
        })
        .catch(error => {
            console.error('Error:', error);
            statusDiv.textContent = 'An error occurred. Please try again.';
            statusDiv.className = 'status error';
        });
    });
});