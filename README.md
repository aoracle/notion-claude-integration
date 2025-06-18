# Notion Integration for Claude Code

Seamless integration between Claude Code and Notion for capturing notes, ideas, and documentation.

## 🎯 Overview

This integration allows Claude Code to directly create and manage Notion pages, making it easy to capture development notes, meeting summaries, and technical documentation without leaving your terminal.

## ✨ Features

- **Quick Notes**: Create Notion pages with a single command
- **Auto-formatting**: Content is automatically formatted with proper headings and structure
- **Tagging System**: Automatic tagging for better organization
- **Database Integration**: Works with your existing Notion databases
- **CLI & Python API**: Use via command line or integrate into your workflows

## 🚀 Quick Start

1. **Setup the integration:**
   ```bash
   ./setup_notion_integration.sh
   ```

2. **Configure your Notion credentials:**
   - Copy `notion_config.example.json` to `notion_config.json`
   - Add your Notion API token and database ID

3. **Start using:**
   ```bash
   # Create a new page
   python notion_integration.py create "Meeting Notes" "Today's standup discussion..."
   
   # Add a quick note
   python notion_integration.py quick "Remember to review PR #123"
   
   # List recent pages
   python notion_integration.py list
   ```

## 📝 Usage Examples

### Command Line Interface
```bash
# Using the shell helper
./notion-api-helper.sh create "Project Ideas" "content.txt"

# Using the Python CLI
python notion_integration.py create "Bug Report" "Found issue with login flow..."
```

### Python Integration
```python
from notion_integration import create_page, quick_note

# Create a detailed page
create_page(
    title="Technical Design Document",
    content="## Overview\n\nSystem architecture details..."
)

# Add a quick note
quick_note("TODO: Implement caching layer")
```

### With Claude Code
When using Claude Code, simply ask:
- "Create a Notion page with meeting notes"
- "Save this code snippet to Notion"
- "Add this to my Notion tasks"

## 🔧 Configuration

Edit `notion_config.json`:
```json
{
  "notion_api_token": "your-token-here",
  "default_database_id": "your-database-id",
  "default_database_name": "Personal",
  "default_tags": ["PRODUCTIVITY"],
  "integration_name": "claude"
}
```

### Getting Your Notion API Token
1. Go to https://www.notion.so/my-integrations
2. Create a new integration
3. Copy the "Internal Integration Token"
4. Share your database with the integration

## 📁 Files

- `notion_integration.py` - Main integration module
- `notion_helper.py` - Helper functions
- `notion-api-helper.sh` - Shell script interface
- `setup_notion_integration.sh` - Automated setup script
- `notion` - Quick CLI wrapper
- `claude-code-notion-integration.md` - Detailed documentation

## 🛠️ Requirements

- Python 3.7+
- `requests` library
- Notion API token
- Shared Notion database

## 🔒 Security

- Never commit `notion_config.json` (it's in .gitignore)
- Use environment variables for tokens in production
- Regularly rotate your API tokens

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please submit PRs for:
- Additional Notion blocks support
- Enhanced formatting options
- Better error handling
- Template system

---

Built to make developer note-taking effortless! 📝✨