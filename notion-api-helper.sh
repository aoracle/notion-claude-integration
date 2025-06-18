#!/bin/bash

# Notion API Helper Script
# Usage: ./notion-api-helper.sh <command> [options]

# Check if NOTION_API_TOKEN is set
if [ -z "$NOTION_API_TOKEN" ]; then
    echo "Error: NOTION_API_TOKEN environment variable is not set"
    echo "Set it with: export NOTION_API_TOKEN='your_secret_token'"
    exit 1
fi

NOTION_API_BASE="https://api.notion.com/v1"
NOTION_VERSION="2022-06-28"

# Function to make authenticated requests
notion_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" \
            "$NOTION_API_BASE/$endpoint" \
            -H "Authorization: Bearer $NOTION_API_TOKEN" \
            -H "Content-Type: application/json" \
            -H "Notion-Version: $NOTION_VERSION"
    else
        curl -s -X "$method" \
            "$NOTION_API_BASE/$endpoint" \
            -H "Authorization: Bearer $NOTION_API_TOKEN" \
            -H "Content-Type: application/json" \
            -H "Notion-Version: $NOTION_VERSION" \
            -d "$data"
    fi
}

# Command handler
case "$1" in
    "search")
        # Search for pages and databases
        query=$2
        data='{
            "query": "'$query'",
            "filter": {
                "property": "object",
                "value": "page"
            }
        }'
        notion_request "POST" "search" "$data" | jq '.'
        ;;
        
    "list-databases")
        # List all accessible databases
        notion_request "POST" "search" '{"filter":{"property":"object","value":"database"}}' | jq '.'
        ;;
        
    "get-page")
        # Get a specific page by ID
        page_id=$2
        if [ -z "$page_id" ]; then
            echo "Usage: $0 get-page <page_id>"
            exit 1
        fi
        notion_request "GET" "pages/$page_id" | jq '.'
        ;;
        
    "get-database")
        # Get database schema
        db_id=$2
        if [ -z "$db_id" ]; then
            echo "Usage: $0 get-database <database_id>"
            exit 1
        fi
        notion_request "GET" "databases/$db_id" | jq '.'
        ;;
        
    "query-database")
        # Query a database
        db_id=$2
        if [ -z "$db_id" ]; then
            echo "Usage: $0 query-database <database_id>"
            exit 1
        fi
        notion_request "POST" "databases/$db_id/query" '{}' | jq '.'
        ;;
        
    "create-page")
        # Create a new page in a database
        db_id=$2
        title=$3
        if [ -z "$db_id" ] || [ -z "$title" ]; then
            echo "Usage: $0 create-page <database_id> <title>"
            exit 1
        fi
        data='{
            "parent": {"database_id": "'$db_id'"},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": "'$title'"
                            }
                        }
                    ]
                }
            }
        }'
        notion_request "POST" "pages" "$data" | jq '.'
        ;;
        
    "append-block")
        # Append a text block to a page
        page_id=$2
        text=$3
        if [ -z "$page_id" ] || [ -z "$text" ]; then
            echo "Usage: $0 append-block <page_id> <text>"
            exit 1
        fi
        data='{
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "'$text'"
                                }
                            }
                        ]
                    }
                }
            ]
        }'
        notion_request "PATCH" "blocks/$page_id/children" "$data" | jq '.'
        ;;
        
    *)
        echo "Notion API Helper"
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  search <query>              - Search for pages"
        echo "  list-databases              - List all databases"
        echo "  get-page <page_id>          - Get page details"
        echo "  get-database <db_id>        - Get database schema"
        echo "  query-database <db_id>      - Query a database"
        echo "  create-page <db_id> <title> - Create a new page"
        echo "  append-block <page_id> <text> - Add text to a page"
        echo ""
        echo "Set NOTION_API_TOKEN environment variable before use"
        ;;
esac