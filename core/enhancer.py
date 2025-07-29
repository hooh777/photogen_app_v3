# core/enhancer.py
import os
import abc
import google.generativeai as genai
from openai import OpenAI
from groq import Groq
from PIL import Image
import numpy as np
import logging

from core import constants as const

class Enhancer(abc.ABC):
    """Abstract base class for all prompt enhancers."""
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.setup_client()

    @abc.abstractmethod
    def setup_client(self):
        """Sets up the specific API client."""
        pass

    @abc.abstractmethod
    def enhance(self, base_prompt, image=None):
        """The main method to enhance a prompt, now accepting an optional image."""
        pass

    def get_instruction(self, base_prompt, has_image=False):
        """Generates a universal instruction for any LLM by reading from prompt_guide.md."""
        image_context_instruction = (
            "You have been provided with an image. First, briefly analyze the key subjects, style, and composition of the image. "
            "Then, use that analysis to inform your three prompt variations. The prompts should be relevant to modifying or building upon the provided image."
            if has_image
            else ""
        )

        try:
            with open('prompt_guide.md', 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logging.error("prompt_guide.md not found. Please ensure the file exists in the main project directory.")
            # Fallback to a basic instruction if the file is missing
            prompt_template = "Enhance this prompt: {base_prompt}"

        return prompt_template.format(
            image_context_instruction=image_context_instruction,
            base_prompt=base_prompt
        )

    def parse_response(self, text):
        """Parses the LLM's response text."""
        parts = text.split('---')
        detailed = parts[0].strip() if len(parts) > 0 else "Could not generate."
        stylized = parts[1].strip() if len(parts) > 1 else "Could not generate."
        rephrased = parts[2].strip() if len(parts) > 2 else "Could not generate."
        return detailed, stylized, rephrased

class GeminiEnhancer(Enhancer):
    def setup_client(self):
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def enhance(self, base_prompt, image=None):
        instruction = self.get_instruction(base_prompt, has_image=(image is not None))
        content = [instruction]
        if image is not None:
            pil_image = Image.fromarray(image)
            content.insert(0, pil_image)
        try:
            response = self.model.generate_content(content)
            return self.parse_response(response.text)
        except Exception as e:
            logging.error("Gemini API Error", exc_info=True)
            return f"API Error: {e}", f"API Error: {e}", f"API Error: {e}"

class OpenAIEnhancer(Enhancer):
    def setup_client(self):
        self.client = OpenAI(api_key=self.api_key)

    def enhance(self, base_prompt, image=None):
        instruction = self.get_instruction(base_prompt, has_image=(image is not None))
        messages = [{"role": "user", "content": instruction}]
        # NOTE: Full vision support for OpenAI requires encoding the image and adding it to the message list.
        # This is a placeholder for text-only enhancement.
        if image is not None:
            logging.info("OpenAI vision enhancement called (image data not yet fully implemented in this example).")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", messages=messages
            )
            return self.parse_response(response.choices[0].message.content)
        except Exception as e:
            logging.error("OpenAI API Error", exc_info=True)
            return f"API Error: {e}", f"API Error: {e}", f"API Error: {e}"

class GroqEnhancer(Enhancer):
    def setup_client(self): self.client = Groq(api_key=self.api_key)
    def enhance(self, base_prompt, image=None):
        if image is not None: return "This provider does not support images.", "", ""
        instruction = self.get_instruction(base_prompt)
        try:
            response = self.client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": instruction}])
            return self.parse_response(response.choices[0].message.content)
        except Exception as e: 
            logging.error("Groq API Error", exc_info=True)
            return f"API Error: {e}", f"API Error: {e}", f"API Error: {e}"

class XaiEnhancer(Enhancer):
    def setup_client(self): self.client = OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
    def enhance(self, base_prompt, image=None):
        if image is not None: return "This provider does not support images.", "", ""
        instruction = self.get_instruction(base_prompt)
        try:
            response = self.client.chat.completions.create(model="grok-4", messages=[{"role": "user", "content": instruction}])
            return self.parse_response(response.choices[0].message.content)
        except Exception as e: 
            logging.error("X.ai API Error", exc_info=True)
            return f"API Error: {e}", f"API Error: {e}", f"API Error: {e}"

ENHANCER_MAP = {
    const.GOOGLE_GEMINI: GeminiEnhancer,
    const.OPENAI_GPT: OpenAIEnhancer,
    const.GROQ_CLOUD: GroqEnhancer,
    const.GROK_3: XaiEnhancer,
}

def get_enhancer(provider_name, api_key):
    enhancer_class = ENHANCER_MAP.get(provider_name)
    if not enhancer_class:
        raise ValueError(f"Invalid provider selected: {provider_name}")
    return enhancer_class(api_key=api_key)