import { Router } from "express";
import Joi from "joi";
import { sendIdleInstanceAlert, sendDowngradeRecommendationAlert } from "../services/alertService.js";

const router = Router();

const idleSchema = Joi.object({
  instanceId: Joi.string().required(),
  userId: Joi.string().allow(""),
  region: Joi.string().allow(""),
  idleMinutes: Joi.number().integer().min(0).default(60),
  metadata: Joi.object().unknown(true).default({})
});

const downgradeSchema = Joi.object({
  instanceId: Joi.string().required(),
  userId: Joi.string().allow(""),
  region: Joi.string().allow(""),
  currentType: Joi.string().required(),
  recommendedType: Joi.string().required(),
  expectedMonthlySavings: Joi.number().optional(),
  confidence: Joi.number().min(0).max(1).optional(),
  metadata: Joi.object().unknown(true).default({})
});

// PUBLIC_INTERFACE
router.post("/idle", async (req, res, next) => {
  /**
   * POST /alerts/idle
   * Body: { instanceId, userId?, region?, idleMinutes?, metadata? }
   * Sends Slack and Email notifications that an instance has been idle > 1 hour.
   * Returns a JSON object with per-channel send results.
   */
  try {
    const { value, error } = idleSchema.validate(req.body, { abortEarly: false, convert: true });
    if (error) {
      return res.status(400).json({ error: error.message });
    }
    const result = await sendIdleInstanceAlert(value);
    res.json(result);
  } catch (err) {
    next(err);
  }
});

// PUBLIC_INTERFACE
router.post("/downgrade", async (req, res, next) => {
  /**
   * POST /alerts/downgrade
   * Body: { instanceId, userId?, region?, currentType, recommendedType, expectedMonthlySavings?, confidence?, metadata? }
   * Sends Slack and Email notifications for an AI downgrade recommendation.
   * Returns a JSON object with per-channel send results.
   */
  try {
    const { value, error } = downgradeSchema.validate(req.body, { abortEarly: false, convert: true });
    if (error) {
      return res.status(400).json({ error: error.message });
    }
    const result = await sendDowngradeRecommendationAlert(value);
    res.json(result);
  } catch (err) {
    next(err);
  }
});

export default router;
