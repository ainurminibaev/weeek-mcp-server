"""
Project tools for Weeek MCP Server.

Provides tools for project management.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_project_tools(server, client) -> int:
    """
    Register project-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_projects(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of all projects in the workspace.
        
        Retrieves all projects with optional filtering by name or status.
        
        Args:
            limit: Maximum number of projects to return (1-100, default: 50)
            offset: Number of projects to skip for pagination (default: 0)
            search: Filter projects by name (optional)
            status: Filter projects by status (optional)
            
        Returns:
            dict: List of projects containing:
                - projects: Array of project objects
                - total: Total number of projects
                
        Example:
            >>> projects = await list_projects(search="Marketing")
            >>> for project in projects["data"]:
            ...     print(project["title"])
        """
        try:
            params = build_query_params(
                limit=limit,
                offset=offset,
                search=search,
                status=status
            )
            response = await client.get("/tm/projects", params)
            return ToolResult.success(response, "Projects list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_project_by_id(project_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.
        
        Retrieves full details of a project including its settings,
        members, and statistics.
        
        Args:
            project_id: The unique identifier of the project (required)
            
        Returns:
            dict: Project information containing:
                - id: Project ID
                - title: Project name
                - description: Project description
                - status: Current status
                - created_at: Creation timestamp
                - updated_at: Last update timestamp
                
        Example:
            >>> project = await get_project_by_id("proj_123")
            >>> print(project["data"]["title"])
        """
        try:
            if not project_id:
                return ToolResult.error("project_id is required")
            response = await client.get(f"/tm/projects/{project_id}")
            return ToolResult.success(response, f"Project {project_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_project(
        title: str,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project in the workspace.
        
        Creates a project that can contain boards, tasks, and other items.
        
        Args:
            title: The name of the project (required, max 255 chars)
            description: Detailed description of the project (optional)
            status: Initial status of the project (optional)
            
        Returns:
            dict: Created project object with all details
            
        Example:
            >>> project = await create_project(
            ...     title="New Marketing Campaign",
            ...     description="Q1 2025 marketing initiatives"
            ... )
            >>> print(project["data"]["id"])
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            if description is not None:
                payload["description"] = description
            if status is not None:
                payload["status"] = status
            
            response = await client.post("/tm/projects", payload)
            return ToolResult.success(response, f"Project '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_project(
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing project.
        
        Updates the specified fields of a project. Only provided
        fields will be updated; others remain unchanged.
        
        Args:
            project_id: The unique identifier of the project (required)
            title: New title for the project (optional)
            description: New description (optional)
            status: New status (optional)
            
        Returns:
            dict: Updated project object
            
        Example:
            >>> result = await update_project(
            ...     project_id="proj_123",
            ...     title="Updated Project Name",
            ...     status="active"
            ... )
        """
        try:
            if not project_id:
                return ToolResult.error("project_id is required")
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if status is not None:
                payload["status"] = status
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/tm/projects/{project_id}", payload)
            return ToolResult.success(response, f"Project {project_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_project(project_id: str) -> Dict[str, Any]:
        """
        Delete a project from the workspace.
        
        Removes a project and all its contents including boards,
        tasks, and other related items.
        
        Args:
            project_id: The unique identifier of the project to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone. All tasks, boards, and
            other items within the project will be permanently deleted.
            
        Example:
            >>> result = await delete_project("proj_123")
            >>> print(result["success"])
            True
        """
        try:
            if not project_id:
                return ToolResult.error("project_id is required")
            response = await client.delete(f"/tm/projects/{project_id}")
            return ToolResult.success(response, f"Project {project_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

