import axios from "axios";
import { getConfig } from "../utils/config.js";

/**
 * Send a Slack message via Incoming Webhook.
 * If SLACK_WEBHOOK_URL is not configured, resolves without sending.
 */
export async function sendSlackMessage(payload) {
  const { SLACK_WEBHOOK_URL } = getConfig();
  if (!SLACK_WEBHOOK_URL) {
    return { sent: false, message: "Slack webhook not configured" };
  }
  try {
    const res = await axios.post(SLACK_WEBHOOK_URL, payload, {
      headers: { "Content-Type": "application/json" },
      timeout: 8000
    });
    return { sent: true, status: res.status };
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error("Slack send error:", err?.response?.status || err.message);
    return { sent: false, error: err.message };
  }
}

/**
 * Build a simple Slack message payload with blocks.
 */
export function buildSlackPayload({ title, text, fields = [] }) {
  const blocks = [
    {
      type: "header",
      text: { type: "plain_text", text: title }
    },
    { type: "section", text: { type: "mrkdwn", text } }
  ];
  if (fields.length) {
    blocks.push({
      type: "section",
      fields: fields.map(f => ({
        type: "mrkdwn",
        text: `*${f.title}:*\n${f.value}`
      }))
    });
  }
  return { blocks };
}
