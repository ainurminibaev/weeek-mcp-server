"""
Board Column tools for Weeek MCP Server.

Provides tools for managing board columns.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_board_column_tools(server, client) -> int:
    """
    Register board column-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_board_columns(
        board_id: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of columns for a specific board.
        
        Retrieves all columns for the specified board.
        
        Args:
            board_id: The board ID to get columns from (required)
            limit: Maximum number of columns to return (1-100, default: 50)
            offset: Number of columns to skip for pagination (default: 0)
            
        Returns:
            dict: List of columns containing:
                - boardColumns: Array of column objects with id, name, order
                - total: Total number of columns
                
        Example:
            >>> columns = await list_board_columns(board_id="10")
            >>> for col in columns["data"]["boardColumns"]:
            ...     print(f"{col['order']}: {col['name']}")
        """
        try:
            if not board_id:
                return ToolResult.error("board_id is required")
            
            params = {"boardId": board_id}
            if limit:
                params["limit"] = limit
            if offset:
                params["offset"] = offset
            
            response = await client.get("/tm/board-columns", params)
            return ToolResult.success(response, "Board columns list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_board_column_by_id(column_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific board column.
        
        Retrieves full details of a column including its tasks.
        
        Args:
            column_id: The unique identifier of the column (required)
            
        Returns:
            dict: Column information containing:
                - id: Column ID
                - title: Column name
                - board_id: Parent board ID
                - order: Column position
                
        Example:
            >>> column = await get_board_column_by_id("col_123")
            >>> print(column["data"]["title"])
        """
        try:
            if not column_id:
                return ToolResult.error("column_id is required")
            response = await client.get(f"/tm/board-columns/{column_id}")
            return ToolResult.success(response, f"Board column {column_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_board_column(
        title: str,
        board_id: str,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new column on a board.
        
        Creates a column that can contain tasks on a Kanban board.
        
        Args:
            title: The name of the column (required, max 255 chars)
            board_id: ID of the board to create the column on (required)
            order: Position of the column (optional, auto-assigned if not provided)
            
        Returns:
            dict: Created column object with all details
            
        Example:
            >>> column = await create_board_column(
            ...     title="In Progress",
            ...     board_id="board_123",
            ...     order=2
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            if not board_id:
                return ToolResult.error("board_id is required")
            
            payload = {
                "title": title,
                "board_id": board_id
            }
            if order is not None:
                payload["order"] = order
            
            response = await client.post("/tm/board-columns", payload)
            return ToolResult.success(response, f"Column '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_board_column(
        column_id: str,
        title: Optional[str] = None,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing board column.
        
        Updates the specified fields of a column.
        
        Args:
            column_id: The unique identifier of the column (required)
            title: New title for the column (optional)
            order: New position for the column (optional)
            
        Returns:
            dict: Updated column object
            
        Example:
            >>> result = await update_board_column(
            ...     column_id="col_123",
            ...     title="Done",
            ...     order=4
            ... )
        """
        try:
            if not column_id:
                return ToolResult.error("column_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if order is not None:
                payload["order"] = order
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/tm/board-columns/{column_id}", payload)
            return ToolResult.success(response, f"Column {column_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_board_column(column_id: str) -> Dict[str, Any]:
        """
        Delete a column from a board.
        
        Removes a column. Tasks in the column may be moved
        or deleted depending on settings.
        
        Args:
            column_id: The unique identifier of the column to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            Tasks in this column may be deleted or moved depending
            on board settings.
            
        Example:
            >>> result = await delete_board_column("col_123")
        """
        try:
            if not column_id:
                return ToolResult.error("column_id is required")
            response = await client.delete(f"/tm/board-columns/{column_id}")
            return ToolResult.success(response, f"Column {column_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

