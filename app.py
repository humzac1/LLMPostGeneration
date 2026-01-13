#!/usr/bin/env python3
"""
Flask Web Application for Thought Leadership Workflow
Provides a drag-and-drop PDF interface to trigger the workflow
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pypdf import PdfReader
import io
import threading
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT

# Import the workflow components
from agents.orchestrator_agent import OrchestratorAgent
from scrapers.linkedin_scraper import scrape_and_format_for_workflow as scrape_linkedin
from scrapers.x_scraper import scrape_and_format_for_workflow as scrape_x
import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store workflow status
workflow_status = {
    'running': False,
    'progress': '',
    'output': '',
    'full_output': '',  # Complete output with summary for download
    'error': None
}


def filter_summary_from_output(output_text):
    """
    Remove the validation summary section from the output for UI display
    Keep only the actual posts
    """
    lines = output_text.split('\n')
    filtered_lines = []
    skip_section = False
    
    for line in lines:
        # Skip validation summary section
        if '🔍 VALIDATION SUMMARY' in line:
            skip_section = True
            continue
        
        # Resume after validation section (look for next major section)
        if skip_section and ('💼 LINKEDIN POSTS' in line or '🐦 X (TWITTER) POSTS' in line):
            skip_section = False
        
        if not skip_section:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file
    
    Args:
        pdf_file: File object from Flask request
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                # Clean up the text: replace multiple newlines with single space
                # and preserve paragraph breaks (double newlines)
                cleaned_text = page_text.replace('\n', ' ')
                # Remove multiple spaces
                cleaned_text = ' '.join(cleaned_text.split())
                
                if text:  # Add spacing between pages
                    text += "\n\n"
                text += cleaned_text
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
            
        return text.strip()
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def run_workflow_async(context, num_posts=3, linkedin_urls=None, x_urls=None, x_search_terms=None):
    """
    Run the complete workflow in a separate thread
    """
    global workflow_status
    
    try:
        workflow_status['running'] = True
        workflow_status['error'] = None
        workflow_status['output'] = ''
        workflow_status['full_output'] = ''  # Store complete output with summary
        
        # Validate API keys
        workflow_status['progress'] = 'Validating API keys...'
        
        if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
            raise Exception("OPENAI_API_KEY not configured!")
        
        if not config.APIFY_API_TOKEN or config.APIFY_API_TOKEN == "your_apify_api_token_here":
            raise Exception("APIFY_API_TOKEN not configured!")
        
        # Step 1: Scrape LinkedIn
        workflow_status['progress'] = 'Scraping LinkedIn posts...'
        
        # Use custom URLs from user input
        # If no URLs provided, skip scraping and use fallback examples
        if linkedin_urls and len(linkedin_urls) > 0:
            try:
                linkedin_examples = scrape_linkedin(
                    urls=linkedin_urls,
                    limit_per_source=5
                )
            except Exception as e:
                print(f"LinkedIn scraping failed: {str(e)}")
                linkedin_examples = """
                LinkedIn Example:
                "Customer expectations have never been higher. 
                In 2024, 73% of customers expect immediate responses.
                This is where AI-powered automation becomes essential.
                #CustomerService #AI"
                """
        else:
            # No URLs provided - use generic example
            linkedin_examples = """
            LinkedIn Example:
            "Customer expectations have never been higher. 
            In 2024, 73% of customers expect immediate responses.
            This is where AI-powered automation becomes essential.
            #CustomerService #AI"
            """
        
        # Step 2: Scrape X
        workflow_status['progress'] = 'Scraping X posts...'
        
        # Use custom inputs from user
        # If no URLs/terms provided, skip scraping and use fallback examples
        if (x_urls and len(x_urls) > 0) or (x_search_terms and len(x_search_terms) > 0):
            try:
                x_examples = scrape_x(
                    start_urls=x_urls if x_urls and len(x_urls) > 0 else None,
                    search_terms=x_search_terms if x_search_terms and len(x_search_terms) > 0 else None,
                    max_items=20
                )
            except Exception as e:
                print(f"X scraping failed: {str(e)}")
                x_examples = """
                X Example:
                "AI won't replace customer service agents.
                But agents using AI will replace those who don't.
                #CX #AI"
                """
        else:
            # No URLs or search terms provided - use generic example
            x_examples = """
            X Example:
            "AI won't replace customer service agents.
            But agents using AI will replace those who don't.
            #CX #AI"
            """
        
        # Step 3: Combine examples
        workflow_status['progress'] = 'Preparing content generation...'
        examples = linkedin_examples + "\n\n---\n\n" + x_examples
        
        # Step 4: Run multi-agent workflow
        workflow_status['progress'] = 'Generating content with AI agents...'
        
        orchestrator = OrchestratorAgent()
        final_output = orchestrator.execute_workflow(
            context=context.strip(),
            examples=examples.strip(),
            num_posts=num_posts
        )
        
        # Format output
        formatted_output = orchestrator.format_output(final_output)
        
        # Save complete output to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        
        # Filter output for UI (remove summary section)
        ui_output = filter_summary_from_output(formatted_output)
        
        workflow_status['progress'] = 'Complete!'
        workflow_status['output'] = ui_output  # UI gets filtered version
        workflow_status['full_output'] = formatted_output  # Store full version for download
        workflow_status['running'] = False
        
    except Exception as e:
        workflow_status['error'] = str(e)
        workflow_status['running'] = False
        workflow_status['progress'] = 'Error occurred'
        print(f"Workflow error: {str(e)}")
        import traceback
        traceback.print_exc()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Handle PDF upload and extract text
    """
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        return jsonify({
            'success': True,
            'text': text,
            'filename': secure_filename(pdf_file.filename)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/start_workflow', methods=['POST'])
def start_workflow():
    """
    Start the workflow with the provided context and optional custom URLs
    """
    try:
        global workflow_status
        
        if workflow_status['running']:
            return jsonify({'error': 'Workflow is already running'}), 400
        
        data = request.json
        context = data.get('context', '')
        num_posts = data.get('num_posts', 3)
        linkedin_urls = data.get('linkedin_urls')
        x_urls = data.get('x_urls')
        x_search_terms = data.get('x_search_terms')
        
        if not context or not context.strip():
            return jsonify({'error': 'Context cannot be empty'}), 400
        
        # Start workflow in background thread
        thread = threading.Thread(
            target=run_workflow_async,
            args=(context, num_posts, linkedin_urls, x_urls, x_search_terms)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Workflow started successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get the current workflow status
    """
    return jsonify({
        'running': workflow_status['running'],
        'progress': workflow_status['progress'],
        'output': workflow_status['output'],
        'error': workflow_status['error']
    })


@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    """
    Generate and download a PDF of the workflow output
    """
    try:
        global workflow_status
        
        if not workflow_status.get('full_output'):
            return jsonify({'error': 'No output available to download'}), 400
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for flowable objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            fontName='Courier'
        )
        
        # Add title
        title = Paragraph("Thought Leadership Content", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Parse and add content
        output_text = workflow_status['full_output']
        lines = output_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                elements.append(Spacer(1, 0.1*inch))
                continue
            
            # Detect headings
            if any(emoji in line for emoji in ['📊', '📋', '🔍', '💼', '🐦', '✅']):
                # It's a heading
                try:
                    p = Paragraph(line, heading_style)
                    elements.append(p)
                    elements.append(Spacer(1, 0.2*inch))
                except:
                    # Fallback if special characters cause issues
                    elements.append(Spacer(1, 0.1*inch))
            elif line.startswith('=') or line.startswith('-'):
                # Skip separator lines
                elements.append(Spacer(1, 0.05*inch))
            else:
                # Regular content
                try:
                    # Escape special characters for reportlab
                    line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    p = Paragraph(line, normal_style)
                    elements.append(p)
                    elements.append(Spacer(1, 0.05*inch))
                except:
                    # Skip problematic lines
                    continue
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='thought_leadership_posts.pdf'
        )
    
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 THOUGHT LEADERSHIP WORKFLOW - WEB INTERFACE")
    print("="*70)
    print("Starting server on http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

