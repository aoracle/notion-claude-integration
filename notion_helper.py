#!/usr/bin/env python3
"""
Notion API Helper for Claude Code
Requires: pip install requests
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional

class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def search(self, query: str) -> Dict:
        """Search for pages and databases"""
        data = {
            "query": query,
            "filter": {"property": "object", "value": "page"}
        }
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def list_databases(self) -> Dict:
        """List all accessible databases"""
        data = {"filter": {"property": "object", "value": "database"}}
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_page(self, page_id: str) -> Dict:
        """Get page details"""
        response = requests.get(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_database(self, database_id: str) -> Dict:
        """Get database schema"""
        response = requests.get(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        )
        return response.json()
    
    def query_database(self, database_id: str, filter_obj: Optional[Dict] = None) -> Dict:
        """Query a database with optional filters"""
        data = {}
        if filter_obj:
            data["filter"] = filter_obj
        
        response = requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def create_page(self, parent_id: str, title: str, parent_type: str = "database_id") -> Dict:
        """Create a new page"""
        data = {
            "parent": {parent_type: parent_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def append_block(self, page_id: str, content: str, block_type: str = "paragraph") -> Dict:
        """Append a block to a page"""
        data = {
            "children": [{
                "object": "block",
                "type": block_type,
                block_type: {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }]
        }
        response = requests.patch(
            f"{self.base_url}/blocks/{page_id}/children",
            headers=self.headers,
            json=data
        )
        return response.json()

def main():
    # Get token from environment
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        print("Error: NOTION_API_TOKEN environment variable not set")
        sys.exit(1)
    
    client = NotionClient(token)
    
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python notion_helper.py <command> [args]")
        print("\nCommands:")
        print("  search <query>")
        print("  list-databases")
        print("  get-page <page_id>")
        print("  get-database <database_id>")
        print("  query-database <database_id>")
        print("  create-page <database_id> <title>")
        print("  append-block <page_id> <content>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "search" and len(sys.argv) > 2:
            result = client.search(sys.argv[2])
        elif command == "list-databases":
            result = client.list_databases()
        elif command == "get-page" and len(sys.argv) > 2:
            result = client.get_page(sys.argv[2])
        elif command == "get-database" and len(sys.argv) > 2:
            result = client.get_database(sys.argv[2])
        elif command == "query-database" and len(sys.argv) > 2:
            result = client.query_database(sys.argv[2])
        elif command == "create-page" and len(sys.argv) > 3:
            result = client.create_page(sys.argv[2], sys.argv[3])
        elif command == "append-block" and len(sys.argv) > 3:
            result = client.append_block(sys.argv[2], sys.argv[3])
        else:
            print(f"Invalid command or missing arguments: {command}")
            sys.exit(1)
        
        print(json.dumps(result, indent=2))
    
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()