"""
Pydantic models for Weeek API data validation.

These models define the structure of data for API requests and responses.
"""

from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task status values."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of items to return (1-100)"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    status_code: Optional[int] = None
    details: Optional[dict] = None


# Workspace Models
class Workspace(BaseModel):
    """Workspace information."""
    id: str
    name: Optional[str] = None
    
    class Config:
        extra = "allow"


# User Models
class User(BaseModel):
    """User information."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    class Config:
        extra = "allow"


# Tag Models
class Tag(BaseModel):
    """Tag information."""
    id: str
    title: str
    color: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateTagRequest(BaseModel):
    """Request to create a tag."""
    title: str = Field(..., min_length=1, max_length=255)


class UpdateTagRequest(BaseModel):
    """Request to update a tag."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)


# Project Models
class Project(BaseModel):
    """Project information."""
    id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateProjectRequest(BaseModel):
    """Request to create a project."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


# Board Models
class Board(BaseModel):
    """Board information."""
    id: str
    title: str
    project_id: Optional[str] = None
    type: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateBoardRequest(BaseModel):
    """Request to create a board."""
    title: str = Field(..., min_length=1, max_length=255)
    project_id: Optional[str] = None
    type: Optional[str] = None


# Board Column Models
class BoardColumn(BaseModel):
    """Board column information."""
    id: str
    title: str
    board_id: str
    order: Optional[int] = None
    
    class Config:
        extra = "allow"


class CreateBoardColumnRequest(BaseModel):
    """Request to create a board column."""
    title: str = Field(..., min_length=1, max_length=255)
    board_id: str
    order: Optional[int] = None


# Task Models
class Task(BaseModel):
    """Task information."""
    id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    project_id: Optional[str] = None
    board_id: Optional[str] = None
    column_id: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    
    class Config:
        extra = "allow"


class CreateTaskRequest(BaseModel):
    """Request to create a task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: Optional[str] = None
    board_id: Optional[str] = None
    column_id: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = Field(
        None,
        description="Due date in ISO8601 format (YYYY-MM-DD)"
    )
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class UpdateTaskRequest(BaseModel):
    """Request to update a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    column_id: Optional[str] = None
    tags: Optional[List[str]] = None


# Funnel Models
class Funnel(BaseModel):
    """Funnel information."""
    id: str
    title: str
    description: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateFunnelRequest(BaseModel):
    """Request to create a funnel."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


# Funnel Status Models
class FunnelStatus(BaseModel):
    """Funnel status information."""
    id: str
    title: str
    funnel_id: str
    order: Optional[int] = None
    
    class Config:
        extra = "allow"


class CreateFunnelStatusRequest(BaseModel):
    """Request to create a funnel status."""
    title: str = Field(..., min_length=1, max_length=255)
    funnel_id: str
    order: Optional[int] = None


# Deal Models
class Deal(BaseModel):
    """Deal information."""
    id: str
    title: str
    funnel_id: str
    status_id: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    contact_id: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateDealRequest(BaseModel):
    """Request to create a deal."""
    title: str = Field(..., min_length=1, max_length=255)
    funnel_id: str
    status_id: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    contact_id: Optional[str] = None


# Organization Models
class Organization(BaseModel):
    """Organization information."""
    id: str
    name: str
    description: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateOrganizationRequest(BaseModel):
    """Request to create an organization."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    email: Optional[str] = None


# Contact Models
class Contact(BaseModel):
    """Contact information."""
    id: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    organization_id: Optional[str] = None
    
    class Config:
        extra = "allow"


class CreateContactRequest(BaseModel):
    """Request to create a contact."""
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    organization_id: Optional[str] = None


# Portfolio Models
class Portfolio(BaseModel):
    """Portfolio information."""
    id: str
    title: Optional[str] = None
    
    class Config:
        extra = "allow"


# Custom Field Models
class CustomField(BaseModel):
    """Custom field information."""
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    
    class Config:
        extra = "allow"


# Attachment Models
class Attachment(BaseModel):
    """Attachment information."""
    id: str
    filename: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


# Currency Models
class Currency(BaseModel):
    """Currency information."""
    code: str
    name: Optional[str] = None
    
    class Config:
        extra = "allow"

