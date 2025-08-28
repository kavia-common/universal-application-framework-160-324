/**
 Simple example showing how to trigger the alert endpoints from another service.
 Run: node examples/integration-example.js (with the alert service running)
*/
import axios from "axios";

const BASE = process.env.ALERT_SERVICE_URL || "http://localhost:4005";

async function run() {
  try {
    const idle = await axios.post(`${BASE}/alerts/idle`, {
      instanceId: "i-1234567890",
      userId: "demo-user",
      region: "us-east-1",
      idleMinutes: 78,
      metadata: { project: "demo", env: "dev" }
    });
    // eslint-disable-next-line no-console
    console.log("Idle alert result:", idle.data);
  } catch (e) {
    console.error("Idle alert error:", e.response?.data || e.message);
  }

  try {
    const downgrade = await axios.post(`${BASE}/alerts/downgrade`, {
      instanceId: "i-abcdef12345",
      userId: "demo-user",
      region: "us-west-2",
      currentType: "m5.large",
      recommendedType: "t3.large",
      expectedMonthlySavings: 33.2,
      confidence: 0.79,
      metadata: { team: "platform", env: "prod" }
    });
    // eslint-disable-next-line no-console
    console.log("Downgrade alert result:", downgrade.data);
  } catch (e) {
    console.error("Downgrade alert error:", e.response?.data || e.message);
  }
}

run();
