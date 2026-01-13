// State management
let pdfText = '';
let workflowRunning = false;
let statusCheckInterval = null;

// DOM elements
const uploadZone = document.getElementById('upload-zone');
const pdfInput = document.getElementById('pdf-input');
const fileInfo = document.getElementById('file-info');
const filename = document.getElementById('filename');
const removeFileBtn = document.getElementById('remove-file');
const contextSection = document.getElementById('context-section');
const actionSection = document.getElementById('action-section');
const resultsSection = document.getElementById('results-section');
const contextText = document.getElementById('context-text');
const charCount = document.getElementById('char-count');
const startWorkflowBtn = document.getElementById('start-workflow');
const progressSection = document.getElementById('progress-section');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultsContent = document.getElementById('results-content');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const startNewBtn = document.getElementById('start-new');
const numPostsSelect = document.getElementById('num-posts');
const linkedinUrlsInput = document.getElementById('linkedin-urls');
const xUrlsInput = document.getElementById('x-urls');
const xSearchInput = document.getElementById('x-search');
const downloadPdfBtn = document.getElementById('download-pdf');

// Utility functions
function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    setTimeout(() => {
        errorSection.style.display = 'none';
    }, 5000);
}

function updateCharCount() {
    const count = contextText.value.length;
    charCount.textContent = count.toLocaleString();
}

function resetUI() {
    pdfText = '';
    workflowRunning = false;
    fileInfo.style.display = 'none';
    contextSection.style.display = 'none';
    actionSection.style.display = 'none';
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
    contextText.value = '';
    updateCharCount();
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// Drag and drop handlers
uploadZone.addEventListener('click', () => {
    pdfInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

pdfInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetUI();
    pdfInput.value = '';
});

// File handling
async function handleFile(file) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please upload a PDF file');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return;
    }

    // Show loading state
    uploadZone.style.opacity = '0.6';
    uploadZone.style.pointerEvents = 'none';

    // Create FormData and upload
    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Store the extracted text
            pdfText = data.text;
            
            // Update UI
            filename.textContent = data.filename;
            fileInfo.style.display = 'block';
            contextText.value = pdfText;
            updateCharCount();
            
            // Show next sections
            contextSection.style.display = 'block';
            actionSection.style.display = 'block';
            
            // Smooth scroll to context section
            setTimeout(() => {
                contextSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        } else {
            showError(data.error || 'Failed to process PDF');
            resetUI();
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        resetUI();
    } finally {
        uploadZone.style.opacity = '1';
        uploadZone.style.pointerEvents = 'auto';
    }
}

// Context text area handler
contextText.addEventListener('input', updateCharCount);

// Start workflow
startWorkflowBtn.addEventListener('click', async () => {
    const context = contextText.value.trim();
    
    if (!context) {
        showError('Context cannot be empty');
        return;
    }

    if (workflowRunning) {
        showError('Workflow is already running');
        return;
    }

    // Parse LinkedIn URLs
    const linkedinUrls = linkedinUrlsInput.value
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);

    // Parse X URLs
    const xUrls = xUrlsInput.value
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);

    // Parse X search terms
    const xSearchTerms = xSearchInput.value
        .split(',')
        .map(term => term.trim())
        .filter(term => term.length > 0);

    // Disable button and show progress
    startWorkflowBtn.disabled = true;
    progressSection.style.display = 'block';
    progressFill.style.width = '10%';
    progressText.textContent = 'Starting workflow...';

    try {
        const response = await fetch('/start_workflow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                context: context,
                num_posts: parseInt(numPostsSelect.value),
                linkedin_urls: linkedinUrls.length > 0 ? linkedinUrls : null,
                x_urls: xUrls.length > 0 ? xUrls : null,
                x_search_terms: xSearchTerms.length > 0 ? xSearchTerms : null
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            workflowRunning = true;
            progressFill.style.width = '30%';
            
            // Start polling for status
            startStatusPolling();
        } else {
            showError(data.error || 'Failed to start workflow');
            startWorkflowBtn.disabled = false;
            progressSection.style.display = 'none';
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        startWorkflowBtn.disabled = false;
        progressSection.style.display = 'none';
    }
});

// Status polling
function startStatusPolling() {
    // Poll every 2 seconds
    statusCheckInterval = setInterval(checkStatus, 2000);
    checkStatus(); // Check immediately
}

async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        // Update progress text
        if (data.progress) {
            progressText.textContent = data.progress;
        }

        // Update progress bar based on status
        if (data.running) {
            // Animate progress bar
            const currentWidth = parseFloat(progressFill.style.width) || 30;
            const newWidth = Math.min(currentWidth + 5, 90);
            progressFill.style.width = newWidth + '%';
        } else {
            // Workflow completed or errored
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
            workflowRunning = false;

            if (data.error) {
                // Show error
                showError(data.error);
                progressFill.style.width = '0%';
                progressSection.style.display = 'none';
                startWorkflowBtn.disabled = false;
            } else if (data.output) {
                // Show results
                progressFill.style.width = '100%';
                progressText.textContent = 'Complete!';
                
                setTimeout(() => {
                    resultsContent.textContent = data.output;
                    resultsSection.style.display = 'block';
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 500);
            }
        }
    } catch (error) {
        console.error('Status check error:', error);
        // Don't show error to user for polling failures
    }
}

// Start new workflow
startNewBtn.addEventListener('click', () => {
    resetUI();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    pdfInput.value = '';
    linkedinUrlsInput.value = '';
    xUrlsInput.value = '';
    xSearchInput.value = '';
});

// Download PDF
downloadPdfBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/download_pdf');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'thought_leadership_posts.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to generate PDF');
        }
    } catch (error) {
        showError('Download error: ' + error.message);
    }
});

// Initialize
updateCharCount();

