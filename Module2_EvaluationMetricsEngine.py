
import os
import math
import string
import logging
import json
import re
from collections import Counter
from google import genai

logger = logging.getLogger("metrics_engine")

# ---------------------------------------------------------
# Hallucination Data and Logic
# ---------------------------------------------------------

# Comprehensive database of valid standard automotive DTC codes
VALID_DTCS = {
    # Powertrain (P)
    "P0001", "P0002", "P0003", "P0004", "P0010", "P0011", "P0012", "P0013", "P0014", "P0015",
    "P0100", "P0101", "P0102", "P0103", "P0104", "P0110", "P0111", "P0112", "P0113", "P0114",
    "P0115", "P0116", "P0120", "P0121", "P0122", "P0123", "P0130", "P0131", "P0132", "P0133",
    "P0135", "P0171", "P0172", "P0300", "P0301", "P0302", "P0303", "P0304", "P0305", "P0306",
    "P0307", "P0308", "P0400", "P0401", "P0402", "P0410", "P0420", "P0430", "P0440", "P0442",
    "P0443", "P0455", "P0500", "P0501", "P0502", "P0503", "P0600", "P0700", "P0701", "P0705",
    "P0706", "P0750", "P0A80", "P0A90",
    # Network/Communication (U)
    "U0001", "U0002", "U0100", "U0101", "U0121", "U0155",
    # Body (B)
    "B0001", "B0002", "B0010", "B0020",
    # Chassis (C)
    "C0034", "C0035", "C0040", "C0045"
}

# Valid automotive ISO & SAE standard numbers
VALID_STANDARDS = {
    "iso": {
        "11898",  # CAN
        "26262",  # Functional Safety
        "14229",  # UDS
        "15765",  # Diagnostics on CAN (DoCAN)
        "21434",  # Cybersecurity
        "9141",   # K-Line
        "15031",  # OBD
        "13400",  # DoIP
        "15118",  # V2G charging
        "16750"   # Environmental conditions
    },
    "sae": {
        "1939",   # J1939 (Heavy duty)
        "1850",   # J1850
        "2012",   # J2012 (DTC definitions)
        "3061",   # J3061 (Cybersecurity guidebook)
        "1979",   # J1979 (OBD regulations)
        "2534"    # J2534 (Pass-thru programming)
    }
}

def load_dtc_codes(base_dir):
    all_codes = set()
    try:
        if os.path.exists(base_dir):
            for filename in os.listdir(base_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(base_dir, filename), 'r') as f:
                        data = json.load(f)
                        all_codes.update(data.keys())
        else:
            logger.warning(f"DTC directory {base_dir} not found. Using defaults.")
    except Exception as e:
        logger.error(f"Error loading DTC codes: {e}")
    return all_codes

# Load real DTCs if directory exists, otherwise use standard set
DTC_CODES_DIR = "dtc-codes"
REAL_DTCS = load_dtc_codes(DTC_CODES_DIR)

class HallucinationDetector:
    def __init__(self, gemini_api_key: str = None):
        self.client = None
        self.valid_dtcs = REAL_DTCS if REAL_DTCS else VALID_DTCS
        if gemini_api_key:
            try:
                self.client = genai.Client(api_key=gemini_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client for detector: {e}")

    def detect_heuristics(self, text: str) -> dict:
        non_existent_dtcs = []
        fabricated_sensor_specs = []
        unsupported_standards = []

        dtc_pattern = re.compile(r'\b([PCBU]\d{4})\b', re.IGNORECASE)
        found_dtcs = dtc_pattern.findall(text)
        for dtc in found_dtcs:
            dtc_upper = dtc.upper()
            if dtc_upper not in self.valid_dtcs:
                if dtc_upper.startswith("P030") and dtc_upper[-1] in "12345678":
                    continue
                non_existent_dtcs.append(dtc_upper)

        # Sensor checks
        o2_volts = re.findall(r'(?:O2|oxygen|lambd[ae])\s+sensor\s+voltage.*?(\d+(?:\.\d+)?)\s*(?:V|volt)', text, re.IGNORECASE)
        for val in o2_volts:
            if float(val) > 2.0:
                fabricated_sensor_specs.append(f"Narrow-band O2 sensor voltage of {val}V (should be 0-1V)")

        can_volts = re.findall(r'(?:CAN\s+High|CAN\s+Low|CAN\s+signal|CAN\s+differential).*?(\d+(?:\.\d+)?)\s*(?:V|volt)', text, re.IGNORECASE)
        for val in can_volts:
            if float(val) > 6.0:
                fabricated_sensor_specs.append(f"CAN signal voltage of {val}V (should be ~1.5V - ~3.5V)")

        # Standards
        iso_matches = re.findall(r'\bISO\s*(\d+)\b', text, re.IGNORECASE)
        for iso in iso_matches:
            if iso not in VALID_STANDARDS["iso"] and not iso.startswith("900"):
                unsupported_standards.append(f"ISO {iso}")
        
        sae_matches = re.findall(r'\bSAE\s*J(\d+)\b', text, re.IGNORECASE)
        for sae in sae_matches:
            if sae not in VALID_STANDARDS["sae"]:
                unsupported_standards.append(f"SAE J{sae}")

        has_hallucinations = bool(non_existent_dtcs or fabricated_sensor_specs or unsupported_standards)
        return {
            "has_hallucinations": has_hallucinations,
            "hallucinations_detected": non_existent_dtcs + fabricated_sensor_specs + unsupported_standards
        }

    def detect_llm_hallucinations(self, prompt: str, response: str) -> dict:
        if not self.client:
            return {"has_contradictions": False, "contradictions": []}
        
        evaluation_prompt = f"""Identify technical contradictions or fabricated facts in the response.
Prompt: {prompt}
Response: {response}
Provide analysis in JSON: {{"has_contradictions_or_errors": bool, "contradictions": [], "factual_errors": []}}"""
        try:
            res = self.client.models.generate_content(
                model="gemini-3.1-flash-lite", # Use latest
                contents=evaluation_prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(res.text)
            return {
                "has_contradictions": data.get("has_contradictions_or_errors", False),
                "contradictions": data.get("contradictions", []) + data.get("factual_errors", [])
            }
        except Exception:
            return {"has_contradictions": False, "contradictions": []}

    def analyze(self, prompt: str, response: str) -> dict:
        heuristics = self.detect_heuristics(response)
        llm_checks = self.detect_llm_hallucinations(prompt, response)
        all_h = heuristics["hallucinations_detected"] + llm_checks["contradictions"]
        return {
            "has_hallucinations": heuristics["has_hallucinations"] or llm_checks["has_contradictions"],
            "hallucinations_detected": all_h
        }

# ---------------------------------------------------------
# Metrics Engine
# ---------------------------------------------------------

def calculate_cosine_similarity(text1: str, text2: str) -> float:
    def tokenize(t):
        t = t.lower().translate(str.maketrans("", "", string.punctuation))
        return t.split()
    words1, words2 = tokenize(text1), tokenize(text2)
    if not words1 or not words2: return 0.0
    vec1, vec2 = Counter(words1), Counter(words2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum(vec1[word] * vec2[word] for word in intersection)
    norm1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
    norm2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

class MetricsEngine:
    def __init__(self, gemini_api_key: str = None):
        self.client = None
        if gemini_api_key:
            try:
                self.client = genai.Client(api_key=gemini_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client for metrics: {e}")

    def compute_length_metrics(self, response_text: str, output_tokens: int) -> dict:
        words = response_text.split()
        word_count = len(words)
        char_count = len(response_text)
        comp_ratio = char_count / output_tokens if output_tokens > 0 else 0.0
        unique_words = set(w.lower() for w in words)
        info_density = len(unique_words) / word_count if word_count > 0 else 0.0
        return {
            "word_count": word_count,
            "token_count": output_tokens,
            "compression_ratio": comp_ratio,
            "info_density": info_density
        }

    def compute_latency_metrics(self, latency, token_count):
        tps = token_count / latency if latency > 0 else 0
        return {"latency": latency, "tps": tps}

    def compute_consistency_metrics(self, responses_list: list, token_counts: list) -> dict:
        if not responses_list: return {}
        n = len(responses_list)
        word_counts = [len(r.split()) for r in responses_list]
        mean_word = sum(word_counts) / n
        mean_token = sum(token_counts) / n
        std_word = math.sqrt(sum((x - mean_word) ** 2 for x in word_counts) / n)
        std_token = math.sqrt(sum((x - mean_token) ** 2 for x in token_counts) / n)
        similarities = [calculate_cosine_similarity(responses_list[i], responses_list[j]) 
                        for i in range(n) for j in range(i + 1, n)]
        avg_semantic = sum(similarities) / len(similarities) if similarities else 1.0
        return {
            "mean_word": mean_word, "std_word": std_word,
            "mean_token": mean_token, "std_token": std_token,
            "semantic_consistency": avg_semantic
        }

    def evaluate_reasoning_quality(self, prompt: str, response: str) -> dict:
        if not self.client:
            return {"chain_of_thought_completeness": 3.0, "technical_correctness": 3.0, "logical_consistency": 3.0, "concept_coverage": 3.0, "overall_reasoning_score": 3.0}
        
        eval_prompt = f"""Rate AI response on 1-5 scale.
Prompt: {prompt}
Response: {response}
JSON: {{"chain_of_thought_completeness": 1-5, "technical_correctness": 1-5, "logical_consistency": 1-5, "concept_coverage": 1-5, "justification": ""}}"""
        try:
            res = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=eval_prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(res.text)
            scores = [float(data.get(k, 3.0)) for k in ["chain_of_thought_completeness", "technical_correctness", "logical_consistency", "concept_coverage"]]
            return {
                "chain_of_thought_completeness": scores[0],
                "technical_correctness": scores[1],
                "logical_consistency": scores[2],
                "concept_coverage": scores[3],
                "overall_reasoning_score": sum(scores) / 4.0
            }
        except Exception:
            return {
                "chain_of_thought_completeness": 3.0,
                "technical_correctness": 3.0,
                "logical_consistency": 3.0,
                "concept_coverage": 3.0,
                "overall_reasoning_score": 3.0
            }

# For backward compatibility or simpler usage
class ReasoningEvaluator:
    @staticmethod
    def evaluate(prompt, response, client=None):
        engine = MetricsEngine()
        engine.client = client
        return engine.evaluate_reasoning_quality(prompt, response)
