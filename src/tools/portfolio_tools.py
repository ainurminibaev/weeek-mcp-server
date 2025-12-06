"""
Portfolio tools for Weeek MCP Server.

Provides tools for portfolio management.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_portfolio_tools(server, client) -> int:
    """
    Register portfolio-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_portfolio(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all portfolios in the workspace.
        
        Retrieves all portfolios which are collections of related projects.
        
        Args:
            limit: Maximum number of portfolios to return (1-100, default: 50)
            offset: Number of portfolios to skip for pagination (default: 0)
            
        Returns:
            dict: List of portfolios containing:
                - portfolios: Array of portfolio objects
                - total: Total number of portfolios
                
        Example:
            >>> portfolios = await list_portfolio()
            >>> for portfolio in portfolios["data"]:
            ...     print(portfolio["title"])
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/tm/portfolios", params)
            return ToolResult.success(response, "Portfolio list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_portfolio_by_id(portfolio_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific portfolio.
        
        Retrieves full details of a portfolio including its projects.
        
        Args:
            portfolio_id: The unique identifier of the portfolio (required)
            
        Returns:
            dict: Portfolio information containing:
                - id: Portfolio ID
                - title: Portfolio name
                - description: Portfolio description
                - projects: Array of project IDs in the portfolio
                
        Example:
            >>> portfolio = await get_portfolio_by_id("port_123")
            >>> print(portfolio["data"]["title"])
        """
        try:
            if not portfolio_id:
                return ToolResult.error("portfolio_id is required")
            response = await client.get(f"/tm/portfolios/{portfolio_id}")
            return ToolResult.success(response, f"Portfolio {portfolio_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_portfolio(
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new portfolio in the workspace.
        
        Creates a portfolio to group related projects together.
        
        Args:
            title: The name of the portfolio (required)
            description: Description of the portfolio (optional)
            
        Returns:
            dict: Created portfolio object
            
        Example:
            >>> portfolio = await create_portfolio(
            ...     title="Q1 2025 Initiatives",
            ...     description="All projects for Q1"
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            if description is not None:
                payload["description"] = description
            
            response = await client.post("/tm/portfolios", payload)
            return ToolResult.success(response, f"Portfolio '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_portfolio(
        portfolio_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing portfolio.
        
        Updates the specified fields of a portfolio.
        
        Args:
            portfolio_id: The unique identifier of the portfolio (required)
            title: New title for the portfolio (optional)
            description: New description (optional)
            
        Returns:
            dict: Updated portfolio object
            
        Example:
            >>> result = await update_portfolio(
            ...     portfolio_id="port_123",
            ...     title="Updated Portfolio Name"
            ... )
        """
        try:
            if not portfolio_id:
                return ToolResult.error("portfolio_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/tm/portfolios/{portfolio_id}", payload)
            return ToolResult.success(response, f"Portfolio {portfolio_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_portfolio(portfolio_id: str) -> Dict[str, Any]:
        """
        Delete a portfolio from the workspace.
        
        Removes a portfolio. Projects within the portfolio will
        not be deleted, only ungrouped.
        
        Args:
            portfolio_id: The unique identifier of the portfolio to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Example:
            >>> result = await delete_portfolio("port_123")
        """
        try:
            if not portfolio_id:
                return ToolResult.error("portfolio_id is required")
            response = await client.delete(f"/tm/portfolios/{portfolio_id}")
            return ToolResult.success(response, f"Portfolio {portfolio_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

