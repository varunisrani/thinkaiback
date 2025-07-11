from typing import Dict, Any, List
import json
import logging
from datetime import datetime
from ...base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CastingDirectorAgent:
    """
    👤 CastingDirectorAgent (GA BREAKDOWN)
    
    Specialized agent for casting breakdown and audition management.
    Responsibilities:
    - Lead cast categorization with union status tracking
    - Day rate estimation and budget planning
    - Audition scene selection and chemistry read coordination
    - Supporting cast and extras breakdown
    - Industry-standard casting materials generation
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Casting Director Agent for film production.
        Your expertise:
        1. Create comprehensive casting breakdowns with union classifications
        2. Estimate day rates and shooting schedules for each role
        3. Select optimal audition scenes and coordination requirements
        4. Categorize cast from leads to extras with specific requirements
        5. Generate industry-standard casting materials and notices"""
        logger.info("CastingDirectorAgent initialized")
    
    def analyze_casting_requirements(self, scene_data: Dict[str, Any], 
                                   character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive casting breakdown and requirements."""
        logger.info("Starting casting requirements analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        characters = character_data.get('characters', []) if character_data else []
        logger.info(f"Processing casting analysis for {len(characters)} characters across {len(scenes)} scenes")
        
        # Core casting analysis
        casting_categories = self._categorize_cast(characters, scenes)
        audition_requirements = self._generate_audition_requirements(characters, scenes)
        union_breakdown = self._analyze_union_requirements(casting_categories)
        budget_estimates = self._calculate_casting_budget(casting_categories, scenes)
        special_skills = self._identify_special_skills(characters, scenes)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "casting_categories": casting_categories,
            "audition_requirements": audition_requirements,
            "union_breakdown": union_breakdown,
            "budget_estimates": budget_estimates,
            "special_skills_requirements": special_skills,
            "casting_timeline": self._generate_casting_timeline(casting_categories)
        }
        
        logger.info(f"Generated casting analysis for {len(casting_categories)} character categories")
        return result
    
    def _categorize_cast(self, characters: List[Dict[str, Any]], 
                        scenes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize cast into industry-standard roles."""
        categories = {
            "lead_cast": [],
            "supporting_lead": [],
            "day_players": [],
            "one_line_people": [],
            "extras": []
        }
        
        total_scenes = len(scenes)
        
        for char in characters:
            char_name = char.get('name', '')
            total_character_scenes = char.get('total_scenes', 0)
            dialogue_count = char.get('dialogue_count', 0)
            scene_percentage = (total_character_scenes / total_scenes) * 100 if total_scenes > 0 else 0
            
            # Calculate estimated shoot days (industry standard: 3-5 pages per day)
            estimated_shoot_days = max(int(total_character_scenes * 0.6), 1)
            
            casting_info = {
                "character": char_name,
                "scene_count": total_character_scenes,
                "dialogue_percentage": round((dialogue_count / sum(c.get('dialogue_count', 0) for c in characters)) * 100, 1) if characters else 0,
                "estimated_shoot_days": estimated_shoot_days,
                "scene_percentage": round(scene_percentage, 1)
            }
            
            # Categorization logic based on industry standards
            if scene_percentage >= 60 and dialogue_count >= 20:
                casting_info.update({
                    "category": "Lead",
                    "union_status": "SAG-AFTRA",
                    "day_rate_range": "$2,500-$5,000",
                    "contract_type": "Series Regular"
                })
                categories["lead_cast"].append(casting_info)
            
            elif scene_percentage >= 30 and dialogue_count >= 10:
                casting_info.update({
                    "category": "Supporting Lead", 
                    "union_status": "SAG-AFTRA",
                    "day_rate_range": "$1,200-$2,500",
                    "contract_type": "Recurring Guest"
                })
                categories["supporting_lead"].append(casting_info)
            
            elif scene_percentage >= 15 or dialogue_count >= 5:
                casting_info.update({
                    "category": "Day Player",
                    "union_status": "SAG-AFTRA",
                    "day_rate_range": "$630-$1,200",
                    "contract_type": "Guest Star"
                })
                categories["day_players"].append(casting_info)
            
            elif dialogue_count > 0:
                casting_info.update({
                    "category": "One-Line",
                    "union_status": "SAG-AFTRA",
                    "day_rate_range": "$380-$630",
                    "contract_type": "Co-Star"
                })
                categories["one_line_people"].append(casting_info)
            
            else:
                casting_info.update({
                    "category": "Background",
                    "union_status": "Non-Union/Union",
                    "day_rate_range": "$150-$200",
                    "contract_type": "Background"
                })
                categories["extras"].append(casting_info)
        
        return categories
    
    def _generate_audition_requirements(self, characters: List[Dict[str, Any]], 
                                      scenes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate audition requirements for each character."""
        audition_requirements = {}
        
        for char in characters:
            char_name = char.get('name', '')
            dialogue_count = char.get('dialogue_count', 0)
            total_scenes = char.get('total_scenes', 0)
            
            if dialogue_count > 0:  # Only speaking roles need auditions
                # Select audition scenes (typically 2-3 scenes that showcase range)
                audition_scenes = self._select_audition_scenes(char_name, scenes)
                
                # Identify special skills from scene analysis
                special_skills = self._extract_character_skills(char_name, scenes)
                
                # Determine chemistry reads needed
                chemistry_reads = self._identify_chemistry_reads(char_name, characters, scenes)
                
                audition_requirements[char_name] = {
                    "audition_scenes": audition_scenes,
                    "special_skills": special_skills,
                    "chemistry_reads_with": chemistry_reads,
                    "sides_length": "2-3 pages",
                    "prep_time_required": "24-48 hours",
                    "callback_recommended": dialogue_count > 10,
                    "self_tape_acceptable": total_scenes <= 3
                }
        
        return audition_requirements
    
    def _select_audition_scenes(self, character: str, scenes: List[Dict[str, Any]]) -> List[str]:
        """Select optimal scenes for character auditions."""
        character_scenes = []
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            main_characters = scene.get('main_characters', [])
            dialogues = scene.get('dialogues', [])
            
            # Check if character appears in scene
            char_in_scene = character in main_characters
            char_has_dialogue = any(d.get('character') == character for d in dialogues)
            
            if char_in_scene or char_has_dialogue:
                # Calculate dialogue intensity for this character in this scene
                char_dialogue_count = sum(1 for d in dialogues if d.get('character') == character)
                if char_dialogue_count >= 2:  # Scenes with substantial dialogue
                    character_scenes.append({
                        "scene": scene_number,
                        "dialogue_count": char_dialogue_count,
                        "description": scene.get('description', '')[:100]
                    })
        
        # Sort by dialogue count and select top 2-3 scenes
        character_scenes.sort(key=lambda x: x["dialogue_count"], reverse=True)
        return [f"Scene {s['scene']}" for s in character_scenes[:3]]
    
    def _extract_character_skills(self, character: str, scenes: List[Dict[str, Any]]) -> List[str]:
        """Extract special skills required for character from scene descriptions."""
        skills = set()
        
        for scene in scenes:
            main_characters = scene.get('main_characters', [])
            description = scene.get('description', '').lower()
            
            if character in main_characters:
                # Identify skills from scene description
                if any(keyword in description for keyword in ['drive', 'driving', 'car']):
                    skills.add('Driving')
                if any(keyword in description for keyword in ['fight', 'combat', 'action']):
                    skills.add('Fight choreography')
                if any(keyword in description for keyword in ['sing', 'music', 'song']):
                    skills.add('Singing')
                if any(keyword in description for keyword in ['dance', 'dancing']):
                    skills.add('Dancing')
                if any(keyword in description for keyword in ['horse', 'riding']):
                    skills.add('Horseback riding')
                if any(keyword in description for keyword in ['swim', 'water']):
                    skills.add('Swimming')
                if any(keyword in description for keyword in ['instrument', 'guitar', 'piano']):
                    skills.add('Musical instrument')
        
        return list(skills)
    
    def _identify_chemistry_reads(self, character: str, characters: List[Dict[str, Any]], 
                                 scenes: List[Dict[str, Any]]) -> List[str]:
        """Identify which characters need chemistry reads together."""
        chemistry_partners = set()
        
        for scene in scenes:
            main_characters = scene.get('main_characters', [])
            if character in main_characters and len(main_characters) > 1:
                # Look for scenes with intimate or relationship-heavy dialogue
                description = scene.get('description', '').lower()
                if any(keyword in description for keyword in ['romantic', 'love', 'kiss', 'relationship']):
                    for other_char in main_characters:
                        if other_char != character:
                            chemistry_partners.add(other_char)
        
        return list(chemistry_partners)
    
    def _analyze_union_requirements(self, casting_categories: Dict[str, List]) -> Dict[str, Any]:
        """Analyze union requirements and compliance."""
        sag_aftra_count = 0
        non_union_count = 0
        total_roles = 0
        
        for category, roles in casting_categories.items():
            for role in roles:
                total_roles += 1
                if role.get('union_status') == 'SAG-AFTRA':
                    sag_aftra_count += 1
                else:
                    non_union_count += 1
        
        return {
            "total_roles": total_roles,
            "sag_aftra_roles": sag_aftra_count,
            "non_union_roles": non_union_count,
            "sag_aftra_percentage": round((sag_aftra_count / total_roles) * 100, 1) if total_roles > 0 else 0,
            "taft_hartley_needed": non_union_count > 0,
            "signatory_required": sag_aftra_count > 0
        }
    
    def _calculate_casting_budget(self, casting_categories: Dict[str, List], 
                                 scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate estimated casting budget."""
        budget_breakdown = {}
        total_estimated_cost = 0
        
        for category, roles in casting_categories.items():
            category_cost = 0
            for role in roles:
                # Extract day rate range and calculate average
                day_rate_range = role.get('day_rate_range', '$0-$0')
                try:
                    min_rate = int(day_rate_range.split('-')[0].replace('$', '').replace(',', ''))
                    max_rate = int(day_rate_range.split('-')[1].replace('$', '').replace(',', ''))
                    avg_rate = (min_rate + max_rate) / 2
                except:
                    avg_rate = 500  # Default rate
                
                shoot_days = role.get('estimated_shoot_days', 1)
                role_cost = avg_rate * shoot_days
                category_cost += role_cost
                
                role['estimated_total_cost'] = role_cost
            
            budget_breakdown[category] = {
                "role_count": len(roles),
                "total_cost": category_cost,
                "average_cost_per_role": category_cost / len(roles) if roles else 0
            }
            total_estimated_cost += category_cost
        
        return {
            "category_breakdown": budget_breakdown,
            "total_estimated_cost": total_estimated_cost,
            "contingency_recommended": total_estimated_cost * 0.1,
            "total_with_contingency": total_estimated_cost * 1.1
        }
    
    def _identify_special_skills(self, characters: List[Dict[str, Any]], 
                               scenes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify special skills requirements across all characters."""
        skills_by_character = {}
        
        for char in characters:
            char_name = char.get('name', '')
            skills = self._extract_character_skills(char_name, scenes)
            if skills:
                skills_by_character[char_name] = skills
        
        return skills_by_character
    
    def _generate_casting_timeline(self, casting_categories: Dict[str, List]) -> Dict[str, str]:
        """Generate recommended casting timeline."""
        timeline = {}
        
        # Lead cast should be cast first
        if casting_categories.get('lead_cast'):
            timeline['lead_cast'] = "Weeks 1-2: Auditions, callbacks, chemistry reads"
        
        if casting_categories.get('supporting_lead'):
            timeline['supporting_lead'] = "Weeks 2-3: Auditions and callbacks"
        
        if casting_categories.get('day_players'):
            timeline['day_players'] = "Weeks 3-4: Auditions"
        
        if casting_categories.get('one_line_people'):
            timeline['one_line_people'] = "Weeks 4-5: Self-tapes and quick auditions"
        
        if casting_categories.get('extras'):
            timeline['extras'] = "Week 5-6: Background casting and fittings"
        
        return timeline