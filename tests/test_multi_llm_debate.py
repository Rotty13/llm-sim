from sim.llm.llm_ollama import LLM

# Initialize the LLM
llm = LLM()
llm.temperature = .5


# Create 3 agents for the debate
agents = [
    {"name": "AgentA", "side": "Pro", "persona": "You argue in favor of AI regulation."},
    {"name": "AgentB", "side": "Con", "persona": "You argue against AI regulation."},
    {"name": "AgentC", "side": "Neutral", "persona": "You are undecided and will ask questions to both sides."}
]

def debate_turn(turn, messages):
    # AgentC asks a question
    question_prompt = (
        f"{agents[2]['persona']} You are moderating a debate between AgentA (Pro) and AgentB (Con) on AI regulation. "
        f"Turn {turn}: Ask a question to both sides to clarify their positions."
    )
    question = llm.chat("", system=question_prompt, messages=messages)
    messages.append({"role": "AgentC", "content": question})

    # AgentA responds
    pro_prompt = (
        f"{agents[0]['persona']} AgentC asked: '{question}'. Respond with arguments supporting your side."
    )
    pro_response = llm.chat("", system=pro_prompt, messages=messages)
    messages.append({"role": "AgentA", "content": pro_response})

    # AgentB responds
    con_prompt = (
        f"{agents[1]['persona']} AgentC asked: '{question}'. Respond with arguments supporting your side."
    )
    con_response = llm.chat("", system=con_prompt, messages=messages)
    messages.append({"role": "AgentB", "content": con_response})

    # AgentA rebuts AgentB
    rebut_pro_prompt = (
        f"{agents[0]['persona']} AgentB said: '{con_response}'. Rebut their argument."
    )
    rebut_pro = llm.chat("", system=rebut_pro_prompt, messages=messages)
    messages.append({"role": "AgentA", "content": rebut_pro})

    # AgentB rebuts AgentA
    rebut_con_prompt = (
        f"{agents[1]['persona']} AgentA said: '{pro_response}'. Rebut their argument."
    )
    rebut_con = llm.chat("", system=rebut_con_prompt, messages=messages)
    messages.append({"role": "AgentB", "content": rebut_con})

    return messages

import random

def generate_debate_topics():
    topic_prompt = (
        'return a list of 25 interesting real debate topics. Return only the topics as a list of string, no explanation. no placeholders or numbering. '
        'Example: {"topics": ["Should AI be regulated?", "Is climate change the greatest threat to humanity?", "Should universal basic income be implemented?"]}'
    )
    topics = llm.chat_json(topic_prompt, max_tokens=2048)
    # Try to extract topics from the response
    if isinstance(topics, dict):
        if "topics" in topics and isinstance(topics["topics"], list):
            return topics["topics"]
        # fallback: try to find a list in any value
        for v in topics.values():
            if isinstance(v, list):
                return v
    # fallback: if failed, just use a static list
    return [f"Topic {i+1}" for i in range(25)]

def multi_agent_debate():
    print("Generating debate topics...")
    topics = generate_debate_topics()
    print("Debate Topics:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    chosen_topic = random.choice(topics)
    print(f"\nChosen Debate Topic: {chosen_topic}\n")

    # Update agent personas to use the chosen topic
    agents[0]["persona"] = f"You argue in favor of: {chosen_topic}."
    agents[1]["persona"] = f"You argue against: {chosen_topic}."
    agents[2]["persona"] = f"You are undecided and will ask questions to both sides about: {chosen_topic}."

    messages = []
    for turn in range(1, 6):
        print(f"\n--- Turn {turn} ---")
        messages = debate_turn(turn, messages)
        # Print last round of messages
        for m in messages[-5:]:
            print(f"{m['role']}: {m['content']}")

    # AgentC makes final decision
    decision_prompt = (
        f"{agents[2]['persona']} After 5 turns of debate, decide which side (AgentA or AgentB) convinced you more and explain why."
    )
    decision = llm.chat("", system=decision_prompt, messages=messages)
    print("\nFinal Decision by AgentC:", decision)

# Uncomment below to run the debate when this file is executed directly
if __name__ == "__main__":
    multi_agent_debate()
