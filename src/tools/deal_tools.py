"""
Deal tools for Weeek MCP Server.

Provides tools for managing deals in sales funnels.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_deal_tools(server, client) -> int:
    """
    Register deal-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_deals(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        funnel_id: Optional[str] = None,
        status_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of deals with optional filtering.
        
        Retrieves deals from the CRM with filtering options.
        
        Args:
            limit: Maximum number of deals to return (1-100, default: 50)
            offset: Number of deals to skip for pagination (default: 0)
            funnel_id: Filter by funnel ID (optional)
            status_id: Filter by status ID (optional)
            search: Search in deal titles (optional)
            
        Returns:
            dict: List of deals containing:
                - deals: Array of deal objects
                - total: Total number of deals
                
        Example:
            >>> deals = await list_deals(
            ...     funnel_id="funnel_sales",
            ...     status_id="status_negotiation"
            ... )
            >>> for deal in deals["data"]:
            ...     print(f"{deal['title']}: ${deal['amount']}")
        """
        try:
            params = build_query_params(
                limit=limit,
                offset=offset,
                funnel_id=funnel_id,
                status_id=status_id,
                search=search
            )
            response = await client.get("/deals", params)
            return ToolResult.success(response, "Deals list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_deal_by_id(deal_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific deal.
        
        Retrieves full details of a deal including contact and value.
        
        Args:
            deal_id: The unique identifier of the deal (required)
            
        Returns:
            dict: Deal information containing:
                - id: Deal ID
                - title: Deal name
                - funnel_id: Funnel ID
                - status_id: Current status
                - amount: Deal value
                - currency: Currency code
                - contact_id: Associated contact
                
        Example:
            >>> deal = await get_deal_by_id("deal_123")
            >>> print(f"{deal['data']['title']}: {deal['data']['amount']}")
        """
        try:
            if not deal_id:
                return ToolResult.error("deal_id is required")
            response = await client.get(f"/deals/{deal_id}")
            return ToolResult.success(response, f"Deal {deal_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_deal(
        title: str,
        funnel_id: str,
        status_id: str,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        contact_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new deal in a sales funnel.
        
        Creates a deal to track a sales opportunity.
        
        Args:
            title: The name of the deal (required)
            funnel_id: ID of the funnel to create the deal in (required)
            status_id: ID of the initial status/stage (required)
            amount: Deal value/amount (optional)
            currency: Currency code, e.g., "USD", "EUR" (optional)
            contact_id: ID of the associated contact (optional)
            
        Returns:
            dict: Created deal object
            
        Example:
            >>> deal = await create_deal(
            ...     title="Enterprise License",
            ...     funnel_id="funnel_123",
            ...     status_id="status_new",
            ...     amount=50000,
            ...     currency="USD",
            ...     contact_id="contact_456"
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            if not funnel_id:
                return ToolResult.error("funnel_id is required")
            if not status_id:
                return ToolResult.error("status_id is required")
            
            payload = {
                "title": title,
                "funnel_id": funnel_id,
                "status_id": status_id
            }
            if amount is not None:
                payload["amount"] = amount
            if currency is not None:
                payload["currency"] = currency
            if contact_id is not None:
                payload["contact_id"] = contact_id
            
            response = await client.post("/deals", payload)
            return ToolResult.success(response, f"Deal '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_deal(
        deal_id: str,
        title: Optional[str] = None,
        status_id: Optional[str] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        contact_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing deal.
        
        Updates the specified fields of a deal. Use status_id
        to move the deal to a different stage.
        
        Args:
            deal_id: The unique identifier of the deal (required)
            title: New title for the deal (optional)
            status_id: Move deal to a different status (optional)
            amount: Updated deal value (optional)
            currency: Updated currency code (optional)
            contact_id: Updated contact ID (optional)
            
        Returns:
            dict: Updated deal object
            
        Example - move deal to won status:
            >>> result = await update_deal(
            ...     deal_id="deal_123",
            ...     status_id="status_won"
            ... )
            
        Example - update deal value:
            >>> result = await update_deal(
            ...     deal_id="deal_123",
            ...     amount=75000
            ... )
        """
        try:
            if not deal_id:
                return ToolResult.error("deal_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if status_id is not None:
                payload["status_id"] = status_id
            if amount is not None:
                payload["amount"] = amount
            if currency is not None:
                payload["currency"] = currency
            if contact_id is not None:
                payload["contact_id"] = contact_id
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/deals/{deal_id}", payload)
            return ToolResult.success(response, f"Deal {deal_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_deal(deal_id: str) -> Dict[str, Any]:
        """
        Delete a deal from the CRM.
        
        Permanently removes a deal from the funnel.
        
        Args:
            deal_id: The unique identifier of the deal to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone.
            
        Example:
            >>> result = await delete_deal("deal_123")
        """
        try:
            if not deal_id:
                return ToolResult.error("deal_id is required")
            response = await client.delete(f"/deals/{deal_id}")
            return ToolResult.success(response, f"Deal {deal_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

