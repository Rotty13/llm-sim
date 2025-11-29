from typing import TYPE_CHECKING
from typing import Dict, Any, Optional, List
from sim.world.world_interface import WorldInterface  # Moved outside TYPE_CHECKING to ensure runtime availability

if TYPE_CHECKING:
    from sim.world.world_interface import WorldInterface
import json
from sim.utils.utils import now_str

class BaseController:
    """
    Base class for agent controllers. Subclasses should implement decision-making logic.
    """
    def decide(self, agent: Any, world: WorldInterface, obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the `decide` method.")

class LogicController(BaseController):
    """
    Controller that uses only the logic-based decision system.

    Notes:
        - All decision logic should reside in the controller, not in the agent.
    """
    def decide(self, agent: Any, world: WorldInterface, obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        if tick < agent.busy_until:
            return self._continue_action()

        # Retrieve relevant memories
        relevant_memories = self._get_relevant_memories(agent, start_dt)

        # Observations and roster
        env_obs = json.dumps(agent.obs_list)
        roster = self._get_roster(agent, world)

        # Decision-making
        decision = self._rule_based_decision(agent)
        if not decision:
            decision = self._probabilistic_decision(agent)
        if not decision:
            decision = self._default_decision()
        return decision

    def _continue_action(self) -> Dict[str, Any]:
        return {"action": "CONTINUE()", "private_thought": None, "memory_write": None}

    def _get_relevant_memories(self, agent: Any, start_dt) -> List[str]:
        relevant = []
        for query in ("today", "schedule", "rent", "meal", "work"):
            for memory in agent.memory.recall(query, k=1):
                relevant.append(f"[{now_str(memory.t, start_dt)}] {memory.kind}: {memory.text}")
        return relevant

    def _get_roster(self, agent: Any, world: WorldInterface) -> str:
        if hasattr(world, "_agents"):
            return ", ".join(sorted(a.persona.name for a in world._agents))
        return "NEARBY"

    def _rule_based_decision(self, agent: Any) -> Optional[Dict[str, Any]]:
        if agent.physio.hunger > 0.7:
            return {
                "action": "EAT()",
                "private_thought": "I need to eat something.",
                "memory_write": "I decided to eat due to hunger."
            }
        if agent.physio.stress > 0.8:
            return {
                "action": "RELAX()",
                "private_thought": "I need to reduce my stress.",
                "memory_write": "I decided to relax due to high stress."
            }
        return None

    def _probabilistic_decision(self, agent: Any) -> Optional[Dict[str, Any]]:
        import random
        if random.random() < 0.3:  # 30% chance to explore
            return {
                "action": "EXPLORE()",
                "private_thought": "I feel like exploring.",
                "memory_write": "I decided to explore the area."
            }
        return None

    def _default_decision(self) -> Dict[str, Any]:
        return {
            "action": "THINK()",
            "private_thought": "I am considering my options.",
            "memory_write": "I spent time thinking about my next move."
        }