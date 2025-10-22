import os
from click import prompt
from sim.llm.llm_ollama import LLM

def read_file_contents(rel_path):
    abs_path = os.path.join(os.getcwd(), rel_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_prompt_file(prompt_text, example_filename):
    output_dir = os.path.join(os.getcwd(), "outputs", "llm_data", "prompts")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(example_filename))[0]
    num = 1
    while True:
        out_path = os.path.join(output_dir, f"{base_name}_prompt_{num}.txt")
        if not os.path.exists(out_path):
            break
        num += 1
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Prompt generated from file: {example_filename}\n\n")
        f.write(prompt_text)
    return out_path

llm = LLM(caller="prompt_from_review")
llm.temperature = 0.7

def generate_prompt_with_llm(file_contents, user_input, system_prompt=None, max_tokens=1024, timeout=120):
    # For .txt review, try to split into example and instruction
    lines = file_contents.splitlines()
    example_lines = []
    instruction_lines = []
    found_example = False
    for line in lines:
        if line.strip().lower().startswith('example'):
            found_example = True
        if found_example:
            example_lines.append(line)
        else:
            instruction_lines.append(line)
    example_text = '\n'.join(example_lines).strip()
    instruction_text = '\n'.join(instruction_lines).strip()
    # If no explicit example, use first block as example
    if not example_text:
        example_text = '\n'.join(lines[:10])  # first 10 lines as fallback
        instruction_text = '\n'.join(lines[10:])
    llm_prompt = f"{file_contents}"
    system_prompt = f"You are a prompt engineer. You are to design a prompt for an LLM that can be used to generate a JSON object fitting the criteria of the given review file. Incorporate these user instructions carefully: {user_input}. Only output the prompt, do not include any explanations. Output prompt should always include a simple example."
    return llm.chat(llm_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

if __name__ == "__main__":
    rel_path = prompt("Enter the relative path to the .txt review file", default="outputs/llm_data/json_reviews/example_review.txt")
    user_input = prompt("Enter additional user input for the prompt (optional)", default="")
    file_contents = read_file_contents(rel_path)
    prompt_text = generate_prompt_with_llm(file_contents, user_input)
    out_path = save_prompt_file(prompt_text, rel_path)
    print(f"\n--- Prompt saved to {out_path} ---\n")
    print(prompt_text)
