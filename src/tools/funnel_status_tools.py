"""
Funnel Status tools for Weeek MCP Server.

Provides tools for managing funnel statuses (stages).
Note: Funnel statuses are accessed via /crm/funnels/{funnel_id}/statuses
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_funnel_status_tools(server, client) -> int:
    """
    Register funnel status-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_funnel_statuses(
        funnel_id: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of statuses for a specific funnel.
        
        Retrieves all statuses (stages) for the specified funnel.
        
        Args:
            funnel_id: The funnel ID to get statuses from (required)
            limit: Maximum number of statuses to return (1-100, default: 50)
            offset: Number of statuses to skip for pagination (default: 0)
            
        Returns:
            dict: List of funnel statuses containing:
                - statuses: Array of status objects with id, name, dealsCount
                - total: Total number of statuses
                
        Example:
            >>> statuses = await list_funnel_statuses(funnel_id="XSx4OQGb4KvEL7Rq")
            >>> for status in statuses["data"]["statuses"]:
            ...     print(f"{status['name']}: {status['dealsCount']} deals")
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get(f"/crm/funnels/{funnel_id}/statuses", params)
            return ToolResult.success(response, "Funnel statuses list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_funnel_status_by_id(
        funnel_id: str,
        status_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific funnel status.
        
        Retrieves full details of a funnel status.
        
        Args:
            funnel_id: The funnel ID (required)
            status_id: The unique identifier of the status (required)
            
        Returns:
            dict: Status information containing:
                - id: Status ID
                - name: Status name
                - dealsCount: Number of deals in this status
                - dealsAmount: Total amount of deals
                
        Example:
            >>> status = await get_funnel_status_by_id(
            ...     funnel_id="XSx4OQGb4KvEL7Rq",
            ...     status_id="JwPoZuaQ81DdrxyD"
            ... )
            >>> print(status["data"]["name"])
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            if not status_id:
                return ToolResult.error("status_id is required")
            response = await client.get(f"/crm/funnels/{funnel_id}/statuses/{status_id}")
            return ToolResult.success(response, f"Funnel status {status_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_funnel_status(
        funnel_id: str,
        name: str,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new status in a funnel.
        
        Creates a stage/status in a sales funnel for deal progression.
        
        Args:
            funnel_id: ID of the funnel to add the status to (required)
            name: The name of the status (required)
            order: Position of the status in the funnel (optional)
            
        Returns:
            dict: Created status object
            
        Example:
            >>> status = await create_funnel_status(
            ...     funnel_id="XSx4OQGb4KvEL7Rq",
            ...     name="Negotiation",
            ...     order=3
            ... )
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            if not name:
                return ToolResult.error("name is required")
            
            payload = {"name": name}
            if order is not None:
                payload["order"] = order
            
            response = await client.post(f"/crm/funnels/{funnel_id}/statuses", payload)
            return ToolResult.success(response, f"Status '{name}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_funnel_status(
        funnel_id: str,
        status_id: str,
        name: Optional[str] = None,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing funnel status.
        
        Updates the specified fields of a funnel status.
        
        Args:
            funnel_id: The funnel ID (required)
            status_id: The unique identifier of the status (required)
            name: New name for the status (optional)
            order: New position in the funnel (optional)
            
        Returns:
            dict: Updated status object
            
        Example:
            >>> result = await update_funnel_status(
            ...     funnel_id="XSx4OQGb4KvEL7Rq",
            ...     status_id="JwPoZuaQ81DdrxyD",
            ...     name="Won Deal",
            ...     order=5
            ... )
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            if not status_id:
                return ToolResult.error("status_id is required")
            
            payload = {}
            if name is not None:
                payload["name"] = name
            if order is not None:
                payload["order"] = order
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/crm/funnels/{funnel_id}/statuses/{status_id}", payload)
            return ToolResult.success(response, f"Status {status_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_funnel_status(
        funnel_id: str,
        status_id: str
    ) -> Dict[str, Any]:
        """
        Delete a status from a funnel.
        
        Removes a status stage. Deals in this status may be
        moved or deleted.
        
        Args:
            funnel_id: The funnel ID (required)
            status_id: The unique identifier of the status to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            Deals in this status may be affected.
            
        Example:
            >>> result = await delete_funnel_status(
            ...     funnel_id="XSx4OQGb4KvEL7Rq",
            ...     status_id="JwPoZuaQ81DdrxyD"
            ... )
        """
        try:
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            if not status_id:
                return ToolResult.error("status_id is required")
            response = await client.delete(f"/crm/funnels/{funnel_id}/statuses/{status_id}")
            return ToolResult.success(response, f"Status {status_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools
