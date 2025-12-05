"""
AgentPlanLogic module for updating agent plan based on personality traits and physio state.
Handles trait-driven and need-driven plan updates.
"""
class AgentPlanLogic:
    @staticmethod
    def update_plan(agent):
        """
        Update the agent's plan for the current tick based on personality and physio state.
        """
        agent.plan.clear()
        personality = getattr(agent, 'persona', None)
        physio = getattr(agent, 'physio', None)
        traits = getattr(personality, 'traits', {}) if personality else {}
        # Life stage modifiers
        stage = getattr(personality, 'life_stage', 'adult') if personality else 'adult'
        # Example: restrict actions for infants/toddlers/elders
        restricted_actions = set()
        if stage in ('infant', 'toddler'):
            restricted_actions.update(['WORK', 'EXPLORE', 'SAY', 'CLEAN', 'INTERACT'])
        elif stage == 'elder':
            restricted_actions.update(['WORK'])
        # Trait-driven actions
        if traits.get('conscientiousness', 0) > 0.8:
            if "WORK" not in restricted_actions:
                agent.plan.append("WORK")
        if traits.get('openness', 0) > 0.8:
            if "EXPLORE" not in restricted_actions:
                agent.plan.append("EXPLORE")
        # Social influence integration: boost likelihood of SAY if group trends favor it
        social_modifier = 0.0
        if hasattr(agent, 'social') and agent.social:
            # Use most recent topic or default to 'social_life'
            recent_topics = agent.social.get_recent_topics(limit=1)
            topic = recent_topics[0] if recent_topics else 'social_life'
            social_modifier = agent.social.get_social_influence_modifier(topic)
        extraversion_score = traits.get('extraversion', 0) + social_modifier
        if extraversion_score > 0.8 and getattr(physio, 'social', 1) < 0.5:
            if "SAY" not in restricted_actions:
                agent.plan.append("SAY")
        # Needs-driven actions
        if getattr(physio, 'hunger', 0) > 0.8:
            if "EAT" not in restricted_actions:
                agent.plan.append("EAT")
        if getattr(physio, 'energy', 1) < 0.2:
            if "REST" not in restricted_actions:
                agent.plan.append("REST")
        if getattr(physio, 'stress', 0) > 0.7:
            if "RELAX" not in restricted_actions:
                agent.plan.append("RELAX")
        if getattr(physio, 'fun', 1) < 0.3:
            if "EXPLORE" not in restricted_actions:
                agent.plan.append("EXPLORE")
        if getattr(physio, 'social', 1) < 0.3:
            if "SAY" not in restricted_actions:
                agent.plan.append("SAY")
        if getattr(physio, 'hygiene', 1) < 0.3:
            if "CLEAN" not in restricted_actions:
                agent.plan.append("CLEAN")
        if getattr(physio, 'comfort', 1) < 0.3:
            if "RELAX" not in restricted_actions:
                agent.plan.append("RELAX")
        if getattr(physio, 'bladder', 1) < 0.2:
            if "TOILET" not in restricted_actions:
                agent.plan.append("TOILET")
        # Moodlet-driven actions
        moodlets = getattr(physio, 'moodlets', []) if physio else []
        for moodlet in moodlets:
            if moodlet == "starving":
                if "EAT" not in restricted_actions:
                    agent.plan.append("EAT")
            elif moodlet == "exhausted":
                if "REST" not in restricted_actions:
                    agent.plan.append("REST")
            elif moodlet == "lonely":
                if "SAY" not in restricted_actions:
                    agent.plan.append("SAY")
            elif moodlet == "bored":
                if "EXPLORE" not in restricted_actions:
                    agent.plan.append("EXPLORE")
            elif moodlet == "dirty":
                if "CLEAN" not in restricted_actions:
                    agent.plan.append("CLEAN")
            elif moodlet == "uncomfortable":
                if "RELAX" not in restricted_actions:
                    agent.plan.append("RELAX")
            elif moodlet == "urgent_bladder":
                if "TOILET" not in restricted_actions:
                    agent.plan.append("TOILET")
            elif moodlet == "stressed":
                if "RELAX" not in restricted_actions:
                    agent.plan.append("RELAX")
        # Emotional state triggers
        emotional_state = getattr(physio, 'emotional_state', None) if physio else None
        if emotional_state == "angry":
            if "SAY" not in restricted_actions:
                agent.plan.append("SAY")
        if emotional_state == "happy":
            if "EXPLORE" not in restricted_actions:
                agent.plan.append("EXPLORE")
    @staticmethod
    def decide(agent, world, obs_text, tick, start_dt):
        """
        Enhanced decision-making logic for agents, including rule-based and probabilistic choices.
        Delegated from Agent.
        """
        from sim.scheduler.scheduler import enforce_schedule
        from sim.actions.actions import parse_action
        import random
        move_command = enforce_schedule(agent.calendar, agent.place, tick, agent.busy_until)
        if move_command:
            payload = parse_action(move_command)[1]
            if payload:
                return {"action": "MOVE", "params": {"to": payload.get("to", "")}, "private_thought": "I need to move to my appointment."}
        physio = agent.agent_physio.physio if agent.agent_physio else None
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
                traits = agent.persona.traits if hasattr(agent.persona, 'traits') else {}
                from sim.agents.interaction import preference_to_interact
                E_self = traits.get("extraversion", 4)
                A_self = traits.get("agreeableness", 4)
                N_self = traits.get("neuroticism", 4)
                E_partner = 4
                A_partner = 4
                N_partner = 4
                familiarity = agent.relationships.get_relationship("dummy_partner").get("familiarity", 3) if agent.relationships else 3
                attractiveness = 3
                pref_score = preference_to_interact(E_self, A_self, N_self, E_partner, A_partner, N_partner, familiarity, attractiveness)
                if pref_score >= 4:
                    return {"action": "SAY", "private_thought": f"My preference to interact is {pref_score}, I want to talk to someone.", "params": {}}
                else:
                    return {"action": "IDLE", "private_thought": f"My preference to interact is low ({pref_score}), so I won't socialize now."}
        traits = agent.persona.traits if hasattr(agent.persona, 'traits') else {}
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
        if "ambition" in agent.persona.values and "achieve goal" in agent.persona.goals:
            if random.random() < 0.3:
                return {"action": "WORK", "private_thought": "I feel motivated to work on my goals."}
        if "curiosity" in agent.persona.values:
            if random.random() < 0.4:
                return {"action": "EXPLORE", "private_thought": "My curiosity drives me to explore."}
        if agent.physio and getattr(agent.physio, 'stress', 0) > 0.7 and "relaxation" in agent.persona.values:
            return {"action": "RELAX", "private_thought": "I value relaxation and need to reduce stress."}
        if random.random() < 0.2:
            return {"action": "EXPLORE", "private_thought": "I feel like exploring the area."}
        return {"action": "IDLE", "private_thought": "I have nothing to do right now."}

    @staticmethod
    def step_interact(agent, world, participants, obs, tick, start_dt, incoming_message, loglist):
        """
        Cohesive step: agent converses, decays needs, updates moodlets, decides, and acts in the world.
        Returns the conversation decision dict.
        Safely handles disabled modules.
        Delegated from Agent.
        """
        if agent.agent_physio:
            agent.agent_physio.decay_needs()
        agent.tick_moodlets()
        conv_decision = agent.decide_conversation(participants, obs, tick, incoming_message, start_dt=start_dt, loglist=loglist)
        if conv_decision and "new_mood" in conv_decision and agent.agent_physio:
            agent.agent_physio.set_mood(conv_decision["new_mood"])
        if conv_decision and "memory_write" in conv_decision and conv_decision["memory_write"] and agent.memory_manager:
            from sim.memory.memory import MemoryItem
            agent.memory_manager.write_memory(MemoryItem(t=tick, kind="episodic", text=conv_decision["memory_write"], importance=0.5))
        action_decision = agent.decide(world, obs, tick, start_dt)
        agent.act(world, action_decision, tick)
        return conv_decision
