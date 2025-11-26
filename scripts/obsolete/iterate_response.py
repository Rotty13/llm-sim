"""
Functional Purpose: Iteratively improves text responses using LLM.
Description: Uses LLM to refine and expand responses over multiple iterations.
Replaced by: iterate_data.py (consolidated)
"""
import re
from click import prompt
from sim.llm.llm_ollama import LLM

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="iterate_response")
llm.temperature = 0.9


def chat_with_improvement(prompt_text, system, max_tokens=4096, timeout=300, retries=3):
    text = llm.chat(prompt_text, system=system, max_tokens=max_tokens, timeout=timeout)
    print("Improved response.\n")
    return text

def iterate_response(initial_prompt, system_prompt, iterations=3):
    response = chat_with_improvement(initial_prompt, system_prompt)
    print("Initial response:", response)
    prev_response = response
    for iteration in range(iterations):
        print(f"--- Iteration {iteration + 1} ---")
        iteration_prompt = (f"You are to improve and expand the following response.\nIteration {iteration+1}:\n{prev_response}\n")
        improved_response = chat_with_improvement(iteration_prompt, system_prompt)
        if improved_response and improved_response != prev_response:
            old_len = len(prev_response) if prev_response else 0
            new_len = len(improved_response) if improved_response else 0
            delta = new_len - old_len
            percent = ((delta / old_len) * 100) if old_len else 0
            print(f"New improvements found in iteration {iteration+1}. Change ({percent:.1f}%)")
            prev_response = improved_response
        else:
            print(f"No new improvements found in iteration {iteration+1}.")
    print(f"Finished response improvement with {iterations} iterations.")
    return prev_response

if __name__ == "__main__":
    user_prompt = prompt("Enter your prompt", default="Describe the process of photosynthesis.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved text.")
    final_response = iterate_response(user_prompt, system_prompt)
    print("Final Improved Response:\n", final_response)
