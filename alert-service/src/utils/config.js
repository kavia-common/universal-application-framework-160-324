import dotenv from "dotenv";
import Joi from "joi";

dotenv.config();

let cached;

const schema = Joi.object({
  SLACK_WEBHOOK_URL: Joi.string().uri().allow("").default(""),
  EMAIL_HOST: Joi.string().allow(""),
  EMAIL_PORT: Joi.number().integer().min(1).max(65535).default(587),
  EMAIL_USER: Joi.string().allow(""),
  EMAIL_PASS: Joi.string().allow(""),
  EMAIL_FROM: Joi.string().email().allow(""),
  EMAIL_TO: Joi.string().allow(""),
  PORT: Joi.number().integer().min(1).max(65535).default(4005),
  NODE_ENV: Joi.string().valid("development", "production", "test").default("development")
}).unknown(true);

export function getConfig() {
  if (cached) return cached;
  const { value, error } = schema.validate(process.env, { abortEarly: false, convert: true });
  if (error) {
    // Log but don't throw; service can run with only Slack or only Email configured
    // Real deployments should fail-fast if both channels are empty
    // eslint-disable-next-line no-console
    console.warn("Config validation warnings:", error.message);
  }
  const EMAIL_RECIPIENTS = (value.EMAIL_TO ?? "")
    .split(",")
    .map(s => s.trim())
    .filter(Boolean);

  cached = {
    SLACK_WEBHOOK_URL: value.SLACK_WEBHOOK_URL,
    EMAIL_HOST: value.EMAIL_HOST,
    EMAIL_PORT: value.EMAIL_PORT,
    EMAIL_USER: value.EMAIL_USER,
    EMAIL_PASS: value.EMAIL_PASS,
    EMAIL_FROM: value.EMAIL_FROM,
    EMAIL_TO: value.EMAIL_TO, // original string
    EMAIL_RECIPIENTS,
    PORT: value.PORT,
    NODE_ENV: value.NODE_ENV
  };
  return cached;
}
