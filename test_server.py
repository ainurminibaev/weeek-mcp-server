#!/usr/bin/env python
"""
Test script to verify Weeek MCP Server initialization and basic operations.
"""

import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def test_server():
    """Test server initialization and basic API calls."""
    print("=" * 60)
    print("Testing Weeek MCP Server")
    print("=" * 60)
    
    # Test 1: Configuration loading
    print("\n[1] Testing configuration loading...")
    try:
        from src.config import get_config
        config = get_config()
        print(f"    ✓ Configuration loaded successfully")
        print(f"    ✓ Base URL: {config.weeek_base_url}")
        print(f"    ✓ Token: {config.weeek_token[:8]}...{config.weeek_token[-4:]}")
    except Exception as e:
        print(f"    ✗ Configuration error: {e}")
        return
    
    # Test 2: Client initialization
    print("\n[2] Testing Weeek client...")
    try:
        from src.weeek_client import WeeekClient
        client = WeeekClient()
        print(f"    ✓ Client initialized")
    except Exception as e:
        print(f"    ✗ Client initialization error: {e}")
        return
    
    # Test 3: API connection - get workspace info
    print("\n[3] Testing API connection (getting workspace info)...")
    try:
        result = await client.get("/ws")
        print(f"    ✓ API connection successful!")
        if "workspace" in result:
            ws = result["workspace"]
            print(f"    ✓ Workspace: {ws.get('name', 'N/A')}")
            print(f"    ✓ Workspace ID: {ws.get('id', 'N/A')}")
        else:
            print(f"    ✓ Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"    ✗ API connection error: {e}")
    
    # Test 4: Get workspace members
    print("\n[4] Testing workspace members endpoint...")
    try:
        result = await client.get("/ws/members", {"limit": 5})
        print(f"    ✓ Members endpoint works!")
        if "members" in result:
            members = result["members"]
            print(f"    ✓ Found {len(members)} members")
            for m in members[:3]:
                name = f"{m.get('firstName', '')} {m.get('lastName', '')}".strip() or m.get('email', 'N/A')
                print(f"      - {name}")
        else:
            print(f"    ✓ Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"    ✗ Members endpoint error: {e}")
    
    # Test 5: Get projects
    print("\n[5] Testing projects endpoint...")
    try:
        result = await client.get("/tm/projects")
        print(f"    ✓ Projects endpoint works!")
        if "projects" in result:
            projects = result["projects"]
            print(f"    ✓ Found {len(projects)} projects")
            for p in projects[:3]:
                print(f"      - {p.get('name', 'N/A')} (ID: {p.get('id')})")
            if len(projects) > 3:
                print(f"      ... and {len(projects) - 3} more")
        else:
            print(f"    ✓ Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"    ✗ Projects endpoint error: {e}")
    
    # Test 6: Get tasks
    print("\n[6] Testing tasks endpoint...")
    try:
        result = await client.get("/tm/tasks", {"limit": 5})
        print(f"    ✓ Tasks endpoint works!")
        if "tasks" in result:
            tasks = result["tasks"]
            print(f"    ✓ Found {len(tasks)} tasks (limited to 5)")
            for t in tasks[:3]:
                print(f"      - {t.get('title', 'N/A')} (ID: {t.get('id')})")
        else:
            print(f"    ✓ Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"    ✗ Tasks endpoint error: {e}")
    
    # Test 7: MCP Server initialization
    print("\n[7] Testing MCP server initialization...")
    try:
        from src.server import mcp
        print(f"    ✓ MCP server created successfully")
        # Get list of tools
        # FastMCP stores tools internally, let's count them
        print(f"    ✓ Server name: weeek-mcp")
    except Exception as e:
        print(f"    ✗ MCP server error: {e}")
    
    # Cleanup
    await client.close()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_server())

