# Claude Code Notion Integration - Complete Package

This package contains all scripts needed to set up Notion integration for Claude Code.

## Files Included

1. `setup_notion_integration.sh` - Automated setup script
2. `notion_integration.py` - Python integration script (created by setup)
3. `notion_config.json` - Configuration template (created by setup)

## Quick Setup

```bash
# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/claude-notion-integration/main/setup_notion_integration.sh | bash
```

Or manually:

```bash
# 1. Save the setup script
# 2. Make it executable
chmod +x setup_notion_integration.sh

# 3. Run it
./setup_notion_integration.sh
```

## Manual Setup Instructions

### 1. Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "claude")
4. Copy the Internal Integration Token

### 2. Share Your Database

1. Open your Notion database
2. Click ... → Add connections → Select your integration
3. Copy the database ID from the URL (32-character string)

### 3. Run Setup Script

The setup script will:
- Create `~/.claude` directory
- Prompt for your API token and database ID
- Create all necessary files
- Install Python dependencies
- Test the installation

## Usage

After setup, you can use:

```bash
# Create a page with title and content
~/.claude/notion create "Meeting Notes" "Today we discussed..."

# Quick note (auto-generates title)
~/.claude/notion quick "Remember to follow up on..."

# List recent pages
~/.claude/notion list
```

## Integration with Claude Code

Add this to your `CLAUDE.md` file:

```markdown
## Notion Integration

When the user asks to create a Notion page or add notes, use:
python3 ~/.claude/notion_integration.py create "Title" "Content"
```

## Complete Setup Script

```bash
#!/bin/bash

# Claude Code Notion Integration Setup Script
# This script sets up the Notion integration for Claude Code

echo "==================================="
echo "Claude Code Notion Integration Setup"
echo "==================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create .claude directory if it doesn't exist
echo "1. Creating ~/.claude directory..."
mkdir -p ~/.claude

# Prompt for Notion API token
echo ""
echo "2. Notion API Configuration"
echo "   Please create a Notion integration first:"
echo "   - Go to https://www.notion.so/my-integrations"
echo "   - Click 'New integration'"
echo "   - Name it (e.g., 'claude')"
echo "   - Copy the Internal Integration Token"
echo ""
read -p "Enter your Notion API token: " NOTION_TOKEN

# Prompt for database ID
echo ""
echo "3. Database Configuration"
echo "   Share your target database with the integration:"
echo "   - Open your Notion database"
echo "   - Click ... → Add connections → Select your integration"
echo "   - Copy the database ID from the URL"
echo "   - URL format: notion.so/workspace/DATABASE_ID?v=..."
echo ""
read -p "Enter your database ID: " DATABASE_ID

# Create notion_config.json
echo ""
echo "4. Creating configuration file..."
cat > ~/.claude/notion_config.json << EOF
{
  "notion_api_token": "$NOTION_TOKEN",
  "default_database_id": "$DATABASE_ID",
  "default_database_name": "Personal",
  "default_tags": ["PRODUCTIVITY"],
  "integration_name": "claude"
}
EOF

# Create notion_integration.py
echo "5. Creating integration script..."
cat > ~/.claude/notion_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Notion Integration for Claude Code
Automatically handles page creation and note management
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class NotionIntegration:
    def __init__(self):
        # Load config
        config_path = os.path.join(os.path.dirname(__file__), "notion_config.json")
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.token = self.config["notion_api_token"]
        self.default_db = self.config["default_database_id"]
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_page_with_notes(self, title: str, notes: str, tags: Optional[List[str]] = None) -> Dict:
        """Create a page with notes in the default database"""
        if not tags:
            tags = self.config.get("default_tags", [])
        
        # First, get database schema to understand properties
        db_response = requests.get(
            f"{self.base_url}/databases/{self.default_db}",
            headers=self.headers
        )
        
        if db_response.status_code != 200:
            return {"error": f"Failed to get database: {db_response.text}"}
        
        db_schema = db_response.json()
        properties = db_schema["properties"]
        
        # Find the title property (could be Title, Name, Page, etc.)
        title_prop = None
        for prop_name, prop_config in properties.items():
            if prop_config["type"] == "title":
                title_prop = prop_name
                break
        
        if not title_prop:
            return {"error": "Could not find title property in database"}
        
        # Build page data
        page_data = {
            "parent": {"database_id": self.default_db},
            "properties": {
                title_prop: {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        
        # Add tags if the database has a Tags property
        if tags and "Tags" in properties and properties["Tags"]["type"] == "multi_select":
            page_data["properties"]["Tags"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }
        
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=page_data
        )
        
        if response.status_code != 200:
            return {"error": f"Failed to create page: {response.text}"}
        
        page = response.json()
        page_id = page["id"]
        
        # Add notes as blocks
        blocks = self._format_notes_as_blocks(notes)
        
        # Split into chunks if needed (Notion has a 2000 char limit per block)
        for i in range(0, len(blocks), 10):  # Send 10 blocks at a time
            chunk = blocks[i:i+10]
            block_data = {"children": chunk}
            
            response = requests.patch(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=self.headers,
                json=block_data
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to add notes: {response.text}"}
        
        return {
            "success": True,
            "page_id": page_id,
            "url": page["url"],
            "title": title,
            "message": f"Created page '{title}' with notes"
        }
    
    def _format_notes_as_blocks(self, notes: str) -> List[Dict]:
        """Convert notes string into Notion blocks"""
        blocks = []
        
        # Add timestamp
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"Created by Claude Code - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                }]
            }
        })
        
        # Split notes by double newlines for paragraphs
        paragraphs = notes.strip().split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                # Check if it's a list
                if para.strip().startswith('- ') or para.strip().startswith('* '):
                    # Create bulleted list
                    lines = para.strip().split('\n')
                    for line in lines:
                        if line.strip().startswith(('- ', '* ')):
                            content = line.strip()[2:]
                            # Split long content
                            if len(content) > 1900:
                                content = content[:1900] + "..."
                            blocks.append({
                                "object": "block",
                                "type": "bulleted_list_item",
                                "bulleted_list_item": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": content}
                                    }]
                                }
                            })
                elif para.strip().startswith('#'):
                    # Create heading
                    level = len(para) - len(para.lstrip('#'))
                    heading_type = f"heading_{min(level, 3)}"
                    content = para.strip('#').strip()
                    if len(content) > 1900:
                        content = content[:1900] + "..."
                    blocks.append({
                        "object": "block",
                        "type": heading_type,
                        heading_type: {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": content}
                            }]
                        }
                    })
                else:
                    # Create paragraph, split if too long
                    content = para.strip()
                    while content:
                        chunk = content[:1900]
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": chunk}
                                }]
                            }
                        })
                        content = content[1900:]
        
        return blocks
    
    def quick_note(self, content: str) -> Dict:
        """Create a quick note with auto-generated title"""
        # Generate title from first line or date
        lines = content.strip().split('\n')
        if lines and len(lines[0]) < 100:
            title = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
        else:
            title = f"Quick Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        default_tags = self.config.get("default_tags", [])
        if "DAILY" not in default_tags:
            tags = ["DAILY"] + default_tags
        else:
            tags = default_tags
        
        return self.create_page_with_notes(title, content, tags)
    
    def list_recent_pages(self, limit: int = 5) -> Dict:
        """List recent pages from the default database"""
        data = {
            "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
            "page_size": limit
        }
        
        response = requests.post(
            f"{self.base_url}/databases/{self.default_db}/query",
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            return {"error": f"Failed to list pages: {response.text}"}
        
        result = response.json()
        pages = []
        
        for page in result["results"]:
            title = "Untitled"
            # Look for title property in any of the common names
            for prop_name, prop_value in page["properties"].items():
                if prop_value.get("type") == "title" and prop_value.get("title"):
                    title = prop_value["title"][0]["plain_text"]
                    break
            
            pages.append({
                "id": page["id"],
                "title": title,
                "url": page["url"],
                "last_edited": page["last_edited_time"]
            })
        
        return {"pages": pages}

# CLI interface
if __name__ == "__main__":
    import sys
    
    try:
        notion = NotionIntegration()
    except FileNotFoundError:
        print("Error: notion_config.json not found. Please run the setup script first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid notion_config.json. Please check the configuration.")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python notion_integration.py create <title> <notes>")
        print("  python notion_integration.py quick <notes>")
        print("  python notion_integration.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "create" and len(sys.argv) >= 4:
            title = sys.argv[2]
            notes = " ".join(sys.argv[3:])
            result = notion.create_page_with_notes(title, notes)
            print(json.dumps(result, indent=2))
        
        elif command == "quick" and len(sys.argv) >= 3:
            notes = " ".join(sys.argv[2:])
            result = notion.quick_note(notes)
            print(json.dumps(result, indent=2))
        
        elif command == "list":
            result = notion.list_recent_pages()
            if "pages" in result:
                for page in result["pages"]:
                    print(f"- {page['title']} ({page['id'][:8]}...)")
            else:
                print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
EOF

# Create wrapper script
echo "6. Creating wrapper script..."
cat > ~/.claude/notion << 'EOF'
#!/bin/bash
# Notion CLI wrapper for Claude Code

python3 ~/.claude/notion_integration.py "$@"
EOF

# Make scripts executable
chmod +x ~/.claude/notion_integration.py
chmod +x ~/.claude/notion

# Install requests if needed
echo ""
echo "7. Checking Python dependencies..."
if python3 -c "import requests" 2>/dev/null; then
    echo "   ✓ requests module is already installed"
else
    echo "   Installing requests module..."
    pip3 install requests || {
        echo "   Warning: Could not install requests automatically."
        echo "   Please run: pip3 install requests"
    }
fi

# Test the installation
echo ""
echo "8. Testing the installation..."
if python3 ~/.claude/notion_integration.py list > /dev/null 2>&1; then
    echo "   ✓ Installation successful!"
    echo ""
    echo "==================================="
    echo "Setup Complete!"
    echo "==================================="
    echo ""
    echo "You can now use these commands:"
    echo "  ~/.claude/notion create \"Title\" \"Content\""
    echo "  ~/.claude/notion quick \"Quick note content\""
    echo "  ~/.claude/notion list"
    echo ""
    echo "For Claude Code integration, add to your CLAUDE.md:"
    echo "  When users ask to create Notion pages, use:"
    echo "  python3 ~/.claude/notion_integration.py create \"Title\" \"Content\""
else
    echo "   ⚠ Installation test failed. Please check your API token and database ID."
fi
```

## Troubleshooting

### Common Issues

1. **Python not installed**: Install Python 3.x
2. **requests module missing**: Run `pip3 install requests`
3. **Invalid token**: Check your Notion integration token
4. **Database not shared**: Share your database with the integration
5. **Wrong property names**: Script auto-detects title property

### Support

For issues or improvements, please contribute to the repository.