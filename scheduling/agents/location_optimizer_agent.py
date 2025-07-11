from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timedelta
from base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationOptimizerAgent:
    """
    🚧 LocationOptimizerAgent (LOGISTICS) - Gemini 2.5 Flash
    
    Superior geographic optimization agent for location logistics.
    Responsibilities:
    - Optimize location grouping for efficient shooting
    - Plan equipment moves and logistics
    - Coordinate crew transportation
    - Manage permit requirements and deadlines
    - Analyze location-based cost optimization
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Location Optimizer Agent for film production.
        Your expertise in superior geographic optimization:
        1. Optimize location grouping for maximum shooting efficiency
        2. Plan detailed equipment moves and logistics coordination
        3. Coordinate crew transportation and accommodation
        4. Manage permit requirements and regulatory compliance
        5. Analyze location-based cost optimization strategies
        
        Focus on superior geographic optimization with PEFT-enhanced location logistics."""
        logger.info("LocationOptimizerAgent initialized")
    
    async def optimize_locations(self, scene_data: Dict[str, Any], location_constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize location logistics for maximum efficiency."""
        logger.info("Starting location logistics optimization")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing location optimization for {len(scenes)} scenes")
        
        # Analyze location grouping
        location_grouping = self._analyze_location_grouping(scenes)
        
        # Plan logistics
        logistics_planning = self._plan_logistics(scenes, location_grouping)
        
        # Assess permit requirements
        permit_requirements = self._assess_permit_requirements(scenes)
        
        # Optimize costs
        cost_optimization = self._optimize_location_costs(scenes, logistics_planning)
        
        # Generate transportation plan
        transportation_plan = self._generate_transportation_plan(scenes, logistics_planning)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "location_grouping": location_grouping,
            "logistics_planning": logistics_planning,
            "permit_requirements": permit_requirements,
            "cost_optimization": cost_optimization,
            "transportation_plan": transportation_plan,
            "optimization_summary": self._generate_optimization_summary(location_grouping, logistics_planning)
        }
        
        logger.info(f"Generated location optimization for {len(scenes)} scenes")
        return result
    
    def _analyze_location_grouping(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and optimize location grouping for efficient shooting."""
        grouping = {
            "location_clusters": {},
            "shooting_efficiency": {},
            "travel_optimization": {},
            "recommended_order": []
        }
        
        # Group scenes by location
        location_scenes = {}
        for scene in scenes:
            location = scene.get('location', {})
            location_key = f"{location.get('place', 'Unknown')}_{location.get('type', 'INT')}"
            
            if location_key not in location_scenes:
                location_scenes[location_key] = {
                    "scenes": [],
                    "total_pages": 0,
                    "complexity_score": 0,
                    "location_type": location.get('type', 'INT'),
                    "location_name": location.get('place', 'Unknown')
                }
            
            location_scenes[location_key]["scenes"].append(scene.get('scene_number', '0'))
            location_scenes[location_key]["total_pages"] += self._estimate_scene_pages_numeric(scene)
            location_scenes[location_key]["complexity_score"] += len(scene.get('technical_cues', []))
        
        # Calculate estimated days for each location
        for location_key, location_data in location_scenes.items():
            scene_count = len(location_data["scenes"])
            complexity_factor = location_data["complexity_score"] / scene_count if scene_count > 0 else 0
            
            # Base calculation: 3-4 scenes per day, adjusted for complexity
            base_days = (scene_count + 2) // 3
            complexity_adjustment = complexity_factor * 0.2
            
            estimated_days = max(1, round(base_days + complexity_adjustment))
            
            grouping["location_clusters"][location_key] = {
                "scenes": location_data["scenes"],
                "estimated_days": estimated_days,
                "scene_count": scene_count,
                "complexity_score": location_data["complexity_score"],
                "location_type": location_data["location_type"],
                "location_name": location_data["location_name"]
            }
        
        # Analyze shooting efficiency
        total_scenes = len(scenes)
        total_locations = len(location_scenes)
        total_estimated_days = sum(cluster["estimated_days"] for cluster in grouping["location_clusters"].values())
        
        grouping["shooting_efficiency"] = {
            "total_scenes": total_scenes,
            "total_locations": total_locations,
            "estimated_shooting_days": total_estimated_days,
            "scenes_per_day_average": round(total_scenes / total_estimated_days, 1) if total_estimated_days > 0 else 0,
            "location_efficiency_score": round((total_scenes / total_locations) * 10, 1) if total_locations > 0 else 0
        }
        
        # Travel optimization
        grouping["travel_optimization"] = self._optimize_travel_between_locations(location_scenes)
        
        # Recommended shooting order
        grouping["recommended_order"] = self._recommend_shooting_order(location_scenes)
        
        return grouping
    
    def _estimate_scene_pages_numeric(self, scene: Dict[str, Any]) -> float:
        """Estimate scene pages as a numeric value."""
        description_length = len(scene.get('description', ''))
        dialogue_count = len(scene.get('dialogues', []))
        
        # Rough estimation: 250 words per page
        estimated_pages = (description_length + dialogue_count * 50) / 250
        return max(0.125, estimated_pages)  # Minimum 1/8 page
    
    def _optimize_travel_between_locations(self, location_scenes: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize travel between locations to minimize time and cost."""
        travel_optimization = {
            "location_pairs": [],
            "optimal_sequence": [],
            "travel_time_matrix": {},
            "cost_savings": {}
        }
        
        locations = list(location_scenes.keys())
        
        # Create simplified travel time matrix (in practice, use real geographic data)
        for i, loc1 in enumerate(locations):
            travel_optimization["travel_time_matrix"][loc1] = {}
            for j, loc2 in enumerate(locations):
                if i != j:
                    # Simplified travel time calculation
                    travel_time = self._estimate_travel_time(loc1, loc2)
                    travel_optimization["travel_time_matrix"][loc1][loc2] = travel_time
        
        # Find optimal sequence using simplified traveling salesman approach
        if len(locations) > 1:
            optimal_sequence = self._find_optimal_location_sequence(locations, travel_optimization["travel_time_matrix"])
            travel_optimization["optimal_sequence"] = optimal_sequence
        
        return travel_optimization
    
    def _estimate_travel_time(self, loc1: str, loc2: str) -> float:
        """Estimate travel time between two locations (simplified)."""
        # In practice, this would use actual geographic data and routing APIs
        # For now, use simplified logic based on location types
        
        loc1_type = loc1.split('_')[-1] if '_' in loc1 else 'INT'
        loc2_type = loc2.split('_')[-1] if '_' in loc2 else 'INT'
        
        if loc1_type == 'EXT' and loc2_type == 'EXT':
            return 2.0  # 2 hours for exterior to exterior
        elif loc1_type == 'INT' and loc2_type == 'INT':
            return 1.0  # 1 hour for interior to interior
        else:
            return 1.5  # 1.5 hours for mixed
    
    def _find_optimal_location_sequence(self, locations: List[str], travel_matrix: Dict[str, Dict[str, float]]) -> List[str]:
        """Find optimal sequence of locations to minimize travel time."""
        if len(locations) <= 2:
            return locations
        
        # Simplified greedy algorithm for demonstration
        # In practice, use more sophisticated optimization
        sequence = [locations[0]]
        remaining = set(locations[1:])
        
        current_location = locations[0]
        
        while remaining:
            # Find nearest location
            min_time = float('inf')
            next_location = None
            
            for location in remaining:
                travel_time = travel_matrix.get(current_location, {}).get(location, 1.0)
                if travel_time < min_time:
                    min_time = travel_time
                    next_location = location
            
            if next_location:
                sequence.append(next_location)
                remaining.remove(next_location)
                current_location = next_location
        
        return sequence
    
    def _recommend_shooting_order(self, location_scenes: Dict[str, Any]) -> List[str]:
        """Recommend optimal shooting order considering multiple factors."""
        # Sort locations by multiple criteria
        location_priorities = []
        
        for location_key, location_data in location_scenes.items():
            scene_count = len(location_data["scenes"])
            complexity_score = location_data["complexity_score"]
            
            # Priority factors
            priority_score = 0
            
            # More scenes = higher priority (efficiency)
            priority_score += scene_count * 2
            
            # Lower complexity first (warm-up)
            priority_score -= complexity_score * 0.1
            
            # Prefer interiors early (weather independent)
            if location_data["location_type"] == 'INT':
                priority_score += 1
            
            location_priorities.append((location_key, priority_score))
        
        # Sort by priority score (descending)
        location_priorities.sort(key=lambda x: x[1], reverse=True)
        
        return [location[0] for location in location_priorities]
    
    def _plan_logistics(self, scenes: List[Dict[str, Any]], location_grouping: Dict[str, Any]) -> Dict[str, Any]:
        """Plan detailed logistics for equipment and crew."""
        logistics = {
            "equipment_moves": [],
            "crew_transportation": {},
            "accommodation_needs": {},
            "catering_requirements": {},
            "storage_requirements": {}
        }
        
        location_clusters = location_grouping.get("location_clusters", {})
        
        # Plan equipment moves
        for i, (location_key, location_data) in enumerate(location_clusters.items()):
            if i > 0:  # Skip first location (no move needed)
                prev_location = list(location_clusters.keys())[i-1]
                
                # Estimate equipment needed
                equipment_needed = self._estimate_equipment_for_location(location_data)
                
                move_plan = {
                    "from": prev_location,
                    "to": location_key,
                    "equipment": equipment_needed,
                    "estimated_time": "2 hours",
                    "estimated_cost": self._estimate_move_cost(equipment_needed),
                    "crew_required": 4,  # Grips/gaffers for equipment move
                    "special_requirements": []
                }
                
                # Add special requirements
                if location_data["location_type"] == 'EXT':
                    move_plan["special_requirements"].append("Weather protection equipment")
                
                logistics["equipment_moves"].append(move_plan)
        
        # Plan crew transportation
        for location_key, location_data in location_clusters.items():
            estimated_crew_size = self._estimate_crew_size(location_data)
            
            logistics["crew_transportation"][location_key] = {
                "crew_size": estimated_crew_size,
                "transport_method": "Crew van" if estimated_crew_size <= 15 else "Multiple vehicles",
                "estimated_cost_per_day": estimated_crew_size * 25,  # $25 per person transport
                "pickup_time": "06:00",
                "return_time": "19:00"
            }
        
        # Accommodation needs
        for location_key, location_data in location_clusters.items():
            days_on_location = location_data["estimated_days"]
            
            if days_on_location > 1:
                logistics["accommodation_needs"][location_key] = {
                    "nights_required": days_on_location - 1,
                    "crew_size": self._estimate_crew_size(location_data),
                    "room_type": "Hotel/Motel",
                    "estimated_cost": (days_on_location - 1) * 150 * (self._estimate_crew_size(location_data) // 2)
                }
        
        # Catering requirements
        for location_key, location_data in location_clusters.items():
            crew_size = self._estimate_crew_size(location_data)
            cast_size = self._estimate_cast_size(location_data)
            
            logistics["catering_requirements"][location_key] = {
                "total_people": crew_size + cast_size,
                "meals_per_day": 2,  # Breakfast and lunch
                "estimated_cost_per_day": (crew_size + cast_size) * 40,
                "special_requirements": []
            }
            
            if location_data["location_type"] == 'EXT':
                logistics["catering_requirements"][location_key]["special_requirements"].append("Weather-protected catering area")
        
        return logistics
    
    def _estimate_equipment_for_location(self, location_data: Dict[str, Any]) -> List[str]:
        """Estimate equipment needed for a location."""
        equipment = [
            "Camera package",
            "Lighting kit",
            "Sound equipment",
            "Grip package"
        ]
        
        # Add location-specific equipment
        if location_data["location_type"] == 'EXT':
            equipment.extend(["Weather protection", "Generator", "Reflectors"])
        
        # Add complexity-based equipment
        if location_data["complexity_score"] > 10:
            equipment.extend(["Steadicam", "Additional cameras", "Specialty lenses"])
        
        return equipment
    
    def _estimate_move_cost(self, equipment_list: List[str]) -> str:
        """Estimate cost of equipment move."""
        base_cost = 800  # Base moving cost
        equipment_cost = len(equipment_list) * 100  # Additional cost per equipment type
        
        return f"${base_cost + equipment_cost:,}"
    
    def _estimate_crew_size(self, location_data: Dict[str, Any]) -> int:
        """Estimate crew size needed for location."""
        base_crew = 15  # Base crew size
        
        # Adjust for complexity
        complexity_adjustment = location_data["complexity_score"] // 5
        
        # Adjust for location type
        location_adjustment = 3 if location_data["location_type"] == 'EXT' else 0
        
        return base_crew + complexity_adjustment + location_adjustment
    
    def _estimate_cast_size(self, location_data: Dict[str, Any]) -> int:
        """Estimate cast size for location."""
        # Simplified estimation - in practice, analyze actual cast per scene
        return min(8, location_data["scene_count"] * 2)
    
    def _assess_permit_requirements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess permit requirements for all locations."""
        permits = {
            "location_permits": {},
            "permit_timeline": {},
            "estimated_costs": {},
            "regulatory_requirements": {}
        }
        
        # Analyze each unique location
        locations = set()
        for scene in scenes:
            location = scene.get('location', {})
            location_key = f"{location.get('place', 'Unknown')}_{location.get('type', 'INT')}"
            locations.add((location_key, location.get('place', 'Unknown'), location.get('type', 'INT')))
        
        for location_key, location_name, location_type in locations:
            permit_requirements = []
            estimated_cost = 0
            
            if location_type == 'EXT':
                permit_requirements.extend([
                    "City filming permit",
                    "Location use permit",
                    "Police coordination"
                ])
                estimated_cost += 500
                
                if 'street' in location_name.lower() or 'road' in location_name.lower():
                    permit_requirements.append("Street closure permit")
                    estimated_cost += 1000
                
                if 'park' in location_name.lower():
                    permit_requirements.append("Parks department permit")
                    estimated_cost += 300
            
            else:  # Interior
                permit_requirements.extend([
                    "Interior shooting permit",
                    "Building use agreement"
                ])
                estimated_cost += 200
                
                if 'office' in location_name.lower():
                    permit_requirements.append("Commercial space permit")
                    estimated_cost += 150
            
            # Common requirements
            permit_requirements.extend([
                "Insurance documentation",
                "Parking permits"
            ])
            estimated_cost += 100
            
            permits["location_permits"][location_key] = permit_requirements
            permits["estimated_costs"][location_key] = f"${estimated_cost:,}"
            
            # Timeline for permits
            permits["permit_timeline"][location_key] = {
                "application_deadline": "30 days before shooting",
                "approval_time": "14-21 days",
                "renewal_required": location_type == 'EXT'
            }
        
        # Regulatory requirements
        permits["regulatory_requirements"] = {
            "insurance_minimum": "$1,000,000 general liability",
            "bond_required": True,
            "fire_safety_coordinator": "Required for interior locations",
            "traffic_control": "Required for street filming"
        }
        
        return permits
    
    def _optimize_location_costs(self, scenes: List[Dict[str, Any]], logistics_planning: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize location-related costs."""
        cost_optimization = {
            "current_costs": {},
            "optimized_costs": {},
            "savings_opportunities": [],
            "cost_breakdown": {}
        }
        
        # Calculate current costs
        equipment_moves = logistics_planning.get("equipment_moves", [])
        crew_transportation = logistics_planning.get("crew_transportation", {})
        accommodation = logistics_planning.get("accommodation_needs", {})
        catering = logistics_planning.get("catering_requirements", {})
        
        total_current_cost = 0
        
        # Equipment move costs
        equipment_cost = sum(int(move["estimated_cost"].replace('$', '').replace(',', '')) for move in equipment_moves)
        total_current_cost += equipment_cost
        
        # Transportation costs
        transport_cost = sum(data["estimated_cost_per_day"] * 5 for data in crew_transportation.values())  # 5 days average
        total_current_cost += transport_cost
        
        # Accommodation costs
        accommodation_cost = sum(data["estimated_cost"] for data in accommodation.values())
        total_current_cost += accommodation_cost
        
        # Catering costs
        catering_cost = sum(data["estimated_cost_per_day"] * 5 for data in catering.values())  # 5 days average
        total_current_cost += catering_cost
        
        cost_optimization["current_costs"] = {
            "equipment_moves": f"${equipment_cost:,}",
            "crew_transportation": f"${transport_cost:,}",
            "accommodation": f"${accommodation_cost:,}",
            "catering": f"${catering_cost:,}",
            "total": f"${total_current_cost:,}"
        }
        
        # Optimization opportunities
        savings = []
        
        if len(equipment_moves) > 3:
            savings.append({
                "opportunity": "Reduce equipment moves by grouping nearby locations",
                "potential_savings": f"${equipment_cost * 0.2:,.0f}",
                "implementation": "Schedule geographically close locations consecutively"
            })
        
        if transport_cost > 10000:
            savings.append({
                "opportunity": "Negotiate crew transportation rates",
                "potential_savings": f"${transport_cost * 0.15:,.0f}",
                "implementation": "Bulk contract with transportation company"
            })
        
        if accommodation_cost > 5000:
            savings.append({
                "opportunity": "Secure group accommodation rates",
                "potential_savings": f"${accommodation_cost * 0.12:,.0f}",
                "implementation": "Block booking with hotels"
            })
        
        cost_optimization["savings_opportunities"] = savings
        
        # Calculate optimized costs
        total_savings = sum(float(saving["potential_savings"].replace('$', '').replace(',', '')) for saving in savings)
        optimized_total = total_current_cost - total_savings
        
        cost_optimization["optimized_costs"] = {
            "total_savings": f"${total_savings:,.0f}",
            "optimized_total": f"${optimized_total:,.0f}",
            "savings_percentage": f"{(total_savings / total_current_cost) * 100:.1f}%" if total_current_cost > 0 else "0%"
        }
        
        return cost_optimization
    
    def _generate_transportation_plan(self, scenes: List[Dict[str, Any]], logistics_planning: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed transportation plan."""
        transportation = {
            "daily_transport_schedule": {},
            "vehicle_requirements": {},
            "route_optimization": {},
            "contingency_plans": {}
        }
        
        crew_transportation = logistics_planning.get("crew_transportation", {})
        
        # Daily transport schedule
        for location_key, transport_data in crew_transportation.items():
            transportation["daily_transport_schedule"][location_key] = {
                "pickup_time": transport_data["pickup_time"],
                "return_time": transport_data["return_time"],
                "crew_size": transport_data["crew_size"],
                "transport_method": transport_data["transport_method"]
            }
        
        # Vehicle requirements
        max_crew_size = max((data["crew_size"] for data in crew_transportation.values()), default=0)
        
        if max_crew_size <= 8:
            vehicle_type = "1 crew van"
        elif max_crew_size <= 15:
            vehicle_type = "2 crew vans"
        else:
            vehicle_type = "3 crew vans + equipment truck"
        
        transportation["vehicle_requirements"] = {
            "primary_transport": vehicle_type,
            "equipment_transport": "1 equipment truck",
            "backup_transport": "1 additional van",
            "special_requirements": []
        }
        
        # Route optimization
        transportation["route_optimization"] = {
            "optimized_routes": "Minimize travel time between locations",
            "fuel_efficiency": "Group nearby locations",
            "traffic_considerations": "Avoid rush hour travel",
            "parking_arrangements": "Pre-arranged parking at each location"
        }
        
        # Contingency plans
        transportation["contingency_plans"] = {
            "vehicle_breakdown": "Backup vehicle on standby",
            "weather_delays": "Flexible pickup/return times",
            "traffic_delays": "Alternative routes mapped",
            "crew_size_changes": "Scalable transport solution"
        }
        
        return transportation
    
    def _generate_optimization_summary(self, location_grouping: Dict[str, Any], logistics_planning: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall optimization summary."""
        summary = {
            "efficiency_metrics": {},
            "cost_impact": {},
            "time_savings": {},
            "recommendations": []
        }
        
        # Efficiency metrics
        location_clusters = location_grouping.get("location_clusters", {})
        total_locations = len(location_clusters)
        total_estimated_days = sum(cluster["estimated_days"] for cluster in location_clusters.values())
        
        summary["efficiency_metrics"] = {
            "total_locations": total_locations,
            "estimated_shooting_days": total_estimated_days,
            "location_efficiency_score": location_grouping.get("shooting_efficiency", {}).get("location_efficiency_score", 0),
            "equipment_moves": len(logistics_planning.get("equipment_moves", []))
        }
        
        # High-level recommendations
        recommendations = [
            f"Optimize shooting schedule to {total_estimated_days} days across {total_locations} locations",
            f"Minimize equipment moves to {len(logistics_planning.get('equipment_moves', []))} transitions",
            "Group geographically close locations to reduce travel time",
            "Schedule weather-dependent exterior scenes with backup options"
        ]
        
        if total_locations > 5:
            recommendations.append("Consider location consolidation to reduce complexity")
        
        summary["recommendations"] = recommendations
        
        return summary