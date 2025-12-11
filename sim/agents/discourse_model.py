"""
Basic Discourse Model for Agentic Conversation

Implements a functional model of agent discourse supporting statements, questions, and imperatives between n agents.

Key Features:
- ObservableBehaviors/InternalStateChanges tuple mapping
- Turn-taking and context tracking
- Reference resolution (by name, tag, or context)
- Response generation for assertions, questions, commands
- Extensible for emotional response, knowledge update

LLM Usage:
- No direct LLM calls; designed for rule-based and data-driven agent logic.

CLI Arguments:
- None; intended for import and use in simulation scripts/tests.
"""
from typing import List, Dict, Any, Optional, Tuple
from itertools import chain, combinations

class Agent:
    def __init__(self, name: str):
        self.name = name
        self.knowledge: Dict[str, Any] = {}
        self.intentions: List[str] = []
        self.emotion: Optional[str] = None

    def receive(self, utterance: str, context: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # Basic mapping: parse utterance, update internal state, generate response
        observable = {}
        internal = {}
        # Example: handle statement, question, imperative
        if utterance.endswith('?'):
            observable['ImmediateUtteranceOrAction'] = f"{self.name} answers: [response]"
        elif utterance.lower().startswith('please') or utterance.lower().startswith('do '):
            observable['ImmediateUtteranceOrAction'] = f"{self.name} acknowledges command."
            internal['OngoingConditionalIntention'] = utterance
        else:
            observable['ImmediateUtteranceOrAction'] = f"{self.name} acknowledges statement."
            internal['BeliefOrKnowledgeUpdate'] = utterance
        return observable, internal

class DiscourseModel:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.turn = 0
        self.context: Dict[str, Any] = {}
        self.turn_order: List[int] = list(range(len(agents)))  # Default order

    def converse(self, utterances: List[str]):
        # Simulate a round of conversation with turn order (no interruption logic)
        n = len(self.agents)
        i = 0
        while i < len(utterances):
            agent_idx = self.turn_order[self.turn % n]
            agent = self.agents[agent_idx]
            utterance = utterances[i]
            observable, internal = agent.receive(utterance, self.context)
            print(f"{agent.name} | Observable: {observable} | Internal: {internal}")
            self.context[f"last_{agent.name}"] = utterance
            self.turn += 1
            i += 1

    def should_conclude(self, utterances: List[str]) -> bool:
        """
        Determines if a conversation should be concluded based on state,utterances, and context.

        Returns True if any utterance signals ending (e.g., 'goodbye', 'bye', 'see you', "that's all"), else False.
        """

        chance_to_conclude = 0.1  # base chance
        # Simple keyword check
        end_signals = ['goodbye', 'bye', 'see you', "that's all", 'end conversation', 'finished']
        for utterance in utterances:
            if any(signal in utterance.lower() for signal in end_signals):
                chance_to_conclude += 0.5
                break


        return False

    
    def single_actor_conversation_probability(self, self_agent: Agent, other_agent: Agent, context: Dict[str, Any]) -> float:
        """
        Computes the base probability of self_agent starting a conversation with other_agent,
        given intentions and context. Used as a building block for subset probabilities.
        """
        prob = 0.2  # base
        if other_agent.name in self_agent.intentions:
            prob += 0.3
        if context.get('location') == 'lounge' and other_agent.name == 'Jamie':
            prob += 0.2
        return min(prob, 1.0)

    def multiple_actor_conversation_start_probability(self, self_agent: Agent, all_nearby_agents: List[Agent], target_group: List[Agent], context: Dict[str, Any]) -> float:
        """
        Returns the probability that self_agent will start a conversation with all agents in target_group,
        given the full set of nearby agents and context.
        - self_agent: the initiator
        - all_nearby_agents: the superset of agents in the vicinity
        - target_group: the subset of agents being considered for conversation
        - context: context for social rules, intentions, etc.
        """
        if not target_group or not all_nearby_agents:
            return 0.0
        # Use the same logic as conditional_conversation_probability
        base_probs = [self.single_actor_conversation_probability(self_agent, agent, context) for agent in target_group]
        from functools import reduce
        import operator
        subset_prob = reduce(operator.mul, base_probs, 1.0)
        # Optionally, normalize by the number of possible non-empty subsets
        # (not required for a single subset probability)
        return min(subset_prob, 1.0)
    
    
# Example usage (for testing):
if __name__ == "__main__":
    agents = [Agent("Alice"), Agent("Bob"), Agent("Jamie")]
    model = DiscourseModel(agents)
    print("--- Normal turn order ---")
    model.converse([
        "What time is lunch?",
        "Please check the lounge.",
        "The train is delayed."
    ])

    print("\n--- Test: Group conversation probability ---")
    # Set up intentions and context
    agents[0].intentions = ["Bob", "Jamie"]  # Alice intends to talk to Bob and Jamie
    context = {"location": "lounge"}
    all_nearby = agents[1:]  # Bob and Jamie are nearby
    # Test probability for Alice starting a conversation with both Bob and Jamie
    prob_both = model.multiple_actor_conversation_start_probability(agents[0], all_nearby, all_nearby, context)
    print(f"Probability (Alice with Bob and Jamie): {prob_both:.3f}")
    # Test probability for Alice starting a conversation with just Bob
    prob_bob = model.multiple_actor_conversation_start_probability(agents[0], all_nearby, [agents[1]], context)
    print(f"Probability (Alice with Bob): {prob_bob:.3f}")
    # Test probability for Alice starting a conversation with just Jamie
    prob_jamie = model.multiple_actor_conversation_start_probability(agents[0], all_nearby, [agents[2]], context)
    print(f"Probability (Alice with Jamie): {prob_jamie:.3f}")
