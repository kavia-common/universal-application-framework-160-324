import express from "express";
import dotenv from "dotenv";
import pino from "pino";
import pinoHttp from "pino-http";
import morgan from "morgan";
import alertsRouter from "./routes/alerts.js";
import { getConfig } from "./utils/config.js";

dotenv.config();

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport: process.env.NODE_ENV === "development" ? { target: "pino-pretty" } : undefined
});

const app = express();

// Middleware
app.use(express.json({ limit: "1mb" }));
app.use(pinoHttp({ logger }));
// morgan for concise access logs in dev
if (process.env.NODE_ENV !== "production") {
  app.use(morgan("dev"));
}

// Health endpoint
// PUBLIC_INTERFACE
app.get("/health", (req, res) => {
  /** Health check endpoint */
  res.json({ status: "ok", service: "alert-service" });
});

// Alerts API
app.use("/alerts", alertsRouter);

// Global error handler
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  req.log?.error({ err }, "Unhandled error");
  const status = err.status || 500;
  res.status(status).json({ error: err.message || "Internal Server Error" });
});

// Start server
const { PORT = 4005 } = getConfig();
app.listen(PORT, () => {
  logger.info(`Alert service listening on port ${PORT}`);
});

/**
 Example curl usage:

 curl -s -X POST http://localhost:4005/alerts/idle \
  -H "Content-Type: application/json" \
  -d '{
    "instanceId": "i-1234567890",
    "userId": "u-1",
    "region": "us-east-1",
    "idleMinutes": 75,
    "metadata": { "project": "demo", "env": "dev" }
  }'

 curl -s -X POST http://localhost:4005/alerts/downgrade \
  -H "Content-Type: application/json" \
  -d '{
    "instanceId": "i-abcdef",
    "userId": "u-2",
    "region": "us-west-2",
    "currentType": "m5.large",
    "recommendedType": "t3.large",
    "expectedMonthlySavings": 42.5,
    "confidence": 0.87,
    "metadata": { "service": "batch", "env": "prod" }
  }'
*/
