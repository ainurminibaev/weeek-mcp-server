"""
Currency tools for Weeek MCP Server.

Provides tools for retrieving available currencies.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_currency_tools(server, client) -> int:
    """
    Register currency-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_currencies(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all available currencies.
        
        Retrieves all currencies that can be used for deals
        and financial operations in the workspace.
        
        Args:
            limit: Maximum number of currencies to return (1-100, default: 50)
            offset: Number of currencies to skip for pagination (default: 0)
            
        Returns:
            dict: List of currencies containing:
                - currencies: Array of currency objects with code and name
                - total: Total number of currencies
                
        Example:
            >>> currencies = await list_currencies()
            >>> for curr in currencies["data"]:
            ...     print(f"{curr['code']}: {curr['name']}")
            "USD: US Dollar"
            "EUR: Euro"
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/crm/currencies", params)
            return ToolResult.success(response, "Currencies list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 1  # Number of registered tools

