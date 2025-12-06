"""
Workspace tools for Weeek MCP Server.

Provides tools for workspace information retrieval via members endpoint.
Note: The /workspace endpoint is not available in Weeek API.
"""

from typing import Any, Dict, Optional

from .base import handle_api_errors, ToolResult, build_query_params


def register_workspace_tools(server, client) -> int:
    """
    Register workspace-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def get_workspace_info() -> Dict[str, Any]:
        """
        Get workspace information by retrieving workspace members.
        
        Since the /workspace endpoint is not available, this retrieves
        workspace context through the members list.
        
        Returns:
            dict: Workspace context containing:
                - members: List of workspace members
                - success: Operation status
                
        Example:
            >>> result = await get_workspace_info()
            >>> print(f"Workspace has {len(result['data']['members'])} members")
        """
        try:
            response = await client.get("/ws/members")
            return ToolResult.success(response, "Workspace information retrieved via members")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def list_workspace_tags(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all tags in the workspace.
        
        Retrieves all tags available in the workspace.
        
        Args:
            limit: Maximum number of tags to return (1-100, default: 50)
            offset: Number of tags to skip for pagination (default: 0)
            
        Returns:
            dict: List of tags containing:
                - tags: Array of tag objects
                - total: Total number of tags
                
        Example:
            >>> tags = await list_workspace_tags()
            >>> for tag in tags["data"]["tags"]:
            ...     print(tag["title"])
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/ws/tags", params)
            return ToolResult.success(response, "Workspace tags retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 2  # Number of registered tools

