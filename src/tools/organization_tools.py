"""
Organization tools for Weeek MCP Server.

Provides tools for managing organizations in CRM.
"""

from typing import Any, Dict, Optional

from .base import ToolResult, build_query_params


def register_organization_tools(server, client) -> int:
    """
    Register organization-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def list_organizations(
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of all organizations in the CRM.
        
        Retrieves organizations (companies) with optional search.
        
        Args:
            limit: Maximum number of organizations to return (1-100, default: 50)
            offset: Number of organizations to skip for pagination (default: 0)
            search: Search in organization names (optional)
            
        Returns:
            dict: List of organizations containing:
                - organizations: Array of organization objects
                - total: Total number of organizations
                
        Example:
            >>> orgs = await list_organizations(search="Tech")
            >>> for org in orgs["data"]:
            ...     print(org["name"])
        """
        try:
            params = build_query_params(
                limit=limit,
                offset=offset,
                search=search
            )
            response = await client.get("/crm/organizations", params)
            return ToolResult.success(response, "Organizations list retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def get_organization_by_id(organization_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific organization.
        
        Retrieves full details of an organization.
        
        Args:
            organization_id: The unique identifier of the organization (required)
            
        Returns:
            dict: Organization information containing:
                - id: Organization ID
                - name: Organization name
                - description: Description
                - email: Contact email
                - contacts: Associated contacts
                
        Example:
            >>> org = await get_organization_by_id("org_123")
            >>> print(org["data"]["name"])
        """
        try:
            if not organization_id:
                return ToolResult.error("organization_id is required")
            response = await client.get(f"/crm/organizations/{organization_id}")
            return ToolResult.success(response, f"Organization {organization_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def create_organization(
        name: str,
        description: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new organization in the CRM.
        
        Creates an organization (company) for tracking contacts and deals.
        
        Args:
            name: The name of the organization (required)
            description: Description of the organization (optional)
            email: Contact email for the organization (optional)
            
        Returns:
            dict: Created organization object
            
        Example:
            >>> org = await create_organization(
            ...     name="Acme Corporation",
            ...     description="Technology company",
            ...     email="info@acme.com"
            ... )
        """
        try:
            if not name:
                return ToolResult.error("name is required")
            
            payload = {"name": name}
            if description is not None:
                payload["description"] = description
            if email is not None:
                payload["email"] = email
            
            response = await client.post("/crm/organizations", payload)
            return ToolResult.success(response, f"Organization '{name}' created successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def update_organization(
        organization_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing organization.
        
        Updates the specified fields of an organization.
        
        Args:
            organization_id: The unique identifier of the organization (required)
            name: New name for the organization (optional)
            description: New description (optional)
            email: New email address (optional)
            
        Returns:
            dict: Updated organization object
            
        Example:
            >>> result = await update_organization(
            ...     organization_id="org_123",
            ...     name="Acme Inc.",
            ...     email="contact@acme.com"
            ... )
        """
        try:
            if not organization_id:
                return ToolResult.error("organization_id is required")
            
            payload = {}
            if name is not None:
                payload["name"] = name
            if description is not None:
                payload["description"] = description
            if email is not None:
                payload["email"] = email
            
            if not payload:
                return ToolResult.error("At least one field to update is required")
            
            response = await client.put(f"/crm/organizations/{organization_id}", payload)
            return ToolResult.success(response, f"Organization {organization_id} updated successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_organization(organization_id: str) -> Dict[str, Any]:
        """
        Delete an organization from the CRM.
        
        Removes an organization. Associated contacts may be
        unlinked but not deleted.
        
        Args:
            organization_id: The unique identifier of the organization to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Example:
            >>> result = await delete_organization("org_123")
        """
        try:
            if not organization_id:
                return ToolResult.error("organization_id is required")
            response = await client.delete(f"/crm/organizations/{organization_id}")
            return ToolResult.success(response, f"Organization {organization_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 5  # Number of registered tools

