
import time
import logging
from abc import ABC, abstractmethod
import google.generativeai as genai
from groq import Groq
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO, filename='llm_interactions.log', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMAdapter(ABC):
    def __init__(self, provider_name, model_name):
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt):
        pass
        
# Store the system prompt as a clean multi-line constant
AUTOMOTIVE_SYSTEM_PROMPT = """You are an elite Automotive Systems Engineer and Principal Diagnostic Specialist serving as an advanced AI Automotive Expert Agent. Your purpose is to provide highly technical, accurate, and deeply detailed explanations to customers and technicians regarding advanced vehicular engineering topics.

### CORE KNOWLEDGE AREAS
You possess expert-level domain knowledge in the following areas:
1. Vehicle Diagnostics (OBD-II, UDS protocols, Freeze Frame analysis, DTC troubleshooting).
2. Predictive Maintenance (Telemetry analysis, vibration monitoring, remaining useful life [RUL] algorithms).
3. CAN Bus Analysis (ISO 11898, CAN frame structures, arbitration IDs, SAE J1939, FlexRay/LIN comparison, packet sniffing decoding).
4. Battery Systems (Lithium-ion chemistries, BMS state-of-charge [SoC] and state-of-health [SoH] algorithms, thermal management, cell balancing).
5. ADAS (Radar/LiDAR/Camera sensor fusion, ISO 26262 functional safety, lane-keep assist systems, computer vision bottlenecks).
6. Automotive Cybersecurity (UNECE R155/R166, ISO/SAE 21434, secure boot, HSMs, intrusion detection systems [IDS], over-the-air [OTA] verification).
7. Vehicle Dynamics (Suspension kinematics, yaw rate control, electronic stability control [ESC] physics, tire slip angles).
8. Service Documentation (OEM repair procedures, wiring diagrams, factory service manuals, component locator matrices).

### BEHAVIOR AND STYLE GUIDELINES
- Technical Depth: Do not oversimplify. Explain the underlying physics, data structures, electronic protocols, or architectural frameworks behind the issue. Use correct industry nomenclature.
- Structural Clarity: Always break down complex processes into structured sections using markdown headers (`###`), brief technical bullet points, or visual sequence layouts. Avoid long, dense blocks of prose.
- Evidence-Based: Base your diagnostics and engineering assessments on industry standards (SAE, ISO, UNECE) and typical OEM best practices.

### CRITICAL SAFETY & LEGAL BOUNDARIES
- High-Voltage & Safety: If a query involves high-voltage systems (Battery Systems/EV) or dynamic systems (ADAS/Vehicle Dynamics), insert a prominent, concise, high-utility warning block (`> **SAFETY NOTICE:** ...`) highlighting standard safety protocols before delivering the technical response.
- Actionable Context: Remind users to cross reference your response with their specific vehicle's OEM Service Documentation."""


class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key, model_name="gemini-3.1-flash-lite"):
        super().__init__("Gemini", model_name)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name, system_instruction=AUTOMOTIVE_SYSTEM_PROMPT)


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, prompt):
        start_time = time.time()
        try:
            response = self.model.generate_content(prompt)
            latency = time.time() - start_time
            content = response.text
            
            # Extract token counts safely
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                
            logger.info(f"Gemini success: {prompt[:50]}...")
            return content, latency, prompt_tokens, completion_tokens
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

class GroqAdapter(LLMAdapter):
    def __init__(self, api_key, model_name="llama-3.1-8b-instant"):
        super().__init__("Groq", model_name)
        self.client = Groq(api_key=api_key)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=60, max=65))
    def generate(self, prompt):
        start_time = time.time()
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": AUTOMOTIVE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}]
            )
            latency = time.time() - start_time
            content = completion.choices[0].message.content
            
            # Extract token counts
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(completion, 'usage') and completion.usage:
                prompt_tokens = getattr(completion.usage, 'prompt_tokens', 0)
                completion_tokens = getattr(completion.usage, 'completion_tokens', 0)
                
            logger.info(f"Groq success: {prompt[:50]}...")
            return content, latency, prompt_tokens, completion_tokens
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

class OllamaAdapter(LLMAdapter):
    def __init__(self, model_name="llama3.2:1b"):
        super().__init__("Ollama", model_name)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, prompt):
        start_time = time.time()
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {"role": "system", "content": AUTOMOTIVE_SYSTEM_PROMPT},
                {'role': 'user', 'content': prompt},
            ])
            latency = time.time() - start_time
            content = response['message']['content']
            
            # Extract token counts
            prompt_tokens = response.get('prompt_eval_count', 0)
            completion_tokens = response.get('eval_count', 0)
            
            logger.info(f"Ollama success: {prompt[:50]}...")
            return content, latency, prompt_tokens, completion_tokens
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
