"""
Attachment tools for Weeek MCP Server.

Provides tools for managing file attachments.
"""

from typing import Any, Dict, Optional
import base64

from .base import ToolResult


def register_attachment_tools(server, client) -> int:
    """
    Register attachment-related tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Number of registered tools
    """
    
    @server.tool()
    async def get_attachment(attachment_id: str) -> Dict[str, Any]:
        """
        Get information about a specific attachment.
        
        Retrieves metadata and download URL for an attachment.
        
        Args:
            attachment_id: The unique identifier of the attachment (required)
            
        Returns:
            dict: Attachment information containing:
                - id: Attachment ID
                - filename: Original filename
                - url: Download URL
                - size: File size in bytes
                - mime_type: MIME type
                - created_at: Upload timestamp
                
        Example:
            >>> attachment = await get_attachment("attach_123")
            >>> print(f"File: {attachment['data']['filename']}")
            >>> print(f"Download: {attachment['data']['url']}")
        """
        try:
            if not attachment_id:
                return ToolResult.error("attachment_id is required")
            response = await client.get(f"/attachments/{attachment_id}")
            return ToolResult.success(response, f"Attachment {attachment_id} retrieved")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def upload_attachment(
        file_content: str,
        filename: str,
        task_id: Optional[str] = None,
        deal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a new attachment.
        
        Uploads a file and optionally attaches it to a task or deal.
        The file content should be base64 encoded.
        
        Args:
            file_content: Base64 encoded file content (required)
            filename: Name for the uploaded file (required)
            task_id: ID of task to attach the file to (optional)
            deal_id: ID of deal to attach the file to (optional)
            
        Returns:
            dict: Created attachment object with:
                - id: Attachment ID
                - filename: Stored filename
                - url: Download URL
                
        Note:
            The file_content must be base64 encoded. For example:
            import base64
            with open('file.pdf', 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
                
        Example:
            >>> result = await upload_attachment(
            ...     file_content="SGVsbG8gV29ybGQ=",  # base64 of "Hello World"
            ...     filename="hello.txt",
            ...     task_id="task_123"
            ... )
        """
        try:
            if not file_content:
                return ToolResult.error("file_content is required")
            if not filename:
                return ToolResult.error("filename is required")
            
            # Decode base64 content
            try:
                file_bytes = base64.b64decode(file_content)
            except Exception:
                return ToolResult.error("file_content must be valid base64 encoded data")
            
            # Prepare multipart form data
            files = {
                "file": (filename, file_bytes)
            }
            
            data = {}
            if task_id is not None:
                data["task_id"] = task_id
            if deal_id is not None:
                data["deal_id"] = deal_id
            
            response = await client.post("/attachments", json_data=data if data else None, files=files)
            return ToolResult.success(response, f"Attachment '{filename}' uploaded successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    @server.tool()
    async def delete_attachment(attachment_id: str) -> Dict[str, Any]:
        """
        Delete an attachment.
        
        Permanently removes an attachment from the workspace.
        
        Args:
            attachment_id: The unique identifier of the attachment to delete (required)
            
        Returns:
            dict: Confirmation of deletion
            
        Warning:
            This action cannot be undone. The file will be
            permanently deleted.
            
        Example:
            >>> result = await delete_attachment("attach_123")
        """
        try:
            if not attachment_id:
                return ToolResult.error("attachment_id is required")
            response = await client.delete(f"/attachments/{attachment_id}")
            return ToolResult.success(response, f"Attachment {attachment_id} deleted successfully")
        except Exception as e:
            return ToolResult.error(str(e))
    
    return 3  # Number of registered tools

