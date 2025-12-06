"""
Funnel tools for Weeek MCP Server.

Provides tools for managing sales funnels.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_funnel_tools(server, client) -> int:
    """
    Register funnel-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_funnels(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all sales funnels in the workspace.
        
        Retrieves all funnels used for CRM and deal tracking.
        
        Args:
            limit: Maximum number of funnels to return (1-100, default: 50)
            offset: Number of funnels to skip for pagination (default: 0)
            
        Returns:
            dict: List of funnels containing:
                - funnels: Array of funnel objects
                - total: Total number of funnels
                
        Example:
            >>> funnels = await list_funnels()
            >>> for funnel in funnels["data"]:
            ...     print(funnel["title"])
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/crm/funnels", params)
            return ToolResult.success(response, "Funnels list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_funnel_by_id(funnel_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific funnel.
        
        Retrieves full details of a funnel including its statuses.
        
        Args:
            funnel_id: The unique identifier of the funnel (required)
            
        Returns:
            dict: Funnel information containing:
                - id: Funnel ID
                - title: Funnel name
                - description: Funnel description
                - statuses: Array of funnel statuses
                
        Example:
            >>> funnel = await get_funnel_by_id("funnel_123")
            >>> print(funnel["data"]["title"])
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            response = await client.get(f"/crm/funnels/{funnel_id}")
            return ToolResult.success(response, f"Funnel {funnel_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_funnel(
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new sales funnel.
        
        Creates a funnel for tracking deals and sales pipeline.
        
        Args:
            title: The name of the funnel (required)
            description: Description of the funnel (optional)
            
        Returns:
            dict: Created funnel object
            
        Example:
            >>> funnel = await create_funnel(
            ...     title="Sales Pipeline",
            ...     description="Main sales funnel for B2B"
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            if description is not None:
                payload["description"] = description
            
            response = await client.post("/crm/funnels", payload)
            return ToolResult.success(response, f"Funnel '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_funnel(
        funnel_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing funnel.
        
        Updates the specified fields of a funnel.
        
        Args:
            funnel_id: The unique identifier of the funnel (required)
            title: New title for the funnel (optional)
            description: New description (optional)
            
        Returns:
            dict: Updated funnel object
            
        Example:
            >>> result = await update_funnel(
            ...     funnel_id="funnel_123",
            ...     title="Enterprise Sales"
            ... )
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/crm/funnels/{funnel_id}", payload)
            return ToolResult.success(response, f"Funnel {funnel_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_funnel(funnel_id: str) -> Dict[str, Any]:
        """
        Delete a funnel from the workspace.
        
        Removes a funnel. Deals within the funnel may be
        deleted or moved depending on settings.
        
        Args:
            funnel_id: The unique identifier of the funnel to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This may affect all deals in the funnel.
            
        Example:
            >>> result = await delete_funnel("funnel_123")
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            response = await client.delete(f"/crm/funnels/{funnel_id}")
            return ToolResult.success(response, f"Funnel {funnel_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

