# Quick Start Guide

Get up and running in 5 minutes! ⚡

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure OpenAI API Key

Create a `.env` file:

```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o
```

## Step 3: Customize Your Input

Edit `main.py` and modify these sections:

```python
context = """
Your business/product context here
"""

examples = """
Your example LinkedIn and X posts here
"""

num_posts = 3  # How many posts per platform
```

## Step 4: Run the Workflow

```bash
python main.py
```

## Step 5: View Results

- Console output shows real-time progress
- `output.txt` contains the complete results

## 🎨 Customizing Agent Behavior

Want different post styles? Edit `config.py`:

- `ORCHESTRATOR_SYSTEM_PROMPT` - Master agent behavior
- `LINKEDIN_SYSTEM_PROMPT` - LinkedIn post style
- `X_SYSTEM_PROMPT` - X/Twitter post style

## 📊 Example Output Structure

```
🚀 Starting Thought Leadership Workflow...
⚡ Executing LinkedIn and X agents in parallel...
✓ LinkedIn Agent completed
✓ X Agent completed
🔍 Validating generated content...
✅ Validation complete!

📊 FINAL OUTPUT
├── LinkedIn Posts (3)
│   ├── Post 1
│   ├── Post 2
│   └── Post 3
└── X Posts (3)
    ├── Post 1
    ├── Post 2
    └── Post 3
```

## 🐛 Common Issues

**"OPENAI_API_KEY not configured"**
- Make sure `.env` file exists
- Check API key has no extra spaces
- Verify key starts with `sk-`

**Import errors**
```bash
pip install -r requirements.txt --upgrade
```

**Agent execution fails**
- Check internet connection
- Verify OpenAI API key is valid
- Ensure API has sufficient credits

## 🚀 Next Steps

1. ✅ Run with default settings to test
2. 📝 Customize your context and examples
3. 🎨 Adjust system prompts in `config.py`
4. 🔄 Iterate and refine your content

## 💡 Pro Tips

- **Better Examples = Better Output**: Provide 2-3 high-quality example posts
- **Context is King**: More detailed context = more relevant posts
- **Experiment with Models**: Try `gpt-4-turbo` or `gpt-4` in `.env`
- **Adjust Post Count**: Start with 3, scale up as needed

---

Need help? Check the full [README.md](README.md) for detailed documentation.

