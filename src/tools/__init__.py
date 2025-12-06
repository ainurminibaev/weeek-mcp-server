"""
MCP Tools for Weeek API.

This package contains all tool implementations organized by API domain.
Each module provides tools for a specific Weeek API section.
"""

from .workspace_tools import register_workspace_tools
from .user_tools import register_user_tools
from .tag_tools import register_tag_tools
from .custom_field_tools import register_custom_field_tools
from .currency_tools import register_currency_tools
from .project_tools import register_project_tools
from .portfolio_tools import register_portfolio_tools
from .board_tools import register_board_tools
from .board_column_tools import register_board_column_tools
from .task_tools import register_task_tools
from .funnel_tools import register_funnel_tools
from .funnel_status_tools import register_funnel_status_tools
from .deal_tools import register_deal_tools
from .organization_tools import register_organization_tools
from .contact_tools import register_contact_tools
from .attachment_tools import register_attachment_tools
from .tag_extra_tools import register_tag_extra_tools


def register_all_tools(server, client):
    """
    Register all Weeek API tools with the MCP server.
    
    Args:
        server: MCP server instance
        client: WeeekClient instance
        
    Returns:
        Total number of registered tools
    """
    total = 0
    
    # Register tools by domain
    total += register_workspace_tools(server, client)
    total += register_user_tools(server, client)
    total += register_tag_tools(server, client)
    total += register_custom_field_tools(server, client)
    total += register_currency_tools(server, client)
    total += register_project_tools(server, client)
    total += register_portfolio_tools(server, client)
    total += register_board_tools(server, client)
    total += register_board_column_tools(server, client)
    total += register_task_tools(server, client)
    total += register_funnel_tools(server, client)
    total += register_funnel_status_tools(server, client)
    total += register_deal_tools(server, client)
    total += register_organization_tools(server, client)
    total += register_contact_tools(server, client)
    total += register_attachment_tools(server, client)
    total += register_tag_extra_tools(server, client)
    
    return total


__all__ = [
    "register_all_tools",
    "register_workspace_tools",
    "register_user_tools",
    "register_tag_tools",
    "register_custom_field_tools",
    "register_currency_tools",
    "register_project_tools",
    "register_portfolio_tools",
    "register_board_tools",
    "register_board_column_tools",
    "register_task_tools",
    "register_funnel_tools",
    "register_funnel_status_tools",
    "register_deal_tools",
    "register_organization_tools",
    "register_contact_tools",
    "register_attachment_tools",
    "register_tag_extra_tools",
]

