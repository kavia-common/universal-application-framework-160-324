# EC2 Manager Backend (FastAPI)

This backend connects to AWS via boto3, lists running EC2 instances, automatically shuts down idle instances, and logs shutdown events into PostgreSQL.

## Features

- AWS connection using boto3 with environment-driven credentials
- FastAPI endpoints:
  - GET `/health`
  - GET `/instances/running`
  - POST `/maintenance/idle-shutdown`
  - GET `/logs/shutdowns`
- Background scheduler automatically checks for idle instances and stops them
- Shutdown events logged to PostgreSQL using SQLAlchemy

## Requirements

- Python 3.11+
- PostgreSQL database (DATABASE_URL)
- AWS credentials available via env or IAM role

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in values:
   ```
   cp .env.example .env
   ```

3. Run the service:
   ```bash
   python run.py
   ```

The server starts at `http://0.0.0.0:8000`. API docs available at `/docs`.

## Environment Variables

- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (or rely on IAM role)
- AWS_DEFAULT_REGION (default: us-east-1)
- DATABASE_URL (e.g., postgresql+psycopg2://user:password@host:5432/db)
- IDLE_THRESHOLD_MINUTES (default: 120)
- SCHEDULER_INTERVAL_SECONDS (default: 300)
- APP_HOST (default: 0.0.0.0)
- APP_PORT (default: 8000)

## Notes

- Idle detection uses instance `launch_time` as a proxy. For accurate CPU/network idleness, integrate CloudWatch metrics.
- Database tables are created automatically on startup.
- Logs are written using Python logging; adjust `LOG_LEVEL` environment variable as needed.

## Security

- Do not commit real secrets. Use environment variables and .env for local only.
- Use least-privilege IAM policy allowing DescribeInstances and StopInstances.

## IAM Policy Example

Grant the service the minimum permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["ec2:DescribeInstances", "ec2:StopInstances"], "Resource": "*" }
  ]
}
```
