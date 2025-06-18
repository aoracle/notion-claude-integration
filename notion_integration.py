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
            tags = self.config["default_tags"]
        
        # Create the page
        page_data = {
            "parent": {"database_id": self.default_db},
            "properties": {
                "Page": {
                    "title": [{"text": {"content": title}}]
                },
                "Tags": {
                    "multi_select": [{"name": tag} for tag in tags]
                }
            }
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
        
        block_data = {"children": blocks}
        
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
                            blocks.append({
                                "object": "block",
                                "type": "bulleted_list_item",
                                "bulleted_list_item": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": line.strip()[2:]}
                                    }]
                                }
                            })
                elif para.strip().startswith('#'):
                    # Create heading
                    level = len(para) - len(para.lstrip('#'))
                    heading_type = f"heading_{min(level, 3)}"
                    blocks.append({
                        "object": "block",
                        "type": heading_type,
                        heading_type: {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": para.strip('#').strip()}
                            }]
                        }
                    })
                else:
                    # Create paragraph
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": para.strip()}
                            }]
                        }
                    })
        
        return blocks
    
    def quick_note(self, content: str) -> Dict:
        """Create a quick note with auto-generated title"""
        # Generate title from first line or date
        lines = content.strip().split('\n')
        if lines and len(lines[0]) < 100:
            title = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
        else:
            title = f"Quick Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self.create_page_with_notes(title, content, ["DAILY", "PRODUCTIVITY"])
    
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
            if page["properties"]["Page"]["title"]:
                title = page["properties"]["Page"]["title"][0]["plain_text"]
            
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
    
    notion = NotionIntegration()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python notion_integration.py create <title> <notes>")
        print("  python notion_integration.py quick <notes>")
        print("  python notion_integration.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
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