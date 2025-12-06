#!/usr/bin/env python
"""
Simple runner script for Weeek MCP Server.
Run from the weeek-mcp-server directory.
"""

import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Run the server
from src.server import mcp
mcp.run()

