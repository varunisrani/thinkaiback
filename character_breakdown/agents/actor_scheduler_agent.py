from typing import Dict, Any, List, Tuple
import json
import logging
from datetime import datetime, timedelta
from ...base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActorSchedulerAgent:
    """
    👤 ActorSchedulerAgent (DOOP REPORTS)
    
    Specialized agent for actor scheduling and Day Out of Days (DOOP) report generation.
    Responsibilities:
    - DOOP report generation with work/travel day tracking
    - Availability conflict identification and resolution
    - Consecutive shooting day optimization
    - Actor scheduling recommendations and cost optimization
    - Industry-standard scheduling compliance
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are an Actor Scheduler Agent for film production.
        Your expertise:
        1. Generate comprehensive Day Out of Days (DOOP) reports
        2. Optimize actor availability and minimize idle time
        3. Identify scheduling conflicts and provide solutions
        4. Calculate work days, travel days, and hold days
        5. Ensure compliance with union regulations and actor contracts"""
        logger.info("ActorSchedulerAgent initialized")
    
    def generate_actor_schedule(self, scene_data: Dict[str, Any], 
                               character_data: Dict[str, Any] = None,
                               casting_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive actor scheduling and DOOP reports."""
        logger.info("Starting actor scheduling analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        characters = character_data.get('characters', []) if character_data else []
        casting_categories = casting_data.get('casting_categories', {}) if casting_data else {}
        
        logger.info(f"Processing actor scheduling for {len(characters)} characters across {len(scenes)} scenes")
        
        # Core scheduling analysis
        doop_reports = self._generate_doop_reports(characters, scenes)
        availability_conflicts = self._identify_availability_conflicts(doop_reports)
        scheduling_optimization = self._optimize_scheduling(doop_reports, scenes)
        cost_analysis = self._calculate_scheduling_costs(doop_reports, casting_categories)
        union_compliance = self._check_union_compliance(doop_reports)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "doop_reports": doop_reports,
            "availability_conflicts": availability_conflicts,
            "scheduling_optimization": scheduling_optimization,
            "cost_analysis": cost_analysis,
            "union_compliance": union_compliance,
            "scheduling_recommendations": self._generate_scheduling_recommendations(doop_reports, scenes)
        }
        
        logger.info(f"Generated actor scheduling for {len(doop_reports)} actors")
        return result
    
    def _generate_doop_reports(self, characters: List[Dict[str, Any]], 
                              scenes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate Day Out of Days reports for each actor."""
        doop_reports = {}
        
        # Create scene number to index mapping
        scene_mapping = {}
        for i, scene in enumerate(scenes):
            scene_number = scene.get('scene_number', i + 1)
            scene_mapping[str(scene_number)] = i + 1  # Shooting day
        
        for char in characters:
            char_name = char.get('name', '')
            scene_numbers = char.get('scene_numbers', [])
            
            if scene_numbers:
                # Convert scene numbers to shooting days
                work_days = []
                for scene_num in scene_numbers:
                    shooting_day = scene_mapping.get(str(scene_num))
                    if shooting_day:
                        work_days.append(shooting_day)
                
                work_days = sorted(list(set(work_days)))  # Remove duplicates and sort
                
                # Calculate travel days, hold days, and work patterns
                doop_data = self._calculate_doop_data(work_days, len(scenes))
                
                doop_reports[char_name] = {
                    "work_days": work_days,
                    "travel_days": doop_data["travel_days"],
                    "hold_days": doop_data["hold_days"],
                    "total_days": doop_data["total_days"],
                    "consecutive_work_blocks": doop_data["consecutive_blocks"],
                    "longest_break": doop_data["longest_break"],
                    "scheduling_efficiency": doop_data["efficiency"],
                    "first_day": min(work_days) if work_days else 0,
                    "last_day": max(work_days) if work_days else 0,
                    "span_days": (max(work_days) - min(work_days) + 1) if work_days else 0
                }
        
        return doop_reports
    
    def _calculate_doop_data(self, work_days: List[int], total_shoot_days: int) -> Dict[str, Any]:
        """Calculate detailed DOOP data for an actor."""
        if not work_days:
            return {
                "travel_days": [],
                "hold_days": [],
                "total_days": 0,
                "consecutive_blocks": [],
                "longest_break": 0,
                "efficiency": 0
            }
        
        # Calculate travel days (typically day before first work day and day after last work day)
        travel_days = []
        if work_days:
            # Add travel day before first work day (if not day 1)
            if min(work_days) > 1:
                travel_days.append(min(work_days) - 1)
            # Add travel day after last work day (if not last day)
            if max(work_days) < total_shoot_days:
                travel_days.append(max(work_days) + 1)
        
        # Calculate hold days (days between work days when actor is on location but not working)
        hold_days = []
        if len(work_days) > 1:
            first_day = min(work_days)
            last_day = max(work_days)
            for day in range(first_day + 1, last_day):
                if day not in work_days:
                    hold_days.append(day)
        
        # Calculate consecutive work blocks
        consecutive_blocks = self._find_consecutive_blocks(work_days)
        
        # Calculate longest break between work days
        longest_break = 0
        if len(work_days) > 1:
            for i in range(len(work_days) - 1):
                break_length = work_days[i + 1] - work_days[i] - 1
                longest_break = max(longest_break, break_length)
        
        # Calculate scheduling efficiency (work days / total span days)
        span_days = max(work_days) - min(work_days) + 1 if work_days else 1
        efficiency = round((len(work_days) / span_days) * 100, 1)
        
        total_days = len(work_days) + len(travel_days) + len(hold_days)
        
        return {
            "travel_days": travel_days,
            "hold_days": hold_days,
            "total_days": total_days,
            "consecutive_blocks": consecutive_blocks,
            "longest_break": longest_break,
            "efficiency": efficiency
        }
    
    def _find_consecutive_blocks(self, work_days: List[int]) -> List[Dict[str, Any]]:
        """Find consecutive work day blocks."""
        if not work_days:
            return []
        
        blocks = []
        current_block_start = work_days[0]
        current_block_end = work_days[0]
        
        for i in range(1, len(work_days)):
            if work_days[i] == work_days[i-1] + 1:
                # Consecutive day
                current_block_end = work_days[i]
            else:
                # End of consecutive block
                blocks.append({
                    "start_day": current_block_start,
                    "end_day": current_block_end,
                    "length": current_block_end - current_block_start + 1
                })
                current_block_start = work_days[i]
                current_block_end = work_days[i]
        
        # Add the last block
        blocks.append({
            "start_day": current_block_start,
            "end_day": current_block_end,
            "length": current_block_end - current_block_start + 1
        })
        
        return blocks
    
    def _identify_availability_conflicts(self, doop_reports: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential scheduling conflicts between actors."""
        conflicts = []
        
        # Check for actors with inefficient scheduling
        for actor, doop_data in doop_reports.items():
            efficiency = doop_data.get("scheduling_efficiency", 0)
            hold_days = len(doop_data.get("hold_days", []))
            longest_break = doop_data.get("longest_break", 0)
            
            # Flag inefficient schedules
            if efficiency < 50 and hold_days > 3:
                conflicts.append({
                    "type": "inefficient_schedule",
                    "actor": actor,
                    "issue": f"Low efficiency ({efficiency}%) with {hold_days} hold days",
                    "severity": "medium",
                    "recommendation": "Consider rescheduling scenes to improve efficiency"
                })
            
            # Flag long breaks
            if longest_break > 5:
                conflicts.append({
                    "type": "extended_break",
                    "actor": actor,
                    "issue": f"Extended {longest_break}-day break between work days",
                    "severity": "low",
                    "recommendation": "Consider grouping scenes or releasing actor"
                })
            
            # Flag excessive consecutive days
            consecutive_blocks = doop_data.get("consecutive_work_blocks", [])
            for block in consecutive_blocks:
                if block["length"] > 6:  # More than 6 consecutive days
                    conflicts.append({
                        "type": "excessive_consecutive_days",
                        "actor": actor,
                        "issue": f"{block['length']} consecutive work days (Days {block['start_day']}-{block['end_day']})",
                        "severity": "high",
                        "recommendation": "Insert mandatory rest day to comply with union regulations"
                    })
        
        return conflicts
    
    def _optimize_scheduling(self, doop_reports: Dict[str, Dict[str, Any]], 
                           scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scheduling optimization recommendations."""
        optimization = {
            "efficiency_improvements": [],
            "cost_savings_opportunities": [],
            "grouping_recommendations": []
        }
        
        # Analyze each actor's schedule for optimization opportunities
        for actor, doop_data in doop_reports.items():
            work_days = doop_data.get("work_days", [])
            hold_days = doop_data.get("hold_days", [])
            efficiency = doop_data.get("scheduling_efficiency", 0)
            
            # Efficiency improvement recommendations
            if efficiency < 70 and len(hold_days) > 2:
                optimization["efficiency_improvements"].append({
                    "actor": actor,
                    "current_efficiency": efficiency,
                    "improvement": f"Group scenes to eliminate {len(hold_days)} hold days",
                    "potential_efficiency": min(95, efficiency + (len(hold_days) * 10))
                })
            
            # Cost savings through better grouping
            if len(work_days) > 1:
                gaps = self._calculate_gaps(work_days)
                if gaps["total_gap_days"] > 3:
                    potential_savings = gaps["total_gap_days"] * 200  # Estimated daily hold cost
                    optimization["cost_savings_opportunities"].append({
                        "actor": actor,
                        "gap_days": gaps["total_gap_days"],
                        "potential_savings": potential_savings,
                        "recommendation": "Reschedule to reduce gaps between work days"
                    })
        
        # Scene grouping recommendations
        location_scenes = self._group_scenes_by_location(scenes)
        for location, scene_list in location_scenes.items():
            if len(scene_list) > 1:
                optimization["grouping_recommendations"].append({
                    "location": location,
                    "scenes": [s.get("scene_number") for s in scene_list],
                    "benefit": "Reduce location moves and actor travel",
                    "estimated_savings": len(scene_list) * 500  # Estimated per-scene savings
                })
        
        return optimization
    
    def _calculate_gaps(self, work_days: List[int]) -> Dict[str, Any]:
        """Calculate gaps between work days."""
        if len(work_days) < 2:
            return {"total_gap_days": 0, "gap_details": []}
        
        gaps = []
        total_gap_days = 0
        
        for i in range(len(work_days) - 1):
            gap = work_days[i + 1] - work_days[i] - 1
            if gap > 0:
                gaps.append({
                    "after_day": work_days[i],
                    "before_day": work_days[i + 1],
                    "gap_length": gap
                })
                total_gap_days += gap
        
        return {
            "total_gap_days": total_gap_days,
            "gap_details": gaps
        }
    
    def _group_scenes_by_location(self, scenes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group scenes by filming location."""
        location_groups = {}
        
        for scene in scenes:
            location = scene.get('location', {}).get('place', 'Unknown')
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(scene)
        
        return location_groups
    
    def _calculate_scheduling_costs(self, doop_reports: Dict[str, Dict[str, Any]], 
                                   casting_categories: Dict[str, List]) -> Dict[str, Any]:
        """Calculate costs associated with current scheduling."""
        cost_analysis = {
            "total_actor_days": 0,
            "total_hold_days": 0,
            "estimated_hold_costs": 0,
            "travel_costs": 0,
            "per_actor_costs": {}
        }
        
        # Standard cost estimates (these would be configurable)
        daily_rates = {
            "lead_cast": 3000,
            "supporting_lead": 1500,
            "day_players": 800,
            "one_line_people": 500,
            "extras": 200
        }
        
        hold_day_percentage = 0.5  # Hold days typically cost 50% of day rate
        travel_day_cost = 150  # Standard travel day allowance
        
        total_hold_days = 0
        total_travel_days = 0
        
        for actor, doop_data in doop_reports.items():
            work_days = len(doop_data.get("work_days", []))
            hold_days = len(doop_data.get("hold_days", []))
            travel_days = len(doop_data.get("travel_days", []))
            
            # Determine actor category and day rate
            actor_category = self._find_actor_category(actor, casting_categories)
            day_rate = daily_rates.get(actor_category, 500)
            
            # Calculate costs
            work_cost = work_days * day_rate
            hold_cost = hold_days * day_rate * hold_day_percentage
            travel_cost = travel_days * travel_day_cost
            total_actor_cost = work_cost + hold_cost + travel_cost
            
            cost_analysis["per_actor_costs"][actor] = {
                "category": actor_category,
                "day_rate": day_rate,
                "work_days": work_days,
                "hold_days": hold_days,
                "travel_days": travel_days,
                "work_cost": work_cost,
                "hold_cost": hold_cost,
                "travel_cost": travel_cost,
                "total_cost": total_actor_cost
            }
            
            total_hold_days += hold_days
            total_travel_days += travel_days
        
        cost_analysis.update({
            "total_hold_days": total_hold_days,
            "estimated_hold_costs": sum(costs["hold_cost"] for costs in cost_analysis["per_actor_costs"].values()),
            "travel_costs": sum(costs["travel_cost"] for costs in cost_analysis["per_actor_costs"].values()),
            "total_estimated_cost": sum(costs["total_cost"] for costs in cost_analysis["per_actor_costs"].values())
        })
        
        return cost_analysis
    
    def _find_actor_category(self, actor: str, casting_categories: Dict[str, List]) -> str:
        """Find which casting category an actor belongs to."""
        for category, actors in casting_categories.items():
            if any(actor_info.get("character") == actor for actor_info in actors):
                return category
        return "day_players"  # Default category
    
    def _check_union_compliance(self, doop_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check compliance with union regulations."""
        compliance = {
            "violations": [],
            "warnings": [],
            "compliance_status": "compliant"
        }
        
        for actor, doop_data in doop_reports.items():
            consecutive_blocks = doop_data.get("consecutive_work_blocks", [])
            
            # Check for consecutive day violations (SAG-AFTRA: max 6 consecutive days)
            for block in consecutive_blocks:
                if block["length"] > 6:
                    compliance["violations"].append({
                        "actor": actor,
                        "violation": "Excessive consecutive work days",
                        "details": f"{block['length']} consecutive days (Days {block['start_day']}-{block['end_day']})",
                        "regulation": "SAG-AFTRA: Maximum 6 consecutive work days",
                        "required_action": "Insert mandatory rest day"
                    })
                    compliance["compliance_status"] = "violation"
                
                elif block["length"] == 6:
                    compliance["warnings"].append({
                        "actor": actor,
                        "warning": "Maximum consecutive work days reached",
                        "details": f"6 consecutive days (Days {block['start_day']}-{block['end_day']})",
                        "recommendation": "Consider scheduling break after this block"
                    })
        
        return compliance
    
    def _generate_scheduling_recommendations(self, doop_reports: Dict[str, Dict[str, Any]], 
                                           scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific scheduling recommendations."""
        recommendations = []
        
        # Analyze overall scheduling efficiency
        total_efficiency = sum(doop["scheduling_efficiency"] for doop in doop_reports.values())
        avg_efficiency = total_efficiency / len(doop_reports) if doop_reports else 0
        
        if avg_efficiency < 60:
            recommendations.append({
                "category": "Overall Efficiency",
                "recommendation": "Consider major schedule restructuring to improve actor utilization",
                "priority": "high",
                "impact": f"Current average efficiency: {avg_efficiency:.1f}%"
            })
        
        # Specific actor recommendations
        for actor, doop_data in doop_reports.items():
            hold_days = len(doop_data.get("hold_days", []))
            if hold_days > 4:
                recommendations.append({
                    "category": "Actor Optimization",
                    "recommendation": f"Reschedule {actor}'s scenes to reduce {hold_days} hold days",
                    "priority": "medium",
                    "impact": f"Potential cost savings: ${hold_days * 500}"
                })
        
        # Location-based recommendations
        location_scenes = self._group_scenes_by_location(scenes)
        for location, scene_list in location_scenes.items():
            if len(scene_list) > 3:
                recommendations.append({
                    "category": "Location Grouping",
                    "recommendation": f"Group all {len(scene_list)} scenes at {location} consecutively",
                    "priority": "medium",
                    "impact": "Reduce location moves and setup costs"
                })
        
        return recommendations