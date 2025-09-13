import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sim.llm.llm_ollama import llm

if __name__ == "__main__":
    import yaml
    print("Testing LLM JSON response...")
    prompt = "Return a JSON object: {\"hello\": \"world\"}"
    result = llm.chat_json(prompt, system="Return strict JSON only.")
    print("LLM response:", result)
    with open("llm_test_output.yaml", "w") as f:
        yaml.safe_dump(result, f)
    print("LLM response saved to llm_test_output.yaml")
    if isinstance(result, dict) and "hello" in result:
        print("LLM is working correctly.")
    else:
        print("LLM did not return valid JSON. Check Ollama server and model configuration.")
