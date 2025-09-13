from sim.llm.llm_ollama import LLM

# Initialize the LLM
llm = LLM()

def main():
    city="Lumière"
    year=1900
    prompt = f"""You are an expert prompt engineer. Your task is to write a prompt for a language model that will generate a believable resident of the city of {city} in the year of {year}. The prompt must:

- Specify the city and year as variables.
- Require output ONLY in strict JSON format, with an example.
- Include clear rules:
  - Ages 5-70.
  - Jobs should realistic for a small city and the time period, not a restricted set.
  - Each person must have a unique name, job, and start_place.
  - Bios should be 5-10 words, reflecting job, age, and personality.
  - Values and goals must be distinct and reflect personality and circumstances.
  - start_place must be specific and unique.
  - All details must respect the historical context of the specified year.

Write the full prompt that will instruct the LLM to generate such personas, including an example JSON and all rules. Make sure the prompt is clear, concise, and time-period appropriate."""

    response = llm.chat(prompt)
    print("Prompt:", prompt)
    print("Response:", response)

if __name__ == "__main__":
    main()
