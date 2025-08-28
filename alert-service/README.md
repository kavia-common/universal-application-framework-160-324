# Alert Service (Node.js)

A small, production-oriented Node.js microservice to send alerts to Slack (via Incoming Webhook) and Email (via SMTP) for cloud cost optimizer events:
- Idle instance detected (> 1 hour idle)
- AI service recommends instance downgrade

## Features
- Environment-driven configuration (dotenv)
- Slack alerts through webhook URL using axios
- Email alerts through SMTP using nodemailer
- Clean, extensible structure (config, services, routes)
- Health check endpoint and two alert endpoints
- Example integration usage included

## Endpoints

- GET `/health`
  - Simple health check.

- POST `/alerts/idle`
  - Sends an alert indicating an instance has been idle for more than 1 hour.
  - Request body:
    ```
    {
      "instanceId": "i-0123456789abcdef0",
      "userId": "u-123",
      "region": "us-east-1",
      "idleMinutes": 75,
      "metadata": { "project": "acme", "env": "dev" }
    }
    ```
  - idleMinutes: optional; default interpreted as >= 60 if omitted.

- POST `/alerts/downgrade`
  - Sends an alert for an AI recommendation to downgrade an instance.
  - Request body:
    ```
    {
      "instanceId": "i-0123456789abcdef0",
      "userId": "u-123",
      "region": "us-east-1",
      "currentType": "m5.large",
      "recommendedType": "t3.large",
      "expectedMonthlySavings": 42.5,
      "confidence": 0.87,
      "metadata": { "service": "batch", "env": "prod" }
    }
    ```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

- SLACK_WEBHOOK_URL
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_USER
- EMAIL_PASS
- EMAIL_FROM
- EMAIL_TO

Notes:
- EMAIL_PORT should be a number (e.g., 587). Use 465 for secure SSL if required.
- EMAIL_TO can be a comma-separated list of recipient emails.

## Quickstart

1) Install dependencies:
```bash
cd universal-application-framework-160-324/alert-service
npm install
```

2) Configure environment:
```bash
cp .env.example .env
# Edit .env to include your Slack webhook and SMTP details
```

3) Run:
```bash
npm start
```

Service will start on PORT (default 4005). Health endpoint:
- http://localhost:4005/health

## Example Integration (Node.js/axios)

```js
import axios from "axios";

async function sendIdleAlert() {
  await axios.post("http://localhost:4005/alerts/idle", {
    instanceId: "i-abc",
    userId: "u-1",
    region: "us-east-1",
    idleMinutes: 80,
    metadata: { project: "demo", env: "dev" }
  });
}

async function sendDowngradeAlert() {
  await axios.post("http://localhost:4005/alerts/downgrade", {
    instanceId: "i-xyz",
    userId: "u-2",
    region: "us-west-2",
    currentType: "m5.large",
    recommendedType: "t3.large",
    expectedMonthlySavings: 35.7,
    confidence: 0.82,
    metadata: { team: "platform", env: "prod" }
  });
}
```

## Implementation Overview

- `src/config.js`: Loads env vars (dotenv) and validates required fields.
- `src/services/slackService.js`: Slack webhook sender using axios.
- `src/services/emailService.js`: Nodemailer SMTP transporter and email helpers.
- `src/services/alertService.js`: Composes Slack + Email messages for each alert type.
- `src/routes/alerts.js`: Express routes for idle and downgrade alerts.
- `src/index.js`: Server bootstrap with health check and error handling.

## Security

- Do not commit real secrets. Use environment variables and `.env` for local dev.
- Restrict network access to the service if deployed in private environments.

## Extensibility

- Add new channels (e.g., Teams, PagerDuty) by creating a new service module and extending `alertService.js`.
- Add authentication middleware for protected deployments (e.g., API keys, JWT).

## License

© {year} Kavia Labs. All rights reserved.
