"""Deterministic business decision layer over collected ModelResult objects."""
from __future__ import annotations

from typing import Any, Mapping

from schemas.contracts import ModelResult
from services.decision_engine.constraints import DEFAULT_CONSTRAINTS, DecisionConstraints
from services.decision_engine.rules import DEFAULT_RULES, DecisionRules


class DecisionEngine:
    def __init__(
        self,
        rules: DecisionRules = DEFAULT_RULES,
        constraints: DecisionConstraints = DEFAULT_CONSTRAINTS,
    ) -> None:
        self.rules = rules
        self.constraints = constraints

    def evaluate(self, models: Mapping[str, ModelResult]) -> dict[str, Any]:
        primary: list[str] = []
        secondary: list[str] = []
        actions: list[dict[str, Any]] = []
        limitations: list[str] = []
        context: dict[str, Any] = {}

        production = self._prediction(models.get("production"))
        equipment = self._prediction(models.get("equipment"))
        weather = self._prediction(models.get("weather"))
        recovery = self._prediction(models.get("recovery"))
        blast = self._prediction(models.get("blast"))
        grade = self._prediction(models.get("grade"))
        prospectivity_result = models.get("prospectivity")
        prospectivity = self._prediction(prospectivity_result)

        if production:
            target = self._number(production, "target_tonnes")
            predicted = self._number(production, "predicted_tonnes")
            production_result = models.get("production")
            shortfall_probability = (
                float(production_result.uncertainty)
                if production_result is not None and production_result.uncertainty is not None
                else self._number(production, "shortfall_probability")
            )
            if shortfall_probability is not None:
                context["shortfall_probability"] = round(shortfall_probability, 4)
            if target is not None and predicted is not None and target > 0:
                gap = target - predicted
                gap_pct = gap / target
                context["production_gap_tonnes"] = round(gap, 4)
                context["production_gap_pct"] = round(gap_pct, 4)
                if gap_pct >= self.rules.production_shortfall_pct or (
                    shortfall_probability is not None
                    and shortfall_probability >= self.rules.production_shortfall_probability
                ):
                    primary.append("production_shortfall")
                    self._add_action(
                        actions,
                        "Review production plan against the current target and shortfall risk",
                        "Predicted production is below target or shortfall probability is elevated",
                        "HIGH",
                    )
        else:
            limitations.append(self._unavailable_message("production", models.get("production")))

        if equipment:
            failure_risk = self._number(equipment, "failure_risk")
            availability = self._number(equipment, "availability_pct")
            if (
                failure_risk is not None and failure_risk >= self.rules.equipment_failure_risk
            ) or (
                availability is not None and availability <= self.rules.equipment_availability_pct
            ):
                primary.append("equipment_availability")
                loader_id = equipment.get("equipment_id", "affected equipment")
                self._add_action(
                    actions,
                    f"Review {loader_id} availability and maintenance contingency",
                    "Equipment availability or failure risk is elevated",
                    "HIGH",
                )
        else:
            limitations.append(self._unavailable_message("equipment", models.get("equipment")))

        if weather:
            rainfall = self._number(weather, "rainfall_mm_forecast")
            weather_risk = str(weather.get("risk", "")).upper()
            if (rainfall is not None and rainfall >= self.rules.weather_rainfall_mm) or weather_risk == "HIGH":
                primary.append("weather")
                self._add_action(
                    actions,
                    "Review the weather-contingency operating plan",
                    "Forecast rainfall/weather risk is elevated",
                    "HIGH",
                )
        else:
            limitations.append(self._unavailable_message("weather", models.get("weather")))

        if blast:
            delay_risk = self._number(blast, "delay_risk")
            if delay_risk is not None and delay_risk >= self.rules.blast_delay_risk:
                secondary.append("blast_delay_risk")
                self._add_action(
                    actions,
                    "Review blast schedule and delay mitigation",
                    "Blast delay risk is elevated",
                    "MEDIUM",
                )
        else:
            limitations.append(self._unavailable_message("blast", models.get("blast")))

        if recovery:
            expected_recovery = self._number(recovery, "expected_recovery_pct")
            if expected_recovery is not None and expected_recovery < self.rules.recovery_pct:
                secondary.append("recovery")
                self._add_action(
                    actions,
                    "Review recovery assumptions and processing conditions",
                    "Expected recovery is below the prototype threshold",
                    "MEDIUM",
                )
        else:
            limitations.append(self._unavailable_message("recovery", models.get("recovery")))

        if grade:
            context["grade"] = grade
        if prospectivity_result is None or prospectivity_result.status == "UNAVAILABLE":
            limitations.append(self._unavailable_message("prospectivity", prospectivity_result))
        elif isinstance(prospectivity_result.prediction, (int, float)):
            context["prospectivity"] = {
                "prediction": float(prospectivity_result.prediction),
                "uncertainty": prospectivity_result.uncertainty,
            }

        driver_count = len(set(primary))
        if driver_count >= self.rules.high_risk_driver_count or "production_shortfall" in primary:
            risk_level = "HIGH"
        elif driver_count == 1 or secondary:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if any(result.status == "DEMO" for result in models.values()):
            limitations.append("Operational model outputs are synthetic demonstration values.")

        limitations = [item for item in dict.fromkeys(limitations) if item]
        return {
            "risk_level": risk_level,
            "primary_drivers": list(dict.fromkeys(primary)),
            "secondary_drivers": list(dict.fromkeys(secondary)),
            "recommended_actions": actions[: self.constraints.max_recommended_actions],
            "limitations": limitations,
            "context": context,
        }

    @staticmethod
    def _prediction(result: ModelResult | None) -> dict[str, Any] | None:
        if result is None or result.status == "UNAVAILABLE" or not isinstance(result.prediction, dict):
            return None
        return result.prediction

    @staticmethod
    def _number(payload: Mapping[str, Any], key: str) -> float | None:
        value = payload.get(key)
        if isinstance(value, bool):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _unavailable_message(model_id: str, result: ModelResult | None) -> str:
        if result is None:
            return f"{model_id}: no model result was returned"
        return f"{model_id}: {result.reason or 'model unavailable'}"

    def _add_action(self, actions: list[dict[str, Any]], action: str, reason: str, priority: str) -> None:
        if any(existing["action"] == action for existing in actions):
            return
        actions.append(
            {
                "action": action,
                "reason": reason,
                "priority": priority,
                "requires_human_approval": self.constraints.recommendations_require_human_approval,
            }
        )
