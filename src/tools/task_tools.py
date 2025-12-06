"""
Task tools for Weeek MCP Server.

Provides comprehensive tools for task management - the core functionality.
"""

from typing import Any, Dict, Optional, List

from .base import ToolResult, build_query_params


def register_task_tools(server, client) -> int:
    """
    Register task-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_tasks(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        project_id: Optional[str] = None,
        board_id: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[str] = None,
        priority: Optional[str] = None,
        due_date_from: Optional[str] = None,
        due_date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of tasks with various filters.
        
        Retrieves tasks from the workspace with optional filtering
        by project, board, status, assignee, and more.
        
        Args:
            limit: Maximum number of tasks to return (1-100, default: 50)
            offset: Number of tasks to skip for pagination (default: 0)
            project_id: Filter by project ID (optional)
            board_id: Filter by board ID (optional)
            status: Filter by task status (optional)
            assigned_to: Filter by assignee user ID (optional)
            search: Search in task titles (optional)
            tags: Filter by tag IDs (comma-separated) (optional)
            priority: Filter by priority (low, medium, high, urgent) (optional)
            due_date_from: Filter tasks due after this date (ISO8601) (optional)
            due_date_to: Filter tasks due before this date (ISO8601) (optional)
            
        Returns:
            dict: List of tasks containing:
                - tasks: Array of task objects
                - total: Total number of matching tasks
                
        Example:
            >>> tasks = await list_tasks(
            ...     project_id="proj_123",
            ...     status="open",
            ...     priority="high",
            ...     limit=20
            ... )
            >>> for task in tasks["data"]:
            ...     print(f"{task['title']} - {task['priority']}")
        """
        try:
            params = build_query_params(
                limit=limit,
                offset=offset,
                project_id=project_id,
                board_id=board_id,
                status=status,
                assigned_to=assigned_to,
                search=search,
                tags=tags,
                priority=priority,
                due_date_from=due_date_from,
                due_date_to=due_date_to
            )
            response = await client.get("/tm/tasks", params)
            return ToolResult.success(response, "Tasks list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_task_by_id(task_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific task.
        
        Retrieves full details of a task including description,
        attachments, comments, custom fields, and activity.
        
        Args:
            task_id: The unique identifier of the task (required)
            
        Returns:
            dict: Task information containing:
                - id: Task ID
                - title: Task title
                - description: Full description
                - status: Current status
                - priority: Task priority
                - due_date: Due date
                - assigned_to: Assignee user ID
                - project_id: Parent project ID
                - board_id: Board ID (if on a board)
                - column_id: Column ID (if on a board)
                - tags: Array of tag IDs
                - custom_fields: Custom field values
                - created_at: Creation timestamp
                - updated_at: Last update timestamp
                
        Example:
            >>> task = await get_task_by_id("task_123")
            >>> print(f"{task['data']['title']}: {task['data']['status']}")
        """
        try:
            if not task_id:
                return ToolResult.error("task_id is required")
            response = await client.get(f"/tm/tasks/{task_id}")
            return ToolResult.success(response, f"Task {task_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_task(
        title: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        board_id: Optional[str] = None,
        column_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new task in Weeek.
        
        Creates a task with the specified properties. The task can be
        assigned to a project and optionally placed on a Kanban board.
        
        Args:
            title: Task title (required, max 255 chars)
            project_id: ID of the project (recommended for organization)
            description: Detailed task description (optional)
            board_id: Board ID for Kanban placement (optional)
            column_id: Column ID within the board (optional)
            assigned_to: User ID to assign the task to (optional)
            priority: Task priority - one of: low, medium, high, urgent (optional)
            due_date: Due date in ISO8601 format YYYY-MM-DD (optional)
            tags: List of tag IDs to apply (optional)
            custom_fields: Dictionary of custom field values (optional)
            
        Returns:
            dict: Created task object with all details including:
                - id: Unique task identifier
                - title: Task title
                - status: Initial status (usually "open")
                - created_at: Creation timestamp
                
        Example:
            >>> task = await create_task(
            ...     title="Review API Documentation",
            ...     project_id="proj_123",
            ...     priority="high",
            ...     due_date="2025-12-15",
            ...     assigned_to="user_456"
            ... )
            >>> print(f"Created task: {task['data']['id']}")
            
        Example with tags:
            >>> task = await create_task(
            ...     title="Fix login bug",
            ...     project_id="proj_123",
            ...     priority="urgent",
            ...     tags=["tag_bug", "tag_security"]
            ... )
        """
        try:
            if not title:
                return ToolResult.error("title is required")
            
            payload = {"title": title}
            
            # API uses camelCase for field names
            if project_id is not None:
                payload["projectId"] = project_id
            if description is not None:
                payload["description"] = description
            if board_id is not None:
                payload["boardId"] = board_id
            if column_id is not None:
                payload["boardColumnId"] = column_id
            if assigned_to is not None:
                payload["userId"] = assigned_to
            if priority is not None:
                if priority not in ["low", "medium", "high", "urgent"]:
                    return ToolResult.error(
                        "priority must be one of: low, medium, high, urgent"
                    )
                payload["priority"] = priority
            if due_date is not None:
                payload["dueDate"] = due_date
            if tags is not None:
                payload["tags"] = tags
            if custom_fields is not None:
                payload["customFields"] = custom_fields
            
            response = await client.post("/tm/tasks", payload)
            return ToolResult.success(response, f"Task '{title}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_task(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        assigned_to: Optional[str] = None,
        column_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Updates the specified fields of a task. Only provided fields
        will be updated; others remain unchanged.
        
        Args:
            task_id: The unique identifier of the task (required)
            title: New task title (optional)
            description: New description (optional)
            status: New status (optional)
            priority: New priority - one of: low, medium, high, urgent (optional)
            due_date: New due date in ISO8601 format YYYY-MM-DD (optional)
            assigned_to: New assignee user ID (optional)
            column_id: Move task to a different column (optional)
            tags: New list of tag IDs (replaces existing tags) (optional)
            
        Returns:
            dict: Updated task object with all details
            
        Example:
            >>> result = await update_task(
            ...     task_id="task_123",
            ...     status="in_progress",
            ...     priority="high"
            ... )
            
        Example - move task to different column:
            >>> result = await update_task(
            ...     task_id="task_123",
            ...     column_id="col_done"
            ... )
        """
        try:
            if not task_id:
                return ToolResult.error("task_id is required")
            
            payload = {}
            # API uses camelCase for field names
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if status is not None:
                payload["status"] = status
            if priority is not None:
                if priority not in ["low", "medium", "high", "urgent"]:
                    return ToolResult.error(
                        "priority must be one of: low, medium, high, urgent"
                    )
                payload["priority"] = priority
            if due_date is not None:
                payload["dueDate"] = due_date
            if assigned_to is not None:
                payload["userId"] = assigned_to
            if column_id is not None:
                payload["boardColumnId"] = column_id
            if tags is not None:
                payload["tags"] = tags
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/tm/tasks/{task_id}", payload)
            return ToolResult.success(response, f"Task {task_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_task(task_id: str) -> Dict[str, Any]:
        """
        Delete a task.
        
        Permanently removes a task from the workspace.
        
        Args:
            task_id: The unique identifier of the task to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone. The task and all its
            attachments, comments will be permanently deleted.
            
        Example:
            >>> result = await delete_task("task_123")
            >>> print(result["success"])
            True
        """
        try:
            if not task_id:
                return ToolResult.error("task_id is required")
            response = await client.delete(f"/tm/tasks/{task_id}")
            return ToolResult.success(response, f"Task {task_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def search_task_in_project(
        project_id: str,
        q: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Search for tasks within a specific project.
        
        Searches task titles and descriptions within the specified project.
        
        Args:
            project_id: The project ID to search within (required)
            q: Search query text (required)
            limit: Maximum number of results (1-100, default: 50)
            offset: Number of results to skip (default: 0)
            
        Returns:
            dict: Search results containing:
                - tasks: Array of matching task objects
                - total: Total number of matches
                
        Example:
            >>> results = await search_task_in_project(
            ...     project_id="proj_123",
            ...     q="bug fix"
            ... )
            >>> print(f"Found {len(results['data'])} tasks")
        """
        try:
            if not project_id:
                return ToolResult.error("project_id is required")
            if not q:
                return ToolResult.error("q (search query) is required")
            
            params = build_query_params(
                project_id=project_id,
                q=q,
                limit=limit,
                offset=offset
            )
            response = await client.get("/tm/tasks/search", params)
            return ToolResult.success(response, f"Search completed in project {project_id}")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def search_task_global(
        q: str,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Search for tasks across the entire workspace.
        
        Performs a global search across all projects and boards
        in the workspace.
        
        Args:
            q: Search query text (required)
            limit: Maximum number of results (1-100, default: 50)
            offset: Number of results to skip (default: 0)
            
        Returns:
            dict: Search results containing:
                - tasks: Array of matching task objects from all projects
                - total: Total number of matches
                
        Example:
            >>> results = await search_task_global(q="urgent meeting")
            >>> for task in results["data"]:
            ...     print(f"{task['title']} ({task['project_id']})")
        """
        try:
            if not q:
                return ToolResult.error("q (search query) is required")
            
            params = build_query_params(
                q=q,
                limit=limit,
                offset=offset
            )
            response = await client.get("/tm/tasks/search/global", params)
            return ToolResult.success(response, "Global search completed")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 7  # Number of registered tools

