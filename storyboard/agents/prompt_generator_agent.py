import logging
import os
import re
from typing import Dict, Any, List, Optional, Union
import asyncio

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class PromptGeneratorAgent:
    """Agent responsible for generating detailed image prompts from scene descriptions.
    
    This agent takes scene descriptions from a screenplay and converts them into
    detailed prompts suitable for AI image generation, capturing visual elements 
    like environment, lighting, framing, and mood.
    """
    
    def __init__(self):
        """Initialize the PromptGeneratorAgent with Google Gemini client and prompt templates."""
        logger.info("Initializing PromptGeneratorAgent")
        
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.google_api_key)
        
        # Shot type templates
        self.shot_templates = {
            "WS": "A wide establishing shot showing {scene}. Capture the entire environment and spatial relationships.",
            "MS": "A medium shot focusing on {subject} from waist up. Show character expressions and body language.",
            "CU": "A dramatic close-up of {subject}, emphasizing facial expressions and emotional detail.",
            "ECU": "An extreme close-up highlighting specific details of {subject}.",
            "OTS": "An over-the-shoulder shot looking past {subject} towards the scene.",
            "POV": "A point-of-view shot from {subject}'s perspective, showing what they see."
        }

        # Technical panel templates
        self.technical_templates = {
            "action": "Show the key moment of action with {description}",
            "reaction": "Capture the emotional reaction to {description}",
            "transition": "Establish the transition between scenes with {description}",
            "montage": "Create a montage effect showing {description}"
        }

        # Mood and atmosphere templates
        self.mood_templates = {
            "tense": "Create a tense atmosphere with dramatic shadows and confined space",
            "joyful": "Use bright, warm lighting and open composition",
            "mysterious": "Employ moody lighting and obscured elements",
            "melancholic": "Utilize muted colors and isolated composition"
        }

        self.prompt_template = """
        Create a detailed visual prompt for an AI image generator based on this scene description:
        
        SCENE: {scene_description}
        SHOT TYPE: {shot_type}
        TECHNICAL NOTES: {technical_notes}
        MOOD: {mood}
        
        Your prompt should:
        1. Include the key visual elements (setting, characters, actions)
        2. Specify camera angle, framing, and perspective
        3. Describe lighting, mood, and atmosphere
        4. Use specific, evocative, and concrete language
        5. Avoid dialogue or non-visual elements
        6. Keep the prompt under 200 words
        7. Format as a single paragraph without bullet points

        OUTPUT ONLY THE PROMPT, nothing else.
        """
    
    async def generate_prompts(self, scene_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate image prompts for a list of scenes with enhanced technical parameters."""
        scenes = scene_data.get('scenes', [])
        logger.info(f"Generating prompts for {len(scenes)} scenes")
        
        results = []
        for i, scene in enumerate(scenes):
            if isinstance(scene, str):
                scene_id = str(i + 1)
                scene_description = scene
                scene_heading = f"Scene {scene_id}"
                technical_params = {}
            else:
                scene_id = scene.get("scene_id") or scene.get("id") or str(i + 1)
                scene_heading = scene.get("scene_heading", f"Scene {scene_id}")
                scene_description = await self._extract_scene_description(scene)
                technical_params = scene.get("technical_params", {})
            
            if not scene_description:
                logger.warning(f"Scene {scene_id} has no description, skipping")
                continue
            
            try:
                # Generate the prompt with technical parameters
                prompt = await self._generate_single_prompt(
                    scene_description,
                    shot_type=technical_params.get("shot_type", "MS"),
                    technical_notes=technical_params.get("technical_notes", ""),
                    mood=technical_params.get("mood", "neutral")
                )
                
                result = {
                    "scene_id": scene_id,
                    "scene_heading": scene_heading,
                    "scene_description": scene_description,
                    "prompt": prompt,
                    "technical_params": technical_params
                }
                results.append(result)
                logger.info(f"Generated prompt for scene {scene_id}")
                
            except Exception as e:
                logger.error(f"Error generating prompt for scene {scene_id}: {str(e)}")
                results.append({
                    "scene_id": scene_id,
                    "scene_heading": scene_heading,
                    "error": str(e)
                })
        
        return results
    
    async def _generate_single_prompt(
        self, 
        scene_description: str,
        shot_type: str = "MS",
        technical_notes: str = "",
        mood: str = "neutral"
    ) -> str:
        """Generate a single image prompt with enhanced technical parameters."""
        try:
            # Apply shot type template if available
            shot_description = self.shot_templates.get(shot_type, "").format(
                scene=scene_description,
                subject="the subject"  # This could be extracted from scene analysis
            )

            # Apply mood template if available
            mood_description = self.mood_templates.get(mood, "")

            # Format the complete prompt template
            formatted_prompt = self.prompt_template.format(
                scene_description=scene_description,
                shot_type=shot_description,
                technical_notes=technical_notes,
                mood=mood_description
            )
            
            system_message = "You are a master cinematic storyboard artist."
            full_prompt = f"{system_message}\n\n{formatted_prompt}"
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=8000,
                    top_p=0.95,
                    top_k=20,
                    response_mime_type="application/json"
                )
            )
            
            # Safe content extraction
            def extract_content_safely(response):
                if not hasattr(response, 'candidates') or not response.candidates:
                    raise ValueError("No candidates in Gemini response")
                
                candidate = response.candidates[0]
                if not hasattr(candidate, 'content') or not candidate.content:
                    raise ValueError("Empty content in Gemini response")
                
                if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                    raise ValueError("No content parts in Gemini response")
                
                text_content = candidate.content.parts[0].text
                if not text_content:
                    raise ValueError("Empty text content in Gemini response")
                
                return text_content

            try:
                generated_prompt = extract_content_safely(response).strip()
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                # Return a basic prompt if extraction fails
                generated_prompt = f"A cinematic scene showing: {scene_description}"
            generated_prompt = re.sub(r'^(prompt:\s*|"|\')', '', generated_prompt, flags=re.IGNORECASE)
            generated_prompt = re.sub(r'("|\')\s*$', '', generated_prompt)
            
            return generated_prompt
            
        except Exception as e:
            logger.error(f"Error in prompt generation: {str(e)}")
            raise
    
    async def _extract_scene_description(self, scene: Dict[str, Any]) -> str:
        """Extract the scene description from various possible field names.
        
        Args:
            scene: A dictionary containing scene information
            
        Returns:
            The scene description text
        """
        # If scene is not a dictionary, return it as is
        if not isinstance(scene, dict):
            return str(scene)
            
        # Check different possible field names for scene description
        description_fields = ["description", "scene_description", "action", "scene_action"]
        
        for field in description_fields:
            if field in scene and scene[field]:
                return scene[field]
        
        # If no description is found, try to extract from dialogue
        if "dialogue" in scene and scene["dialogue"]:
            dialogue_entries = scene["dialogue"]
            if isinstance(dialogue_entries, list) and dialogue_entries:
                # Compile dialogue descriptions/actions
                descriptions = []
                for entry in dialogue_entries:
                    if isinstance(entry, dict):
                        # Extract character action/description if available
                        action = entry.get("action", "")
                        if action:
                            descriptions.append(action)
                
                if descriptions:
                    return " ".join(descriptions)
        
        # If no description is found, use scene heading as a fallback
        if "scene_heading" in scene and scene["scene_heading"]:
            return f"A scene showing {scene['scene_heading']}"
            
        return "" 