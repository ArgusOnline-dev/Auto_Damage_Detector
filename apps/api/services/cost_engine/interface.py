"""Cost engine interface for Saad's cost estimation service."""
from typing import List
from apps.api.models.estimate import EstimateLineItem, EstimateTotals


def calculate_cost(
    detections: List[dict],
    labor_rate: float = 150.0,
    use_oem_parts: bool = True
) -> dict:
    """
    Calculate repair cost estimate (placeholder).
    
    This is an interface for Saad's cost engine service.
    When Saad implements the actual cost engine (Step 6), this will call his service.
    
    Args:
        detections: List of detection results with severity
        labor_rate: Labor rate per hour
        use_oem_parts: Whether to use OEM parts (True) or used parts (False)
        
    Returns:
        Dictionary with line_items and totals
    """
    # Mock cost calculation for testing
    # This will be replaced with actual cost engine call when Saad's service is ready
    
    line_items = []
    
    for detection in detections:
        part = detection.get("part", "unknown")
        damage_type = detection.get("damage_type", "unknown")
        severity = detection.get("severity", "moderate")
        
        # Mock cost data (based on sample from cost_rules.csv)
        mock_costs = {
            ("door", "dent", "moderate"): {
                "labor_hours": 5.4,
                "part_cost_new": 3500.0,
                "part_cost_used": 1750.0
            },
            ("front_bumper", "scrape", "minor"): {
                "labor_hours": 1.5,
                "part_cost_new": 2800.0,
                "part_cost_used": 1400.0
            }
        }
        
        # Get mock costs or use defaults
        key = (part.lower().replace("_", " "), damage_type.lower(), severity.lower())
        costs = mock_costs.get(key, {
            "labor_hours": 3.0,
            "part_cost_new": 2000.0,
            "part_cost_used": 1000.0
        })
        
        labor_hours = costs["labor_hours"]
        labor_cost = labor_hours * labor_rate
        part_cost_new = costs["part_cost_new"]
        part_cost_used = costs["part_cost_used"]
        
        line_item = EstimateLineItem(
            part=part,
            damage_type=damage_type,
            severity=severity,
            labor_hours=labor_hours,
            labor_cost=labor_cost,
            part_cost_new=part_cost_new,
            part_cost_used=part_cost_used,
            total_new=labor_cost + part_cost_new,
            total_used=labor_cost + part_cost_used
        )
        line_items.append(line_item)
    
    # Calculate totals
    total_new = sum(item.total_new for item in line_items)
    total_used = sum(item.total_used for item in line_items)
    total_max = total_new * 1.2  # Add 20% buffer for max
    
    totals = EstimateTotals(
        min=total_used,
        likely=total_new,
        max=total_max
    )
    
    return {
        "line_items": line_items,
        "totals": totals
    }

