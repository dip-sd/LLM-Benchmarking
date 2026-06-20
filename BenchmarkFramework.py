
import os
import json
import time
import pandas as pd
from tqdm import tqdm
from benchmark import AUTOMOTIVE_PROMPTS
from Module1_MultiProviderInterface import GeminiAdapter, GroqAdapter, OllamaAdapter
from Module2_EvaluationMetricsEngine import MetricsEngine, HallucinationDetector, ReasoningEvaluator

def run_evaluation(prompts, providers, runs_per_prompt=5):
    results = []
    # API key for as-a-judge metrics
    GEMINI_KEY = "<Gemini API Key>"
    detector = HallucinationDetector(gemini_api_key=GEMINI_KEY)
    engine = MetricsEngine(gemini_api_key=GEMINI_KEY)
    
    for prompt_data in tqdm(prompts, desc="Prompts"):
        prompt_text = prompt_data['prompt']
        category = prompt_data['category']
        
        for provider in providers:
            provider_contents = []
            provider_token_counts = []
            
            for i in range(runs_per_prompt):
                try:
                    content, latency, p_tokens, c_tokens = provider.generate(prompt_text)
                    
                    # Individual Run Metrics
                    len_metrics = engine.compute_length_metrics(content, c_tokens)
                    lat_metrics = engine.compute_latency_metrics(latency, c_tokens)
                    h_report = detector.analyze(prompt_text, content)
                    reason_metrics = engine.evaluate_reasoning_quality(prompt_text, content)
                    
                    res = {
                        "prompt_id": prompt_data['id'],
                        "category": category,
                        "provider": provider.provider_name,
                        "run": i + 1,
                        "content": content,
                        "latency": latency,
                        "prompt_tokens": p_tokens,
                        "completion_tokens": c_tokens,
                        "hallucinations": len(h_report["hallucinations_detected"]),
                        "hallucination_details": "; ".join(str(x) for x in h_report["hallucinations_detected"]),
                        **len_metrics,
                        **lat_metrics,
                        **reason_metrics
                    }
                    results.append(res)
                    provider_contents.append(content)
                    provider_token_counts.append(c_tokens)
                    
                    # Rate limit management
                    if provider.provider_name == "Groq":
                        time.sleep(2)
                    elif provider.provider_name == "Gemini":
                        time.sleep(15)
                        
                except Exception as e:
                    print(f"Error with {provider.provider_name} on prompt {prompt_data['id']}: {e}")
            
            # Compute Consistency if we have multiple runs
            if len(provider_contents) > 1:
                consistency = engine.compute_consistency_metrics(provider_contents, provider_token_counts)
                # Update the last results for this provider/prompt with consistency data
                for r in results:
                    if r["prompt_id"] == prompt_data['id'] and r["provider"] == provider.provider_name:
                        r.update(consistency)
                    
    return results

def main():
    # API Keys (Ideally these would be env vars)
    GEMINI_KEY = "<Gemini API Key>"
    GROQ_KEY = "<Groq API Key>"
    
    # Initialize Adapters
    providers = [
        # OllamaAdapter(model_name="llama3.2:1b"),
        GroqAdapter(api_key=GROQ_KEY),
        # GeminiAdapter(model_name="gemini-3.1-flash-lite",api_key=GEMINI_KEY)
    ]
    
    # Check if Ollama is running and model pulled
    try:
        providers.insert(0, OllamaAdapter(model_name="llama3.2:1b"))
    except Exception as e:
        print(f"Ollama not available: {e}")

    # subset_prompts = AUTOMOTIVE_PROMPTS[:2]
    # For full run, use AUTOMOTIVE_PROMPTS
    subset_prompts = AUTOMOTIVE_PROMPTS[20:31] 
    
    print(f"Starting FULL evaluation on {len(subset_prompts)} prompts, 5 runs each...")
    results = run_evaluation(subset_prompts, providers, runs_per_prompt=5)
    
    df = pd.DataFrame(results)
    df.to_csv("benchmark_master5.csv", index=False)
    df.to_csv("evaluation_results5.csv", index=False)
    
    # Summary report
    summary = df.groupby('provider').agg({
        'latency': ['mean', 'max', 'std'],
        'tps': 'mean',
        'completion_tokens': 'sum',
        'hallucinations': 'sum',
        'overall_reasoning_score': 'mean',
        'technical_correctness': 'mean',
        'semantic_consistency': 'mean'
    })
    
    print("\nEvaluation Summary:")
    print(summary)
    
    summary.to_csv("evaluation_summary5.csv")
    print("\nResults saved to evaluation_results.csv and evaluation_summary.csv")

if __name__ == "__main__":
    main()

# -------------------------------------------------------------
# CODE FOR CUSTOM DEMONSTRATION & REUSE
# -------------------------------------------------------------
# To load prompts from a CSV or JSON file instead of the default list:
#
# def run_custom_benchmark(file_path, file_type='csv'):
#     import pandas as pd
#     import json
#     
#     if file_type == 'csv':
#         custom_df = pd.read_csv(file_path)
#         custom_prompts = custom_df.to_dict(orient='records')
#     elif file_type == 'json':
#         with open(file_path, 'r') as f:
#             custom_prompts = json.load(f)
#
#     # Initialize providers...
#     # results = run_evaluation(custom_prompts, providers, runs_per_prompt=5)
#     # ...
