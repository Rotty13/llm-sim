"""
test_agent_conversation_topics.py

Tests for agent conversation topic tracking and retrieval via AgentSocial.
"""
import pytest
from sim.agents.persona import Persona
from sim.agents.agents import Agent
from sim.agents.modules.agent_social import AgentSocial

def test_conversation_topic_logging_and_retrieval():
        # Patch AgentLLM to avoid real LLM calls
        from sim.agents.modules import agent_llm
        class MockAgentLLM(agent_llm.AgentLLM):
            def decide_conversation(self, agent, participants, obs, tick, incoming_message, start_dt=None, loglist=None):
                # Return a dict with the topic from incoming_message
                topic = None
                if isinstance(incoming_message, dict):
                    topic = incoming_message.get('topic')
                return {'reply': 'ok', 'topic': topic}
        # Assign mock LLM to agents
        agent_a.agent_llm = MockAgentLLM(agent_a)
        agent_b.agent_llm = MockAgentLLM(agent_b)
    # Create two agents
    persona_a = Persona(
        name="Alice", age=30, job="engineer", city="Metropolis", bio="Likes weather.", values=["curiosity"], goals=["learn"])
    persona_b = Persona(
        name="Bob", age=32, job="teacher", city="Metropolis", bio="Enjoys sports.", values=["friendship"], goals=["teach"])
    agent_a = Agent(persona=persona_a)
    agent_b = Agent(persona=persona_b)
    # Simulate a conversation with a topic
    topic = "weather"
    participants = [agent_a, agent_b]
    obs = "It's sunny today."
    tick = 1
    incoming_message = {"topic": topic, "content": "How's the weather?"}
    # Agent A decides conversation (should log topic)
    agent_a.decide_conversation(participants, obs, tick, incoming_message)
    # Check that topic is logged in AgentSocial
    recent_topics = agent_a.get_recent_conversation_topics()
    assert topic in recent_topics, f"Expected topic '{topic}' in recent topics: {recent_topics}"
    # Agent B has not logged the topic
    assert topic not in agent_b.get_recent_conversation_topics(), "Agent B should not have topic logged yet."
    # Agent B now converses and logs a new topic
    topic2 = "sports"
    incoming_message2 = {"topic": topic2, "content": "Did you watch the game?"}
    agent_b.decide_conversation(participants, obs, tick+1, incoming_message2)
    recent_topics_b = agent_b.get_recent_conversation_topics()
    assert topic2 in recent_topics_b, f"Expected topic '{topic2}' in Agent B's recent topics: {recent_topics_b}"
    # Both agents should have their own topic histories
    assert topic not in recent_topics_b, "Agent B should not have Agent A's topic."
    assert topic2 not in recent_topics, "Agent A should not have Agent B's topic."
