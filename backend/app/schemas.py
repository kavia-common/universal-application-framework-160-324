from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class EC2Instance(BaseModel):
    instance_id: str = Field(..., description="EC2 instance ID")
    state: str = Field(..., description="EC2 instance state, e.g., running, stopped")
    instance_type: Optional[str] = Field(None, description="Instance type such as t3.micro")
    launch_time: Optional[datetime] = Field(None, description="Time when the instance was launched")
    region: str = Field(..., description="AWS region of the instance")
    tags: Optional[dict] = Field(default=None, description="Instance tags")


class EC2InstanceListResponse(BaseModel):
    count: int = Field(..., description="Number of instances in result")
    instances: List[EC2Instance] = Field(default_factory=list, description="List of running EC2 instances")


class ShutdownEvent(BaseModel):
    instance_id: str = Field(..., description="Instance ID shut down")
    region: str = Field(..., description="Region where the instance resides")
    reason: str = Field(..., description="Reason of shutdown")
    details: Optional[str] = Field(None, description="Additional details/context")
    event_time: datetime = Field(..., description="Timestamp of the shutdown event")
