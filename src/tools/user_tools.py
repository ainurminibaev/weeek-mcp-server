"""
User tools for Weeek MCP Server.

Provides tools for user management and information retrieval.
"""

from typing import Any, Dict, Optional

from .base import handle_api_errors, ToolResult, build_query_params


def register_user_tools(server, client) -> int:
    """
    Register user-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_workspace_members(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all members in the workspace.
        
        Retrieves all members who have access to the current workspace,
        with optional pagination.
        
        Args:
            limit: Maximum number of members to return (1-100, default: 50)
            offset: Number of members to skip for pagination (default: 0)
            
        Returns:
            dict: List of members with pagination info containing:
                - members: Array of member objects with id, email, name, role
                - total: Total number of members
                
        Example:
            >>> members = await list_workspace_members(limit=10)
            >>> for member in members["data"]["members"]:
            ...     print(member["name"])
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/ws/members", params)
            return ToolResult.success(response, "Workspace members list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_member_by_id(member_id: str) -> Dict[str, Any]:
        """
        Get information about a specific workspace member by their ID.
        
        Retrieves detailed information about a member in the workspace.
        
        Args:
            member_id: The unique identifier of the member to retrieve
            
        Returns:
            dict: Member information containing:
                - id: Member ID
                - email: Member email
                - name: Display name
                - role: Member role
                
        Example:
            >>> member = await get_member_by_id("123")
            >>> print(member["data"]["name"])
        """
        try:
            if not member_id:
                return ToolResult.error("member_id is required")
            response = await client.get(f"/ws/members/{member_id}")
            return ToolResult.success(response, f"Member {member_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_member(
        member_id: str,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a workspace member's information.
        
        Updates the specified fields of a member. Only workspace admins
        can update member roles.
        
        Args:
            member_id: The unique identifier of the member (required)
            role: New role for the member (optional)
            
        Returns:
            dict: Updated member object
            
        Example:
            >>> result = await update_member(
            ...     member_id="123",
            ...     role="admin"
            ... )
        """
        try:
            if not member_id:
                return ToolResult.error("member_id is required")
            
            payload = {}
            if role is not None:
                payload["role"] = role
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/ws/members/{member_id}", payload)
            return ToolResult.success(response, f"Member {member_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_member(member_id: str) -> Dict[str, Any]:
        """
        Remove a member from the workspace.
        
        Removes a member's access to the workspace. Only workspace
        admins can remove members.
        
        Args:
            member_id: The unique identifier of the member to remove (required)
            
        Returns:
            dict: Confirmation of removal
            
        Warning:
            This action will revoke the member's access to the workspace.
            
        Example:
            >>> result = await delete_member("123")
        """
        try:
            if not member_id:
                return ToolResult.error("member_id is required")
            response = await client.delete(f"/ws/members/{member_id}")
            return ToolResult.success(response, f"Member {member_id} removed successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 4  # Number of registered tools

