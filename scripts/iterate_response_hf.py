import imp
import re
from click import prompt
from sympy import im
from sim.llm.llm_ollama import LLM

llm = LLM(caller="iterate_response_hf")
llm.temperature = 0.9

def chat_with_improvement(prompt_text, system, max_tokens=4096, timeout=300, retries=3):
    text = llm.chat(prompt_text, system=system, max_tokens=max_tokens, timeout=timeout)
    return text

def is_fulfilled(response, system_prompt, initial_prompt):
    # Ask the LLM if the response fulfills the user's request
    judge_system = "You are a helpful assistant that determines if a response fulfills the user's request. Answer with 'yes' or 'no' following by a short explanation in parentheses."
    judge_prompt = f"Does the following response fully fulfill the user's request and the initial prompt? Respond with 'yes' or 'no' following by a short explanation in parentheses.\nInitial Prompt:\n{initial_prompt}\nResponse:\n{response}\n"
    judgment = llm.chat(judge_prompt, system=judge_system, max_tokens=32)
    explaination=None
    if '(' in judgment and ')' in judgment:
        explaination=judgment[judgment.find('('):], judgment[judgment.find(')')+1:]
    return 'yes' in judgment.lower(), explaination

def try_attain_fulfillment_loop(response, system_prompt, initial_prompt, max_retries=3):
    for attempt in range(max_retries):
        if is_fulfilled(response, system_prompt, initial_prompt)[0]:
            return response
        print(f"Attempt {attempt+1} to improve response for fulfillment.")
        improvement_prompt = f"The previous response did not fully meet the user's request. Please improve it.\nPrevious Response:\n{response}"
        response = chat_with_improvement(improvement_prompt, system_prompt)
    return response


def iterate_response_hf(initial_prompt, system_prompt, max_iterations=10):
    response = chat_with_improvement(initial_prompt, system_prompt)
    print("Initial response:", response)
    prev_response = response
    for iteration in range(max_iterations):
        print(f"--- Iteration {iteration + 1} ---")
        got_user_feedback = False
        user_input = prompt(f"Enter your improvement or press Enter to keep previous (iteration {iteration+1})", default="No user input")
        # If no user input, continue improving based on original prompt
        if user_input.strip().lower() == "no user input" or user_input.strip() == "":
            iteration_prompt = "You are to improve and expand the following response based on the initial prompt: \n" + initial_prompt
            got_user_feedback = False
        else:
            iteration_prompt = f"You are to improve and expand the following response based on user feedback.\nIteration {iteration+1}:\n{user_input}\n"
            got_user_feedback = True
        
        #if already fulfilled continue, else retry n times
        improved_response = chat_with_improvement(iteration_prompt + prev_response, system_prompt)
        if got_user_feedback:
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial_prompt)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                print(improved_response)
                prev_response = improved_response
                continue
            improved_response = try_attain_fulfillment_loop(improved_response, system_prompt, initial_prompt)
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial_prompt)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                print(improved_response)
                prev_response = improved_response
                continue

            print(f"User feedback provided but request still not fulfilled.")
        print(improved_response)
        prev_response = improved_response
    print(f"Finished response improvement after {iteration+1} iterations.")
    return prev_response

if __name__ == "__main__":
    user_prompt = prompt("Enter your prompt", default="Describe the process of photosynthesis.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved text. Do not ask questions. if no changes are made, respond with the original text.")
    final_response = iterate_response_hf(user_prompt, system_prompt)
    print("Final Improved Response:\n", final_response)
