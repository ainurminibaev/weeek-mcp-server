"""
Custom Field tools for Weeek MCP Server.

Provides tools for managing custom fields in the workspace.
"""

from typing import Any, Dict, Optional, List

from .base import ToolResult, build_query_params


def register_custom_field_tools(server, client) -> int:
    """
    Register custom field-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_custom_fields(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get a list of all custom fields in the workspace.
        
        Retrieves all custom fields that can be used to add
        additional data to tasks and other items.
        
        Args:
            limit: Maximum number of fields to return (1-100, default: 50)
            offset: Number of fields to skip for pagination (default: 0)
            
        Returns:
            dict: List of custom fields containing:
                - fields: Array of custom field objects
                - total: Total number of custom fields
                
        Example:
            >>> fields = await list_custom_fields()
            >>> for field in fields["data"]:
            ...     print(f"{field['name']}: {field['type']}")
        """
        try:
            params = build_query_params(limit=limit, offset=offset)
            response = await client.get("/crm/custom-fields", params)
            return ToolResult.success(response, "Custom fields list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_custom_field(
        name: str,
        field_type: str,
        options: Optional[List[str]] = None,
        required: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Create a new custom field in the workspace.
        
        Creates a custom field that can be used to add additional
        data to tasks. Supported types include text, number, date,
        dropdown, checkbox, etc.
        
        Args:
            name: The name of the custom field (required)
            field_type: Type of the field (e.g., 'text', 'number', 'date', 'dropdown')
            options: List of options for dropdown fields (optional)
            required: Whether the field is required (default: False)
            
        Returns:
            dict: Created custom field object
            
        Example:
            >>> field = await create_custom_field(
            ...     name="Priority Level",
            ...     field_type="dropdown",
            ...     options=["Low", "Medium", "High"]
            ... )
        """
        try:
            if not name:
                return ToolResult.error("name is required")
            if not field_type:
                return ToolResult.error("field_type is required")
            
            payload = {
                "name": name,
                "type": field_type,
            }
            if options is not None:
                payload["options"] = options
            if required is not None:
                payload["required"] = required
            
            response = await client.post("/crm/custom-fields", payload)
            return ToolResult.success(response, f"Custom field '{name}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_custom_field(
        field_id: str,
        name: Optional[str] = None,
        options: Optional[List[str]] = None,
        required: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing custom field.
        
        Updates the specified properties of a custom field.
        Only provided fields will be updated.
        
        Args:
            field_id: The unique identifier of the custom field (required)
            name: New name for the field (optional)
            options: New options for dropdown fields (optional)
            required: Whether the field is required (optional)
            
        Returns:
            dict: Updated custom field object
            
        Example:
            >>> result = await update_custom_field(
            ...     field_id="field_123",
            ...     name="Updated Field Name"
            ... )
        """
        try:
            if not field_id:
                return ToolResult.error("field_id is required")
            
            payload = {}
            if name is not None:
                payload["name"] = name
            if options is not None:
                payload["options"] = options
            if required is not None:
                payload["required"] = required
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/crm/custom-fields/{field_id}", payload)
            return ToolResult.success(response, f"Custom field {field_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_custom_field(field_id: str) -> Dict[str, Any]:
        """
        Delete a custom field from the workspace.
        
        Removes a custom field. Data stored in this field on
        existing tasks will be lost.
        
        Args:
            field_id: The unique identifier of the custom field to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone. All data stored in this
            field on tasks will be permanently deleted.
            
        Example:
            >>> result = await delete_custom_field("field_123")
        """
        try:
            if not field_id:
                return ToolResult.error("field_id is required")
            response = await client.delete(f"/crm/custom-fields/{field_id}")
            return ToolResult.success(response, f"Custom field {field_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 4  # Number of registered tools

