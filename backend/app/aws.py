from __future__ import annotations

import boto3
from botocore.config import Config as BotoConfig

from .config import Settings


def get_boto3_session(settings: Settings) -> boto3.session.Session:
    """
    Create a boto3 session using explicitly provided credentials if available,
    otherwise fall back to default credentials chain (env, shared config, IAM role).
    """
    session_kwargs = {
        "region_name": settings.aws_default_region,
    }
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    # You can add token support if needed via AWS_SESSION_TOKEN in env; boto3 picks it up automatically.
    return boto3.session.Session(**session_kwargs)


def get_ec2_client(session: boto3.session.Session, region: str | None = None):
    """
    Return a low-level EC2 client.
    """
    config = BotoConfig(retries={"max_attempts": 10, "mode": "standard"})
    if region:
        return session.client("ec2", region_name=region, config=config)
    return session.client("ec2", config=config)


def get_ec2_resource(session: boto3.session.Session, region: str | None = None):
    """
    Return a high-level EC2 resource.
    """
    if region:
        return session.resource("ec2", region_name=region)
    return session.resource("ec2")
