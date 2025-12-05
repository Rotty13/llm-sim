"""
DecisionController module for agent decision-making logic.
Handles rule-based and probabilistic choices for agent actions.
"""
import random

class DecisionController:
    def __init__(self, agent):
        self.agent = agent

    def decide(self, world, obs_text, tick, start_dt):
        # Check and enforce schedule
        move_command = self.agent.enforce_schedule(self.agent.calendar, self.agent.place, tick, self.agent.busy_until)
        if move_command:
            payload = self.agent.parse_action_payload(move_command)
            if payload:
                return {"action": "MOVE", "params": {"to": payload.get("to", "")}, "private_thought": "I need to move to my appointment."}

        # Rule-based decision-making
        physio = self.agent.physio
        if physio:
            if getattr(physio, 'hunger', 0) > 0.8:
                return {"action": "EAT", "private_thought": "I'm feeling very hungry."}
            elif getattr(physio, 'energy', 1) < 0.3:
                return {"action": "SLEEP", "private_thought": "I'm too tired to continue."}
            elif getattr(physio, 'stress', 0) > 0.5:
                return {"action": "RELAX", "private_thought": "I need to relax and reduce my stress."}
            elif getattr(physio, 'fun', 1) < 0.3:
                return {"action": "EXPLORE", "private_thought": "I'm bored and need to have some fun."}
            elif getattr(physio, 'social', 1) < 0.3:
                # Social interaction decision using preference_to_interact
                traits = self.agent.persona.traits if hasattr(self.agent.persona, 'traits') else {}
                E_self = traits.get("extraversion", 4)
                A_self = traits.get("agreeableness", 4)
                N_self = traits.get("neuroticism", 4)
                E_partner = 4
                A_partner = 4
                N_partner = 4
                familiarity = self.agent.relationships.get_relationship("dummy_partner").get("familiarity", 3) if self.agent.relationships else 3
                attractiveness = 3
                pref_score = self.agent.preference_to_interact(E_self, A_self, N_self, E_partner, A_partner, N_partner, familiarity, attractiveness)
                if pref_score >= 4:
                    return {"action": "SAY", "private_thought": f"My preference to interact is {pref_score}, I want to talk to someone.", "params": {}}
                else:
                    return {"action": "THINK", "private_thought": f"My preference to interact is low ({pref_score}), so I won't socialize now."}

        traits = self.agent.persona.traits if hasattr(self.agent.persona, 'traits') else {}
        if traits.get("conscientiousness", 0.5) > 0.7 and random.random() < traits["conscientiousness"]:
            return {"action": "WORK", "private_thought": "My conscientiousness drives me to work diligently."}
        if traits.get("openness", 0.5) > 0.6 and random.random() < traits["openness"]:
            return {"action": "EXPLORE", "private_thought": "My openness makes me want to explore new things."}
        if traits.get("extraversion", 0.5) > 0.6 and random.random() < traits["extraversion"]:
            return {"action": "SAY", "private_thought": "I feel like socializing with others.", "params": {}}
        if traits.get("neuroticism", 0.5) > 0.6 and random.random() < traits["neuroticism"]:
            return {"action": "RELAX", "private_thought": "I need to relax and manage my stress."}
        if traits.get("agreeableness", 0.5) > 0.6 and random.random() < traits["agreeableness"]:
            return {"action": "INTERACT", "private_thought": "I want to help or interact with others.", "params": {"action_type": "help"}}

        if "ambition" in self.agent.persona.values and "achieve goal" in self.agent.persona.goals:
            if random.random() < 0.3:
                return {"action": "WORK", "private_thought": "I feel motivated to work on my goals."}
        if "curiosity" in self.agent.persona.values:
            if random.random() < 0.4:
                return {"action": "EXPLORE", "private_thought": "My curiosity drives me to explore."}
        if physio and getattr(physio, 'stress', 0) > 0.7 and "relaxation" in self.agent.persona.values:
            return {"action": "RELAX", "private_thought": "I value relaxation and need to reduce stress."}
        if random.random() < 0.2:
            return {"action": "EXPLORE", "private_thought": "I feel like exploring the area."}
        return {"action": "THINK", "private_thought": "I have nothing to do right now."}
