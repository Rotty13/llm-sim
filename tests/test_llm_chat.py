from operator import call
from sim.llm.llm_ollama import LLM, LLM_Convo
from tests.test_tensorrt import llm

# Initialize the LLM
llm_director = LLM_Convo()
llm_director.temperature = 0.3
llm_student = LLM_Convo(caller="test_llm_chat")
llm_student.temperature = 0.5
llm_json_converter = LLM()
llm_json_converter.temperature = 0.2


def main():
    director_system_prompt = (
        "You are an expert prompt engineer. You will be given a goal and you will create a prompt to help another AI model achieve that goal. "
        "You will then evaluate the response from that model and briefly critique it, providing a short list of suggestions for improvement."
        "The other llm model is memoryless so you must include all necessary context or improvements in your prompts."
        "Only provide the improved prompt as your final output, no other text."
    )

    student_system_prompt = (
        "You are a creative writer AI. You will be given prompts to generate text content. "
        "Respond creatively and thoughtfully based on the prompts provided."
    )
    llm_student_response = None
    init_prompt = "create a comprehensive but concise json representation for an entity, suitable for conversion into a logical entity model with properties and affordances for a text-based simulation environment. "
    constructed_prompt = init_prompt
    for i in range(3):  # Limit to 3 iterations for testing
        print(f"\n--- Iteration {i+1} ---")
        print(f"Director Prompt: {constructed_prompt}\n")
        llm_student_response = llm_student.chat(constructed_prompt, system=student_system_prompt, max_tokens=4096, timeout=120)
        if i == 2:  # On last iteration, print the final response
            print(f"====== Final Student Response ======\n{llm_student_response}\n")
            break
        else:
            print(f"Student Responded.")

        critique_prompt = (
            f"The following is a response from another AI model to the prompt: '{constructed_prompt}'. "
            f"Critique the response and provide suggestions for improvement. "
            f"Response: '{llm_student_response}'"
        )
        critique = llm_director.chat(critique_prompt, system=director_system_prompt, max_tokens=4096, timeout=120)
        print(f"Director Critiqued")

        improvement_prompt = (
            f"Based on the critique: '{critique}', improve the original prompt: '{constructed_prompt}' "
            f"to better achieve the goal."
            f"Provide only the improved prompt as your output."
        )
        constructed_prompt = llm_director.chat(improvement_prompt, system=director_system_prompt, max_tokens=4096, timeout=120)
        print(f"Prompt Improved")

    llm_json_prompt = (
        f"Convert the following text description into a structured JSON format with properties and affordances suitable for a text-based simulation environment. "
        f"Description: '{llm_student_response}'"
    ) 
    json_response = llm_json_converter.chat_json(llm_json_prompt, max_tokens=4096, timeout=120)
    print(f"====== JSON Response ======\n{json_response}\n")
    #save to file in data\entities\items
    with open("data\\entities\\items\\claw_hammer.json", "x", encoding="utf-8") as f:
        import json
        json.dump(json_response, f, indent=2)

if __name__ == "__main__":
    main()

