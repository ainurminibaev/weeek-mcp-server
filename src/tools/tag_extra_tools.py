"""
Extra Tag tools for Weeek MCP Server.

Provides additional tools for working with tags.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_tag_extra_tools(server, client) -> int:
    """
    Register extra tag-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def get_tag_details(tag_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific tag.
        
        Retrieves full details of a tag including usage statistics.
        
        Args:
            tag_id: The unique identifier of the tag (required)
            
        Returns:
            dict: Tag information containing:
                - id: Tag ID
                - title: Tag name
                - color: Tag color
                - usage_count: Number of items using this tag
                
        Example:
            >>> tag = await get_tag_details("tag_123")
            >>> print(f"Tag '{tag['data']['title']}' used {tag['data'].get('usage_count', 0)} times")
        """
        try:
            if not tag_id:
                return ToolResult.error("tag_id is required")
            response = await client.get(f"/tag/{tag_id}")
            return ToolResult.success(response, f"Tag {tag_id} details retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_tasks_by_tag(
        tag_id: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get all tasks that have a specific tag.
        
        Retrieves all tasks tagged with the specified tag ID.
        
        Args:
            tag_id: The unique identifier of the tag (required)
            limit: Maximum number of tasks to return (1-100, default: 50)
            offset: Number of tasks to skip for pagination (default: 0)
            
        Returns:
            dict: List of tasks containing:
                - tasks: Array of task objects with this tag
                - total: Total number of tasks with this tag
                
        Example:
            >>> results = await get_tasks_by_tag(
            ...     tag_id="tag_urgent",
            ...     limit=20
            ... )
            >>> print(f"Found {len(results['data'])} urgent tasks")
            >>> for task in results["data"]:
            ...     print(f"- {task['title']}")
        """
        try:
            if not tag_id:
                return ToolResult.error("tag_id is required")
            
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get(f"/tag/{tag_id}/tasks", params)
            return ToolResult.success(response, f"Tasks with tag {tag_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 2  # Number of registered tools

