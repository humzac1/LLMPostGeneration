# Thought Leadership Workflow - Multi-Agent Content Generator

An intelligent multi-agent system built with [Agno](https://docs.agno.com/introduction) that generates professional LinkedIn and X (Twitter) posts based on your context and examples.

## 🌟 Features

- **Multi-Agent Architecture**: Master/Orchestrator pattern with specialized sub-agents
- **Parallel Execution**: LinkedIn and X agents run simultaneously for optimal performance
- **Intelligent Validation**: Orchestrator validates content quality and consistency
- **Customizable System Prompts**: Easy-to-modify agent behaviors in `config.py`
- **OpenAI Integration**: Uses OpenAI's GPT models for high-quality content generation
- **Production Ready**: Structured, maintainable codebase with proper error handling

## 🏗️ Architecture

```
Master/Orchestrator Agent
    │
    ├─→ LinkedIn Agent (runs in parallel)
    │   └─→ Generates LinkedIn posts
    │
    └─→ X Agent (runs in parallel)
        └─→ Generates X/Twitter posts
    
    ↓
Validation & Compilation
    │
    └─→ Final Output (LinkedIn posts → X posts)
```

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Apify API token (for scraping social media posts)
- Internet connection

## 🚀 Installation

1. **Clone the repository** (or navigate to the project directory):
```bash
cd ThoughtLeadershipWorkflow
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API keys
# .env file should contain:
# OPENAI_API_KEY=your_actual_api_key_here
# APIFY_API_TOKEN=your_apify_token_here
# OPENAI_MODEL=gpt-4o
```

## 💻 Usage

### 🌐 Web UI (Recommended)

The easiest way to use the workflow is through the web interface:

```bash
# Quick start
./start_web_ui.sh

# Or manually
python app.py
```

Then open your browser to `http://localhost:5000`

**Features:**
- 📄 Drag-and-drop PDF upload
- ✨ Automatic text extraction
- 🎯 Real-time progress tracking
- 📊 Beautiful results display
- 💾 Automatic file saving

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed instructions.

### 🖥️ Command Line

Run the workflow with default settings:

```bash
python main.py
```

### Customizing Input

Edit `main.py` and modify these variables:

```python
context = """
Your context here - describe your business, product, or topic
"""

examples = """
Provide example LinkedIn and X posts that match your desired style
"""

num_posts = 3  # Number of posts to generate per platform
```

### Customizing Agent Behavior

Edit `config.py` to modify system prompts:

- **`ORCHESTRATOR_SYSTEM_PROMPT`**: Controls master agent behavior
- **`LINKEDIN_SYSTEM_PROMPT`**: Controls LinkedIn content generation
- **`X_SYSTEM_PROMPT`**: Controls X/Twitter content generation
- **`VALIDATION_PROMPT_TEMPLATE`**: Controls validation criteria

## 📁 Project Structure

```
ThoughtLeadershipWorkflow/
│
├── agents/
│   ├── __init__.py              # Agent module initialization
│   ├── orchestrator_agent.py    # Master/Orchestrator agent
│   ├── linkedin_agent.py        # LinkedIn content creator
│   └── x_agent.py               # X/Twitter content creator
│
├── scrapers/
│   ├── __init__.py              # Scraper module initialization
│   ├── linkedin_scraper.py      # LinkedIn post scraper
│   └── x_scraper.py             # X/Twitter post scraper
│
├── templates/
│   └── index.html               # Web UI HTML
│
├── static/
│   ├── css/
│   │   └── style.css            # Web UI styles
│   └── js/
│       └── app.js               # Web UI JavaScript
│
├── app.py                       # Flask web server
├── config.py                    # Configuration & system prompts
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── start_web_ui.sh              # Quick start script
├── env.example                  # Environment variables template
├── .env                         # Your actual environment variables (not in git)
├── README.md                    # This file
└── WEB_UI_GUIDE.md              # Web UI documentation
```

## 🎯 How It Works

1. **Input Processing**: The Orchestrator receives context, example posts, and post count
2. **Parallel Execution**: LinkedIn and X agents run simultaneously using ThreadPoolExecutor
3. **Content Generation**: Each agent generates platform-specific posts using OpenAI
4. **Validation**: Orchestrator validates content for quality, consistency, and platform requirements
5. **Output Compilation**: Final output organized with LinkedIn posts first, then X posts
6. **File Export**: Results saved to `output.txt` for easy access

## 🔧 Configuration Options

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-...          # Your OpenAI API key

# Optional
OPENAI_MODEL=gpt-4o            # OpenAI model to use
```

### System Prompts (config.py)

Each agent has a dedicated system prompt that controls its behavior:

- **LinkedIn Agent**: Optimized for professional, 150-300 word posts with hashtags
- **X Agent**: Optimized for concise, <280 character posts with impact
- **Orchestrator**: Coordinates workflow and validates output quality

## 📊 Output Format

The workflow generates:

1. **Console Output**: Real-time progress updates and formatted results
2. **output.txt**: Complete results saved to file
3. **Structured Data**: Organized by platform with metadata and validation summary

Example output structure:
```
📊 FINAL OUTPUT - THOUGHT LEADERSHIP CONTENT
================================================

📋 WORKFLOW METADATA
[Metadata about the workflow execution]

🔍 VALIDATION SUMMARY
[AI-generated quality assessment]

💼 LINKEDIN POSTS
[All LinkedIn posts numbered and formatted]

🐦 X (TWITTER) POSTS
[All X posts numbered and formatted]

✅ WORKFLOW COMPLETED SUCCESSFULLY
```

## 🎨 Customization Examples

### Change OpenAI Model
Edit `.env`:
```bash
OPENAI_MODEL=gpt-4-turbo
```

### Adjust LinkedIn Post Length
Edit `config.py` → `LINKEDIN_SYSTEM_PROMPT`:
```python
# Change: "Posts should be between 150-300 words"
# To: "Posts should be between 200-400 words"
```

### Modify Validation Criteria
Edit `config.py` → `VALIDATION_PROMPT_TEMPLATE` to add custom validation rules.

## 🐛 Troubleshooting

### "OPENAI_API_KEY not configured" Error
- Make sure you've created a `.env` file (copy from `.env.example`)
- Verify your API key is correctly set in `.env`
- Check that the API key has no extra spaces or quotes

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Agent Execution Failures
- Check your internet connection
- Verify your OpenAI API key is valid and has credits
- Review console output for specific error messages

## 📚 Learn More

- [Agno Documentation](https://docs.agno.com/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Python ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)

## 🤝 Contributing

To customize this workflow:

1. Modify `config.py` for prompt changes
2. Edit agent files in `agents/` for behavior changes
3. Update `main.py` for workflow modifications

## 📝 License

This project is provided as-is for your use and modification.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Agno documentation
3. Verify your API key and environment setup

---

**Built with [Agno](https://docs.agno.com) - The fastest multi-agent framework**

