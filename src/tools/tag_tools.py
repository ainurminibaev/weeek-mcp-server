"""
Tag tools for Weeek MCP Server.

Provides tools for managing workspace tags.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_tag_tools(server, client) -> int:
    """
    Register tag-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_tags(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all tags in the workspace.
        
        Retrieves all available tags that can be used to categorize
        tasks and other items in the workspace.
        
        Args:
            limit: Maximum number of tags to return (1-100, default: 50)
            offset: Number of tags to skip for pagination (default: 0)
            
        Returns:
            dict: List of tags containing:
                - tags: Array of tag objects with id, title, color
                - total: Total number of tags
                
        Example:
            >>> tags = await list_tags(limit=20)
            >>> for tag in tags["data"]:
            ...     print(f"{tag['title']}: {tag['color']}")
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/ws/tags", params)
            return ToolResult.success(response, "Tags list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_tag(title: str) -> Dict[str, Any]:
        """
        Create a new tag in the workspace.
        
        Creates a tag that can be used to categorize tasks and
        other items in the workspace.
        
        Args:
            title: The name/title of the tag to create (required, max 255 chars)
            
        Returns:
            dict: Created tag object containing:
                - id: Unique tag identifier
                - title: Tag name
                - color: Tag color (auto-assigned or default)
                
        Example:
            >>> tag = await create_tag(title="urgent")
            >>> print(tag["data"]["id"])
            "tag_abc123"
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            response = await client.post("/ws/tags", payload)
            return ToolResult.success(response, f"Tag '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_tag(
        tag_id: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing tag.
        
        Updates the title of an existing tag. The tag ID must be valid.
        
        Args:
            tag_id: The unique identifier of the tag to update (required)
            title: New title for the tag (optional)
            
        Returns:
            dict: Updated tag object
            
        Example:
            >>> result = await update_tag(
            ...     tag_id="tag_123",
            ...     title="priority"
            ... )
        """
        try:
            if not tag_id:
                return ToolResult.error("tag_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/ws/tags/{tag_id}", payload)
            return ToolResult.success(response, f"Tag {tag_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_tag(tag_id: str) -> Dict[str, Any]:
        """
        Delete a tag from the workspace.
        
        Removes a tag from the workspace. Tasks that have this tag
        will have it removed but will not be deleted.
        
        Args:
            tag_id: The unique identifier of the tag to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Example:
            >>> result = await delete_tag("tag_123")
            >>> print(result["success"])
            True
        """
        try:
            if not tag_id:
                return ToolResult.error("tag_id is required")
            response = await client.delete(f"/ws/tags/{tag_id}")
            return ToolResult.success(response, f"Tag {tag_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 4  # Number of registered tools

