"""
Board tools for Weeek MCP Server.

Provides tools for managing Kanban boards.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_board_tools(server, client) -> int:
    """
    Register board-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_boards(
        project_id: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all boards for a specific project.
        
        Retrieves all Kanban boards in the specified project.
        
        Args:
            project_id: The project ID to get boards from (required)
            limit: Maximum number of boards to return (1-100, default: 50)
            offset: Number of boards to skip for pagination (default: 0)
            
        Returns:
            dict: List of boards containing:
                - boards: Array of board objects
                - total: Total number of boards
                
        Example:
            >>> boards = await list_boards(project_id="7")
            >>> for board in boards["data"]["boards"]:
            ...     print(board["name"])
        """
        try:
            if not project_id:
                return ToolResult.error("project_id is required")
            
            params = {"projectId": project_id}
            if limit:
                params["limit"] = limit
            if offset:
                params["offset"] = offset
            
            response = await client.get("/tm/boards", params)
            return ToolResult.success(response, "Boards list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_board_by_id(board_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific board.
        
        Retrieves full details of a board including its columns and settings.
        
        Args:
            board_id: The unique identifier of the board (required)
            
        Returns:
            dict: Board information containing:
                - id: Board ID
                - title: Board name
                - project_id: Parent project ID
                - type: Board type (e.g., kanban)
                - columns: Array of column objects
                
        Example:
            >>> board = await get_board_by_id("board_123")
            >>> print(board["data"]["title"])
        """
        try:
            if not board_id:
                return ToolResult.error("board_id is required")
            response = await client.get(f"/tm/boards/{board_id}")
            return ToolResult.success(response, f"Board {board_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_board(
        title: str,
        project_id: Optional[str] = None,
        board_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new board in the workspace.
        
        Creates a Kanban board that can contain columns and tasks.
        
        Args:
            title: The name of the board (required, max 255 chars)
            project_id: ID of the project to create the board in (optional)
            board_type: Type of board, e.g., 'kanban' (optional)
            
        Returns:
            dict: Created board object with all details
            
        Example:
            >>> board = await create_board(
            ...     title="Development Sprint",
            ...     project_id="proj_123",
            ...     board_type="kanban"
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            if project_id is not None:
                payload["project_id"] = project_id
            if board_type is not None:
                payload["type"] = board_type
            
            response = await client.post("/tm/boards", payload)
            return ToolResult.success(response, f"Board '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_board(
        board_id: str,
        title: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing board.
        
        Updates the specified fields of a board.
        
        Args:
            board_id: The unique identifier of the board (required)
            title: New title for the board (optional)
            project_id: Move board to a different project (optional)
            
        Returns:
            dict: Updated board object
            
        Example:
            >>> result = await update_board(
            ...     board_id="board_123",
            ...     title="Updated Board Name"
            ... )
        """
        try:
            if not board_id:
                return ToolResult.error("board_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if project_id is not None:
                payload["project_id"] = project_id
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/tm/boards/{board_id}", payload)
            return ToolResult.success(response, f"Board {board_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_board(board_id: str) -> Dict[str, Any]:
        """
        Delete a board from the workspace.
        
        Removes a board and all its columns. Tasks may be moved
        or deleted depending on settings.
        
        Args:
            board_id: The unique identifier of the board to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone. All columns within
            the board will be deleted.
            
        Example:
            >>> result = await delete_board("board_123")
        """
        try:
            if not board_id:
                return ToolResult.error("board_id is required")
            response = await client.delete(f"/tm/boards/{board_id}")
            return ToolResult.success(response, f"Board {board_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

