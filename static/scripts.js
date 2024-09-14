function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.target.classList.add('highlight');
}

function unhighlight(e) {
    e.target.classList.remove('highlight');
}

function handleDrop(e, inputElement, fileNameElement) {
    const dt = e.dataTransfer;
    const files = dt.files;
    inputElement.files = files; // Assign dropped files to input element
    displayFileName(files[0], fileNameElement); // Display file name
    validateForm(); // Validate form on file drop
}

function displayFileName(file, fileNameElement) {
    fileNameElement.textContent = `Uploaded: ${file.name}`;
}

function setupDropArea(dropAreaId, inputElementId, fileNameElementId) {
    const dropArea = document.getElementById(dropAreaId);
    const inputElement = document.getElementById(inputElementId);
    const fileNameElement = document.getElementById(fileNameElementId);

    dropArea.addEventListener('dragenter', highlight, false);
    dropArea.addEventListener('dragover', highlight, false);
    dropArea.addEventListener('dragleave', unhighlight, false);
    dropArea.addEventListener('drop', (e) => {
        preventDefaults(e);
        unhighlight(e);
        handleDrop(e, inputElement, fileNameElement);
    }, false);

    dropArea.addEventListener('click', () => inputElement.click());

    inputElement.addEventListener('change', (e) => {
        const files = e.target.files;
        displayFileName(files[0], fileNameElement); // Display file name on selection
        validateForm(); // Validate form on file selection
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
}

function validateForm() {
    const player1File = document.getElementById('win').files.length > 0;
    const player2File = document.getElementById('loss').files.length > 0;
    const analyzeButton = document.getElementById('analyze-button');
    const errorMessage = document.getElementById('error-message');

    if (player1File && player2File) {
        analyzeButton.disabled = false;
        analyzeButton.style.opacity = 1;
        errorMessage.textContent = ''; // Clear error message
    } else {
        analyzeButton.disabled = true;
        analyzeButton.style.opacity = 0.5;
        errorMessage.textContent = 'Please upload both win and loss files.'; // Show error message
    }
}

// Setup drop areas for both the win and loss PGN files
setupDropArea('drop-area-win', 'win', 'file-name-win');
setupDropArea('drop-area-loss', 'loss', 'file-name-loss');
