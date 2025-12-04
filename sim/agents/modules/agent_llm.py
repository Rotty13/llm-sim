"""
AgentLLM module for managing agent LLM-based conversation logic.
Handles LLM prompt construction and chat response parsing.
"""
from sim.llm import llm_ollama
import json

class AgentLLM:
    def __init__(self, agent):
        self.agent = agent
        self.llm = llm_ollama.LLM()

    def decide_conversation(self, participants, obs, tick, incoming_message, start_dt=None, loglist=None):
        system_prompt = (
            "You are a human engaged in a conversation. "
            "You are not being simulated or in a simulation. "
            "You are yourself and your memories are real.\n"
            "If you must recall something in your distant past or childhood, "
            "you may invent it. Don't reference specific names or places.\n"
            "Respond as naturally as possible, considering your persona, "
            "context, and conversation history. 1-3 sentences only.\n"
            "Return ONLY JSON with keys: reply, private_thought, memory_write (nullable).\n"
            "Example: {\"to\":\"David\",\"reply\":\"Hello! How can I help you?\"," +
            "\"private_thought\":\"I feel helpful.\",\"memory_write\":\"I greeted someone.\"," +
            "\"new_mood\":\"happy\"}\n"
        )
        history_str = "\n".join([
            f"{entry['role']}: {entry['content']}"
            for entry in self.agent.conversation_history[-15:]
        ])
        def format_memories(query):
            if self.agent.memory and hasattr(self.agent.memory, 'get_episodic'):
                memories = self.agent.memory.get_episodic()[:5]
                return ", ".join(str(m) for m in memories)
            return ""
        user_prompt = (
            f"You are {self.agent.persona.name} (job: {self.agent.persona.job}, "
            f"city: {self.agent.persona.city}) Bio: {self.agent.persona.bio}.\n" +
            (f"The date is {self.agent.now_str(tick, start_dt).split()[0]}.\n" if start_dt else "") +
            f"Participants: {', '.join(p.persona.name for p in participants if p != self.agent)}.\n" +
            f"Observations: {obs}\n\n" +
            (f"Time {self.agent.now_str(tick, start_dt)}. " if start_dt else "") +
            f"Location {self.agent.place}. Mood {getattr(self.agent.physio, 'mood', 'unknown')}.\n" +
            f"Conversation history:\n{history_str}\n" +
            f"My values: {', '.join(self.agent.persona.values)}.\n" +
            f"My goals: {', '.join(self.agent.persona.goals)}.\n" +
            f"I remember: {format_memories('conversation')}\n" +
            f"I remember: {format_memories('life')}\n" +
            f"I remember: {format_memories('recent')}\n" +
            f"Incoming message: {json.dumps(incoming_message)}\n\n" +
            "Craft a thoughtful and context-aware reply.\n"
        )
        out = self.llm.chat_json(user_prompt, system=system_prompt, max_tokens=256)
        if not isinstance(out, dict):
            out = {"reply": "Sorry, I didn't understand.", "private_thought": None, "memory_write": None}
        if incoming_message is not None:
            msg_content = json.dumps(incoming_message) if isinstance(incoming_message, dict) else str(incoming_message)
            self.agent.conversation_history.append({"role": "user", "content": msg_content})
        out['from'] = self.agent.persona.name
        self.agent.conversation_history.append({"role": "agent", "content": json.dumps(out)})
        if loglist is not None:
            loglist.append(out)
        return out
