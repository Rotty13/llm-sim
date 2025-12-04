"""
AgentPlanLogic module for updating agent plan based on personality traits and physio state.
Handles trait-driven and need-driven plan updates.
"""
class AgentPlanLogic:
    def __init__(self, agent):
        self.agent = agent

    def update_plan(self, personality, physio):
        # Trait-driven actions
        if personality.trait_effect("conscientiousness") > 0.6 and physio.energy > 0.5:
            if "WORK" not in self.agent.plan:
                self.agent.plan.append("WORK")
        if personality.trait_effect("extraversion") > 0.6 and physio.social < 0.7:
            if "SAY" not in self.agent.plan:
                self.agent.plan.append("SAY")
        if personality.trait_effect("openness") > 0.6 and physio.energy > 0.3:
            if "EXPLORE" not in self.agent.plan:
                self.agent.plan.append("EXPLORE")
