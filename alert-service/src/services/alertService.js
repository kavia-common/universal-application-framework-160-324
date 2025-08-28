import { buildSlackPayload, sendSlackMessage } from "./slackService.js";
import { buildEmailTemplate, sendEmail } from "./emailService.js";

/**
// PUBLIC_INTERFACE
export async function sendIdleInstanceAlert(params) {
  /**
   * Sends Slack + Email alerts for idle instance detection.
   * params: { instanceId, userId, region, idleMinutes, metadata? }
   */
  const {
    instanceId,
    userId,
    region,
    idleMinutes = 60,
    metadata = {}
  } = params;

  const title = "Idle Instance Detected";
  const text = `Instance ${instanceId} has been idle for ${idleMinutes} minutes (>= 60).`;
  const fields = [
    { title: "Instance ID", value: instanceId },
    { title: "User", value: userId || "-" },
    { title: "Region", value: region || "-" },
    { title: "Idle Minutes", value: String(idleMinutes) }
  ];
  Object.entries(metadata).forEach(([k, v]) => fields.push({ title: k, value: String(v) }));

  // Slack
  const slackRes = await sendSlackMessage(buildSlackPayload({ title, text, fields }));

  // Email
  const html = buildEmailTemplate({
    title,
    intro: text,
    meta: fields
  });
  const emailRes = await sendEmail({
    subject: `[ALERT] Idle Instance ${instanceId}`,
    html,
    text
  });

  return { slack: slackRes, email: emailRes };
}

/**
// PUBLIC_INTERFACE
export async function sendDowngradeRecommendationAlert(params) {
  /**
   * Sends Slack + Email alerts for AI downgrade recommendation.
   * params: { instanceId, userId, region, currentType, recommendedType, expectedMonthlySavings?, confidence?, metadata? }
   */
  const {
    instanceId,
    userId,
    region,
    currentType,
    recommendedType,
    expectedMonthlySavings,
    confidence,
    metadata = {}
  } = params;

  const title = "AI Recommendation: Downgrade Instance";
  const text =
    `AI suggests downgrading instance ${instanceId} from ${currentType} to ${recommendedType}.` +
    (expectedMonthlySavings != null ? ` Expected monthly savings: $${Number(expectedMonthlySavings).toFixed(2)}.` : "") +
    (confidence != null ? ` Confidence: ${(Number(confidence) * 100).toFixed(1)}%.` : "");

  const fields = [
    { title: "Instance ID", value: instanceId },
    { title: "User", value: userId || "-" },
    { title: "Region", value: region || "-" },
    { title: "Current Type", value: currentType },
    { title: "Recommended", value: recommendedType }
  ];
  if (expectedMonthlySavings != null) fields.push({ title: "Est. Savings", value: `$${Number(expectedMonthlySavings).toFixed(2)}` });
  if (confidence != null) fields.push({ title: "Confidence", value: `${(Number(confidence) * 100).toFixed(1)}%` });
  Object.entries(metadata).forEach(([k, v]) => fields.push({ title: k, value: String(v) }));

  // Slack
  const slackRes = await sendSlackMessage(buildSlackPayload({ title, text, fields }));

  // Email
  const html = buildEmailTemplate({
    title,
    intro: text,
    meta: fields
  });
  const emailRes = await sendEmail({
    subject: `[ALERT] AI Downgrade Recommendation for ${instanceId}`,
    html,
    text
  });

  return { slack: slackRes, email: emailRes };
}
