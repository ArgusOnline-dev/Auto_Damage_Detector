"""CSV-driven cost engine."""
from __future__ import annotations

import csv
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from apps.api.core.config import settings
from apps.api.models.estimate import EstimateLineItem, EstimateTotals

logger = logging.getLogger(__name__)


DamageKey = Tuple[str, str, str, str]  # (car_type, part, damage_type, severity)


PART_MAP = {
    "front_door": "Door",
    "door": "Door",
    "back_door": "Door",
    "rear_door": "Door",
    "front_bumper": "Front bumper",
    "bumper": "Front bumper",
    "back_bumper": "Rear bumper",
    "rear_bumper": "Rear bumper",
    "fender": "Front fender",
    "front_fender": "Front fender",
    "rear_fender": "Rear fender",
    "quarter_panel": "Rear fender",
    "hood": "Hood",
    "roof": "Roof",
    "trunk": "Trunk",
    "tail_light": "Taillight",
    "taillight": "Taillight",
    "headlight": "Headlight",
    "front_wheel": "Wheel",
    "back_wheel": "Wheel",
    "wheel": "Wheel",
    "front_window": "Window",
    "back_window": "Window",
    "window": "Window",
    "windshield": "Windshield",
    "back_windshield": "Windshield",
    "mirror": "Door",
    "grille": "Front bumper",
}


DAMAGE_TYPE_MAP = {
    "dent": "Dent",
    "scratch": "Scrape",
    "paint_chip": "Scrape",
    "flaking": "Scrape",
    "corrosion": "Scrape",
    "scrape": "Scrape",
    "cracked": "Crack",
    "crack": "Crack",
    "broken_part": "Missing",
    "missing_part": "Missing",
    "missing": "Missing",
}


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


@lru_cache(maxsize=1)
def _load_cost_rules() -> Dict[DamageKey, Dict[str, str]]:
    rules: Dict[DamageKey, Dict[str, str]] = {}
    path: Path = settings.COST_RULES_PATH
    if not path.exists():
        raise FileNotFoundError(f"Cost rules CSV not found: {path}")
    with path.open() as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            key = (
                _normalize(row.get("Car_Type", "super")),
                _normalize(row.get("Part", "")),
                _normalize(row.get("Damage_Type", "")),
                _normalize(row.get("Severity", "")),
            )
            rules[key] = row
    logger.info("Loaded %d cost rules from %s", len(rules), path)
    return rules


def _map_part(part: str) -> str:
    part_key = _normalize(part)
    if part_key in PART_MAP:
        return PART_MAP[part_key]
    if "door" in part_key:
        return "Door"
    if "bumper" in part_key:
        return "Front bumper"
    if "fender" in part_key or "quarter" in part_key:
        return "Front fender"
    if "wheel" in part_key:
        return "Wheel"
    if "window" in part_key:
        return "Window"
    if "light" in part_key:
        return "Headlight"
    logger.warning("Unknown part '%s', defaulting to Door", part)
    return "Door"


def _map_damage_type(damage_type: str) -> Optional[str]:
    dt = _normalize(damage_type)
    mapped = DAMAGE_TYPE_MAP.get(dt)
    if not mapped:
        if dt == "intact":
            return None
        logger.warning("Unknown damage_type '%s', defaulting to 'Dent'", damage_type)
        return "Dent"
    return mapped


def _lookup_rule(
    car_type: str,
    part: str,
    damage_type: str,
    severity: str,
) -> Optional[Dict[str, str]]:
    rules = _load_cost_rules()
    car_key = _normalize(car_type) or "super"
    part_key = _normalize(part)
    damage_key = _normalize(damage_type)
    severity_key = _normalize(severity)
    key = (car_key, part_key, damage_key, severity_key)
    if key in rules:
        return rules[key]
    fallback = ("super", part_key, damage_key, severity_key)
    if fallback in rules:
        return rules[fallback]
    return None


def _fallback_row(part: str, damage_type: str, severity: str) -> Dict[str, str]:
    logger.warning(
        "Missing cost rule for part=%s damage=%s severity=%s. Using fallback values.",
        part,
        damage_type,
        severity,
    )
    return {
        "Part": part,
        "Damage_Type": damage_type,
        "Severity": severity,
        "New_Part_Cost": "1500",
        "Used_Part_Cost": "750",
        "Labor_Hours": "3.0",
    }


def _build_line_item(
    detection: dict,
    rule: Dict[str, str],
    labor_rate: float,
) -> EstimateLineItem:
    labor_hours = float(rule.get("Labor_Hours", 3.0))
    labor_cost = labor_hours * labor_rate
    part_cost_new = float(rule.get("New_Part_Cost", 0.0))
    part_cost_used = float(rule.get("Used_Part_Cost", part_cost_new))
    return EstimateLineItem(
        part=detection.get("part", "unknown"),
        damage_type=detection.get("damage_type", "unknown"),
        severity=detection.get("severity", "moderate"),
        labor_hours=labor_hours,
        labor_cost=labor_cost,
        part_cost_new=part_cost_new,
        part_cost_used=part_cost_used,
        total_new=labor_cost + part_cost_new,
        total_used=labor_cost + part_cost_used,
    )


def calculate_cost(
    detections: List[dict],
    labor_rate: float = 150.0,
    use_oem_parts: bool = True,
    car_type: str = "Super",
) -> dict:
    """
    Calculate repair cost estimate using CSV rules.
    """
    line_items: List[EstimateLineItem] = []

    for detection in detections:
        damage_type = detection.get("damage_type")
        if not damage_type or damage_type.lower() == "intact":
            continue  # skip intact or unknown

        severity = detection.get("severity") or "minor"
        csv_damage = _map_damage_type(damage_type)
        if not csv_damage:
            continue
        csv_part = _map_part(detection.get("part", "door"))

        rule = _lookup_rule(car_type, csv_part, csv_damage, severity)
        if not rule:
            rule = _fallback_row(csv_part, csv_damage, severity)

        item = _build_line_item(detection, rule, labor_rate)
        line_items.append(item)

    if not line_items:
        totals = EstimateTotals(min=0.0, likely=0.0, max=0.0)
        return {"line_items": [], "totals": totals}

    total_new = sum(item.total_new for item in line_items)
    total_used = sum(item.total_used for item in line_items)
    likely = total_new if use_oem_parts else total_used
    min_total = total_used
    max_total = likely * 1.2

    totals = EstimateTotals(
        min=min_total,
        likely=likely,
        max=max_total,
    )

    return {
        "line_items": line_items,
        "totals": totals,
    }

