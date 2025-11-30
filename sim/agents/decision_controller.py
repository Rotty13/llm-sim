"""
Handles decision-making logic for an agent.

Classes:
    DecisionController: Centralizes decision-making logic, consolidating
    rule-based and probabilistic decision strategies.

Methods:
    decide(agent: Any, world: WorldInterface, obs_text: str, tick: int, start_dt):
        Makes a decision based on the agent's state and observations.
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
import json
import random
from sim.utils.utils import now_str

if TYPE_CHECKING:
    from sim.world.world import World


class DecisionController:
    """
    Consolidated decision-making controller for agents.
    Combines rule-based, probabilistic, and goal-driven decision logic.
    """
    
    def decide(self, agent: Any, world: 'World', obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        """
        Make a decision based on the agent's state, observations, and context.
        
        Decision priority:
        1. Check if agent is busy
        2. Enforce schedule (appointments)
        3. Critical needs (hunger, energy)
        4. Goal-driven decisions (based on persona)
        5. Context-aware decisions (location, time)
        6. Probabilistic exploration
        7. Default idle
        
        Args:
            agent: The agent making the decision.
            world: The world context.
            obs_text: Observation text.
            tick: Current simulation tick.
            start_dt: Start datetime for time formatting.
        
        Returns:
            Decision dictionary with action, params, and private_thought.
        """
        # Check if agent is still busy
        if tick < agent.busy_until:
            return self._continue_action()
        
        # Retrieve context
        place = world.places.get(agent.place) if agent.place else None
        
        # Enforce schedule
        schedule_decision = self._check_schedule(agent, tick)
        if schedule_decision:
            return schedule_decision
        
        # Critical needs (highest priority after schedule)
        needs_decision = self._check_critical_needs(agent, world, place)
        if needs_decision:
            return needs_decision
        
        # Goal-driven decisions based on persona
        goal_decision = self._goal_driven_decision(agent, world, tick)
        if goal_decision:
            return goal_decision
        
        # Context-aware decisions (location, time, social)
        context_decision = self._context_aware_decision(agent, world, place, tick)
        if context_decision:
            return context_decision
        
        # Probabilistic decisions
        prob_decision = self._probabilistic_decision(agent)
        if prob_decision:
            return prob_decision
        
        # Default action
        return self._default_decision()
    
    def _continue_action(self) -> Dict[str, Any]:
        """Return a continue action when agent is busy."""
        return {
            "action": "CONTINUE",
            "params": {},
            "private_thought": "I'm still busy with my current activity."
        }
    
    def _check_schedule(self, agent: Any, tick: int) -> Optional[Dict[str, Any]]:
        """Check if agent needs to move for a scheduled appointment."""
        from sim.scheduler.scheduler import enforce_schedule
        
        move_command = enforce_schedule(agent.calendar, agent.place, tick, agent.busy_until)
        if move_command:
            # Parse the destination from MOVE({"to":"..."})
            try:
                dest = json.loads(move_command[move_command.find("(")+1:move_command.rfind(")")])
                return {
                    "action": "MOVE",
                    "params": {"to": dest.get("to", "")},
                    "private_thought": "I need to head to my appointment."
                }
            except (json.JSONDecodeError, AttributeError):
                pass
        return None
    
    def _check_critical_needs(self, agent: Any, world: 'World', place: Any) -> Optional[Dict[str, Any]]:
        """Check and respond to critical physiological needs."""
        # Hunger check
        if agent.physio.hunger > 0.8:
            if place and "food" in place.capabilities:
                return {
                    "action": "EAT",
                    "params": {"location": agent.place},
                    "private_thought": "I'm starving, I need to eat now."
                }
            # Find nearest food location
            food_places = [p for p in world.places.values() if "food" in p.capabilities]
            if food_places:
                return {
                    "action": "MOVE",
                    "params": {"to": food_places[0].name},
                    "private_thought": "I'm very hungry, I need to find food."
                }
        elif agent.physio.hunger > 0.6:
            if place and "food" in place.capabilities:
                if random.random() < 0.5:  # 50% chance to eat when moderately hungry
                    return {
                        "action": "EAT",
                        "params": {},
                        "private_thought": "I'm getting hungry, I should eat something."
                    }
        
        # Energy check
        if agent.physio.energy < 0.2:
            home_places = [p for p in world.places.values() if "home" in p.capabilities or p.name.lower() == "home"]
            if home_places:
                if agent.place == home_places[0].name:
                    return {
                        "action": "SLEEP",
                        "params": {},
                        "private_thought": "I'm exhausted, I need to sleep."
                    }
                return {
                    "action": "MOVE",
                    "params": {"to": home_places[0].name},
                    "private_thought": "I'm too tired, I need to go home and rest."
                }
        
        # Stress check
        if agent.physio.stress > 0.8:
            if place and "relax" in place.capabilities:
                return {
                    "action": "RELAX",
                    "params": {},
                    "private_thought": "I'm too stressed, I need to take a break."
                }
            return {
                "action": "RELAX",
                "params": {},
                "private_thought": "I'm overwhelmed, I need to calm down."
            }
        
        return None
    
    def _goal_driven_decision(self, agent: Any, world: 'World', tick: int) -> Optional[Dict[str, Any]]:
        """Make decisions based on agent's persona values and goals."""
        values = agent.persona.values if hasattr(agent.persona, 'values') else []
        goals = agent.persona.goals if hasattr(agent.persona, 'goals') else []
        
        # Check if agent should work (based on job)
        if agent.persona.job and agent.persona.job != "unemployed":
            from sim.agents.agents import JOB_SITE
            work_site = JOB_SITE.get(agent.persona.job)
            if work_site and agent.place == work_site:
                # Good time to work (morning/afternoon)
                hour = (tick * 5) // 60
                if 8 <= hour <= 17:  # 8 AM to 5 PM
                    if random.random() < 0.6:  # 60% chance to work during work hours
                        return {
                            "action": "WORK",
                            "params": {"task": agent.persona.job},
                            "private_thought": f"Time to focus on my work as a {agent.persona.job}."
                        }
        
        # Value-driven decisions
        if "ambition" in values or "career" in goals:
            if random.random() < 0.2:
                return {
                    "action": "WORK",
                    "params": {},
                    "private_thought": "I'm driven to work hard and achieve my goals."
                }
        
        if "curiosity" in values or "exploration" in goals:
            if random.random() < 0.25:
                return {
                    "action": "EXPLORE",
                    "params": {},
                    "private_thought": "My curiosity drives me to discover new things."
                }
        
        if "social" in values or "kindness" in values:
            # Look for other agents to interact with
            if agent.place in world.places:
                place = world.places[agent.place]
                other_agents = [a for a in place.agents_present if a != agent]
                if other_agents and random.random() < 0.3:
                    target = random.choice(other_agents)
                    return {
                        "action": "SAY",
                        "params": {"to": target.persona.name, "text": "Hello!"},
                        "private_thought": f"I should talk to {target.persona.name}."
                    }
        
        return None
    
    def _context_aware_decision(self, agent: Any, world: 'World', place: Any, tick: int) -> Optional[Dict[str, Any]]:
        """Make decisions based on current context (location, time, social)."""
        hour = (tick * 5) // 60
        
        # Morning routine
        if 6 <= hour <= 8:
            if place and "food" in place.capabilities and agent.physio.hunger > 0.3:
                if random.random() < 0.4:
                    return {
                        "action": "EAT",
                        "params": {},
                        "private_thought": "Time for breakfast."
                    }
        
        # Lunch time
        if 11 <= hour <= 13:
            if agent.physio.hunger > 0.4:
                if random.random() < 0.5:
                    return {
                        "action": "EAT",
                        "params": {},
                        "private_thought": "It's lunch time."
                    }
        
        # Evening relaxation
        if 18 <= hour <= 21:
            if agent.physio.stress > 0.3:
                if random.random() < 0.3:
                    return {
                        "action": "RELAX",
                        "params": {},
                        "private_thought": "Time to unwind after the day."
                    }
        
        # Late night - should sleep
        if hour >= 22 or hour < 6:
            if random.random() < 0.5:
                home_places = [p for p in world.places.values() if "home" in p.capabilities or p.name.lower() == "home"]
                if home_places:
                    if agent.place == home_places[0].name:
                        return {
                            "action": "SLEEP",
                            "params": {},
                            "private_thought": "It's late, I should get some sleep."
                        }
                    return {
                        "action": "MOVE",
                        "params": {"to": home_places[0].name},
                        "private_thought": "It's getting late, I should head home."
                    }
        
        return None
    
    def _probabilistic_decision(self, agent: Any) -> Optional[Dict[str, Any]]:
        """Make random decisions for variety."""
        roll = random.random()
        
        if roll < 0.1:  # 10% chance to think
            return {
                "action": "THINK",
                "params": {},
                "private_thought": "Let me think about my situation."
            }
        elif roll < 0.2:  # 10% chance to explore
            return {
                "action": "EXPLORE",
                "params": {},
                "private_thought": "I feel like exploring the area."
            }
        
        return None
    
    def _default_decision(self) -> Dict[str, Any]:
        """Return a default idle/think action."""
        return {
            "action": "THINK",
            "params": {},
            "private_thought": "I'm considering my options."
        }
    
    def _get_relevant_memories(self, agent: Any, start_dt) -> List[str]:
        """Get relevant memories for context."""
        relevant = []
        for query in ("today", "schedule", "recent"):
            for memory in agent.memory.recall(query, k=2):
                relevant.append(f"[{now_str(memory.t, start_dt)}] {memory.kind}: {memory.text}")
        return relevant