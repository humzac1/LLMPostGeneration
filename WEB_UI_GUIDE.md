# Web UI Guide - Thought Leadership Workflow

## Overview
This web interface provides a drag-and-drop system for uploading PDF documents and triggering the thought leadership content generation workflow.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Make sure your `.env` file is configured with:
- `OPENAI_API_KEY` - Your OpenAI API key
- `APIFY_API_TOKEN` - Your Apify API token

### 3. Start the Server
```bash
python app.py
```

The server will start on `http://localhost:5000`

## How to Use

### Step 1: Upload PDF
- Open your browser and navigate to `http://localhost:5000`
- Drag and drop your PDF file onto the upload zone, or click to browse
- The PDF text will be automatically extracted

### Step 2: Review Context
- The extracted text will appear in the text area
- You can edit or modify the text as needed
- Select the number of posts to generate per platform (1-5)

### Step 3: Generate Content
- Click "Start Workflow" to begin the content generation process
- The workflow will:
  1. Scrape LinkedIn posts for style examples
  2. Scrape X (Twitter) posts for style examples
  3. Generate new content using the multi-agent system
  4. Display the results

### Step 4: View Results
- Generated content will be displayed in the results section
- Content is also saved to a timestamped file (e.g., `output_20260112_143022.txt`)
- Click "Start New Workflow" to begin again

## Features

### PDF Text Extraction
- Supports PDFs up to 16MB
- Automatically extracts text from all pages
- Displays character count for context validation

### Real-time Progress Tracking
- Live progress updates during workflow execution
- Visual progress bar
- Status messages for each workflow stage

### Error Handling
- Validates PDF file types and sizes
- Displays clear error messages
- Graceful fallback for scraping failures

### Modern UI
- Beautiful gradient design
- Smooth animations and transitions
- Responsive layout for mobile devices
- Drag-and-drop file upload

## Architecture

### Backend (Flask)
- `app.py` - Main Flask application
  - `/` - Serves the main page
  - `/upload` - Handles PDF upload and text extraction
  - `/start_workflow` - Triggers the content generation workflow
  - `/status` - Returns current workflow status

### Frontend
- `templates/index.html` - Main HTML structure
- `static/css/style.css` - Modern styling and animations
- `static/js/app.js` - Drag-and-drop and AJAX functionality

### PDF Processing
- Uses `pypdf` library for text extraction
- Processes all pages and concatenates text
- Handles corrupted or scanned PDFs gracefully

### Workflow Execution
- Runs in a background thread to prevent blocking
- Polls status every 2 seconds for real-time updates
- Saves output with timestamps

## Troubleshooting

### PDF Upload Fails
- Ensure the file is a valid PDF (not an image or scanned document)
- Check file size is under 16MB
- Try re-saving the PDF if it's corrupted

### Workflow Doesn't Start
- Verify API keys are configured in `.env`
- Check console logs for errors
- Ensure no other workflow is currently running

### No Results Displayed
- Check the browser console for JavaScript errors
- Verify the Flask server is still running
- Check the terminal for Python errors

## Port Configuration

By default, the server runs on port 5000. To change this:

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

## Security Notes

- The server binds to `0.0.0.0` for development
- For production, use a proper WSGI server (gunicorn, uWSGI)
- Add authentication if deploying publicly
- Consider adding CSRF protection for production use

## Original CLI Usage

The original command-line interface is still available:
```bash
python main.py
```

This runs the workflow with the hardcoded context in `main.py`.

