"""
Contact tools for Weeek MCP Server.

Provides tools for managing contacts in CRM.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_contact_tools(server, client) -> int:
    """
    Register contact-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_contacts(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        search: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of all contacts in the CRM.
        
        Retrieves contacts (people) with optional filtering.
        
        Args:
            limit: Maximum number of contacts to return (1-100, default: 50)
            offset: Number of contacts to skip for pagination (default: 0)
            search: Search in contact names (optional)
            organization_id: Filter contacts by organization (optional)
            
        Returns:
            dict: List of contacts containing:
                - contacts: Array of contact objects
                - total: Total number of contacts
                
        Example:
            >>> contacts = await list_contacts(
            ...     organization_id="org_123",
            ...     limit=20
            ... )
            >>> for contact in contacts["data"]:
            ...     print(f"{contact['first_name']} {contact['last_name']}")
        """
        try:
            params = build_query_params(
                limit=limit,
                offset=offset,
                search=search,
                organization_id=organization_id
            )
            response = await client.get("/crm/contacts", params)
            return ToolResult.success(response, "Contacts list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_contact_by_id(contact_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific contact.
        
        Retrieves full details of a contact including deals.
        
        Args:
            contact_id: The unique identifier of the contact (required)
            
        Returns:
            dict: Contact information containing:
                - id: Contact ID
                - first_name: First name
                - last_name: Last name
                - email: Email address
                - phone: Phone number
                - organization_id: Associated organization
                - deals: Associated deals
                
        Example:
            >>> contact = await get_contact_by_id("contact_123")
            >>> print(f"{contact['data']['first_name']} {contact['data']['last_name']}")
        """
        try:
            if not contact_id:
                return ToolResult.error("contact_id is required")
            response = await client.get(f"/crm/contacts/{contact_id}")
            return ToolResult.success(response, f"Contact {contact_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_contact(
        first_name: str,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new contact in the CRM.
        
        Creates a contact (person) for tracking relationships and deals.
        
        Args:
            first_name: First name of the contact (required)
            last_name: Last name of the contact (optional)
            email: Email address (optional)
            phone: Phone number (optional)
            organization_id: ID of the associated organization (optional)
            
        Returns:
            dict: Created contact object
            
        Example:
            >>> contact = await create_contact(
            ...     first_name="John",
            ...     last_name="Doe",
            ...     email="john@example.com",
            ...     phone="+1234567890",
            ...     organization_id="org_123"
            ... )
        """
        try:
            if not first_name:
                return ToolResult.error("first_name is required")
            
            payload = {"first_name": first_name}
            if last_name is not None:
                payload["last_name"] = last_name
            if email is not None:
                payload["email"] = email
            if phone is not None:
                payload["phone"] = phone
            if organization_id is not None:
                payload["organization_id"] = organization_id
            
            response = await client.post("/crm/contacts", payload)
            return ToolResult.success(response, f"Contact '{first_name}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_contact(
        contact_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing contact.
        
        Updates the specified fields of a contact.
        
        Args:
            contact_id: The unique identifier of the contact (required)
            first_name: New first name (optional)
            last_name: New last name (optional)
            email: New email address (optional)
            phone: New phone number (optional)
            organization_id: New organization ID (optional)
            
        Returns:
            dict: Updated contact object
            
        Example:
            >>> result = await update_contact(
            ...     contact_id="contact_123",
            ...     email="new.email@example.com",
            ...     phone="+1987654321"
            ... )
        """
        try:
            if not contact_id:
                return ToolResult.error("contact_id is required")
            
            payload = {}
            if first_name is not None:
                payload["first_name"] = first_name
            if last_name is not None:
                payload["last_name"] = last_name
            if email is not None:
                payload["email"] = email
            if phone is not None:
                payload["phone"] = phone
            if organization_id is not None:
                payload["organization_id"] = organization_id
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/crm/contacts/{contact_id}", payload)
            return ToolResult.success(response, f"Contact {contact_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_contact(contact_id: str) -> Dict[str, Any]:
        """
        Delete a contact from the CRM.
        
        Permanently removes a contact.
        
        Args:
            contact_id: The unique identifier of the contact to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            Associated deals will be unlinked but not deleted.
            
        Example:
            >>> result = await delete_contact("contact_123")
        """
        try:
            if not contact_id:
                return ToolResult.error("contact_id is required")
            response = await client.delete(f"/crm/contacts/{contact_id}")
            return ToolResult.success(response, f"Contact {contact_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

