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

class DialogueProfilerAgent:
    """
    👤 DialogueProfilerAgent (SPEECH ANALYSIS)
    
    Specialized agent for dialogue analysis and speech pattern recognition.
    Responsibilities:
    - Voice profile creation with tone and vocabulary analysis
    - Emotional range mapping and vocal demands assessment
    - Language requirements identification
    - Speech pattern complexity analysis
    - Accent and vocal coaching needs
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Dialogue Profiler Agent for film production.
        Your expertise:
        1. Analyze speech patterns, tone, and vocabulary for each character
        2. Create detailed voice profiles with emotional range assessment
        3. Identify accent requirements and vocal coaching needs
        4. Calculate dialogue complexity and vocal demands
        5. Generate comprehensive speech analysis for casting directors"""
        logger.info("DialogueProfilerAgent initialized")
    
    def profile_dialogue(self, scene_data: Dict[str, Any], character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze character dialogues and speech patterns for casting directors."""
        logger.info("Starting dialogue profiling analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing dialogue profiling for {len(scenes)} scenes")
        
        try:
            # Create voice profiles for each character
            voice_profiles = self._create_voice_profiles(scenes, character_data)
            dialogue_complexity = self._analyze_dialogue_complexity(scenes)
            language_requirements = self._identify_language_requirements(scenes)
            vocal_demands = self._assess_vocal_demands(scenes)
            
            result = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "voice_profiles": voice_profiles,
                "dialogue_complexity": dialogue_complexity,
                "language_requirements": language_requirements,
                "vocal_demands": vocal_demands,
                "casting_notes": self._generate_casting_notes(voice_profiles)
            }
            
            logger.info(f"Generated dialogue profiling for {len(voice_profiles)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error in dialogue profiling: {str(e)}")
            return {"error": str(e)}
    
    def _create_voice_profiles(self, scenes: List[Dict[str, Any]], 
                              character_data: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """Create detailed voice profiles for each character."""
        voice_profiles = {}
        
        # Extract characters from scenes
        characters = set()
        for scene in scenes:
            dialogues = scene.get('dialogues', [])
            for dialogue in dialogues:
                char_name = dialogue.get('character', '')
                if char_name:
                    characters.add(char_name)
        
        # Build voice profiles
        for char_name in characters:
            char_dialogues = []
            for scene in scenes:
                dialogues = scene.get('dialogues', [])
                char_dialogues.extend([d for d in dialogues if d.get('character') == char_name])
            
            if char_dialogues:
                voice_profiles[char_name] = {
                    "tone": self._analyze_tone(char_dialogues),
                    "vocabulary": self._analyze_vocabulary(char_dialogues),
                    "emotional_range": self._analyze_emotional_range(char_dialogues),
                    "accent_requirements": self._identify_accent_requirements(char_dialogues),
                    "vocal_demands": self._calculate_vocal_demands(char_dialogues),
                    "speech_patterns": self._identify_speech_patterns(char_dialogues)
                }
        
        return voice_profiles
    
    def _analyze_tone(self, dialogues: List[Dict[str, Any]]) -> str:
        """Analyze the overall tone of character's dialogue."""
        if not dialogues:
            return "Neutral"
        
        # Analyze dialogue text for tone indicators
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        
        # Basic tone analysis based on keywords
        if any(word in dialogue_text for word in ['please', 'thank you', 'excuse me']):
            return "Polite and professional"
        elif any(word in dialogue_text for word in ['damn', 'hell', 'shit']):
            return "Aggressive and direct"
        elif any(word in dialogue_text for word in ['love', 'dear', 'sweetheart']):
            return "Warm and affectionate"
        elif any(word in dialogue_text for word in ['boss', 'sir', 'ma\'am']):
            return "Respectful and formal"
        else:
            return "Direct and conversational"
    
    def _analyze_vocabulary(self, dialogues: List[Dict[str, Any]]) -> str:
        """Analyze vocabulary complexity and style."""
        if not dialogues:
            return "Standard vocabulary"
        
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        word_count = len(dialogue_text.split())
        
        # Basic vocabulary analysis
        if any(word in dialogue_text for word in ['consequently', 'furthermore', 'nevertheless']):
            return "Sophisticated and educated"
        elif any(word in dialogue_text for word in ['ain\'t', 'gonna', 'wanna']):
            return "Casual with colloquialisms"
        elif any(word in dialogue_text for word in ['protocol', 'procedure', 'analysis']):
            return "Technical and professional"
        else:
            return "Standard conversational"
    
    def _analyze_emotional_range(self, dialogues: List[Dict[str, Any]]) -> List[str]:
        """Identify emotional range requirements for the character."""
        emotions = set()
        
        for dialogue in dialogues:
            text = dialogue.get('text', '').lower()
            
            # Identify emotions from dialogue content
            if any(word in text for word in ['angry', 'mad', 'furious']):
                emotions.add('Anger')
            if any(word in text for word in ['sad', 'cry', 'tears']):
                emotions.add('Sadness')
            if any(word in text for word in ['happy', 'joy', 'excited']):
                emotions.add('Joy')
            if any(word in text for word in ['scared', 'afraid', 'terrified']):
                emotions.add('Fear')
            if any(word in text for word in ['love', 'adore', 'care']):
                emotions.add('Love')
            if any(word in text for word in ['determined', 'focused', 'will']):
                emotions.add('Determination')
            if any(word in text for word in ['vulnerable', 'hurt', 'broken']):
                emotions.add('Vulnerability')
        
        return list(emotions) if emotions else ['Neutral']
    
    def _identify_accent_requirements(self, dialogues: List[Dict[str, Any]]) -> str:
        """Identify accent or dialect requirements."""
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        
        # Look for dialect indicators
        if any(word in dialogue_text for word in ['y\'all', 'fixin\'', 'reckon']):
            return "Southern American"
        elif any(word in dialogue_text for word in ['bloody', 'bloke', 'mate']):
            return "British"
        elif any(word in dialogue_text for word in ['eh', 'about', 'house']):
            return "Canadian"
        elif any(word in dialogue_text for word in ['oy', 'crikey', 'fair dinkum']):
            return "Australian"
        else:
            return "Neutral American"
    
    def _calculate_vocal_demands(self, dialogues: List[Dict[str, Any]]) -> str:
        """Calculate vocal demands for the role."""
        if not dialogues:
            return "Low"
        
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        total_words = len(dialogue_text.split())
        
        # Analyze vocal intensity
        shouting_indicators = dialogue_text.count('!') + dialogue_text.count('yell') + dialogue_text.count('shout')
        singing_indicators = dialogue_text.count('sing') + dialogue_text.count('song')
        
        if total_words > 500 or shouting_indicators > 5 or singing_indicators > 0:
            return "High - extensive dialogue, shouting, or singing required"
        elif total_words > 200 or shouting_indicators > 2:
            return "Medium - moderate dialogue with some vocal intensity"
        else:
            return "Low - minimal dialogue requirements"
    
    def _identify_speech_patterns(self, dialogues: List[Dict[str, Any]]) -> List[str]:
        """Identify specific speech patterns or quirks."""
        patterns = []
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        
        # Identify speech patterns
        if dialogue_text.count('um') > 2 or dialogue_text.count('uh') > 2:
            patterns.append("Hesitant speech with fillers")
        if dialogue_text.count('...') > 3:
            patterns.append("Frequent pauses or trailing off")
        if dialogue_text.count('?') > len(dialogues) * 0.3:
            patterns.append("Questioning and uncertain")
        if len([d for d in dialogues if len(d.get('text', '').split()) < 3]) > len(dialogues) * 0.5:
            patterns.append("Short, clipped responses")
        
        return patterns if patterns else ["Standard speech patterns"]
    
    def _analyze_dialogue_complexity(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall dialogue complexity across all scenes."""
        total_dialogues = 0
        total_words = 0
        long_speeches = 0
        
        for scene in scenes:
            dialogues = scene.get('dialogues', [])
            total_dialogues += len(dialogues)
            
            for dialogue in dialogues:
                text = dialogue.get('text', '')
                word_count = len(text.split())
                total_words += word_count
                
                if word_count > 50:  # Long speech
                    long_speeches += 1
        
        return {
            "average_line_length": round(total_words / total_dialogues, 1) if total_dialogues > 0 else 0,
            "total_dialogue_blocks": total_dialogues,
            "total_words": total_words,
            "long_speeches": long_speeches,
            "complexity_level": "High" if total_words > 2000 else "Medium" if total_words > 1000 else "Low"
        }
    
    def _identify_language_requirements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify language requirements for the production."""
        languages = {"primary": "English", "secondary": []}
        
        # Basic language detection from dialogue content
        all_dialogue = ""
        for scene in scenes:
            dialogues = scene.get('dialogues', [])
            all_dialogue += ' '.join([d.get('text', '') for d in dialogues])
        
        # Look for non-English phrases (simplified detection)
        if any(phrase in all_dialogue.lower() for phrase in ['si', 'oui', 'ja', 'da']):
            languages["secondary"].append("Foreign language phrases")
        
        return languages
    
    def _assess_vocal_demands(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess vocal demands across all characters."""
        vocal_assessment = {
            "overall_demands": "Medium",
            "special_requirements": [],
            "coaching_needed": []
        }
        
        # Analyze scene descriptions for vocal requirements
        for scene in scenes:
            description = scene.get('description', '').lower()
            
            if 'singing' in description or 'song' in description:
                vocal_assessment["special_requirements"].append("Singing ability required")
            if 'shouting' in description or 'yelling' in description:
                vocal_assessment["special_requirements"].append("Strong vocal projection needed")
            if 'whisper' in description:
                vocal_assessment["special_requirements"].append("Intimate vocal control required")
        
        return vocal_assessment
    
    def _generate_casting_notes(self, voice_profiles: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate casting notes based on voice profiles."""
        casting_notes = []
        
        for char_name, profile in voice_profiles.items():
            note = {
                "character": char_name,
                "casting_priority": "High" if profile["vocal_demands"].startswith("High") else "Medium",
                "voice_requirements": f"{profile['tone']} with {profile['vocabulary']}",
                "special_notes": f"Accent: {profile['accent_requirements']}, Emotional range: {', '.join(profile['emotional_range'][:3])}"
            }
            casting_notes.append(note)
        
        return casting_notes