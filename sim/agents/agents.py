@dataclass
class Agent:
    # ...existing fields...

    def tick_update(self, world, tick: int):
        """
        Update agent state each tick: decay needs (with trait effects), update mood, and check aspirations.
        """
        self.physio.decay_needs(traits=self.persona.traits)
        # Mood logic: baseline + emotional reactivity + stress
        base = self.persona.emotional_modifiers.get("baseline_mood", 0.0)
        react = self.persona.emotional_modifiers.get("emotional_reactivity", 0.5)
        mood_val = base + react * (0.5 - self.physio.stress)
        if mood_val > 0.3:
            self.physio.mood = "positive"
        elif mood_val < -0.3:
            self.physio.mood = "negative"
        else:
            self.physio.mood = "neutral"
        # Aspirations: if agent has a long-term goal, nudge plan
        if self.persona.aspirations:
            for asp in self.persona.aspirations:
                if asp == "wealth" and self.physio.energy > 0.5:
                    if "WORK" not in self.plan:
                        self.plan.append("WORK")
                if asp == "friendship" and self.physio.social < 0.7:
                    if "SAY" not in self.plan:
                        self.plan.append("SAY")
                if asp == "exploration" and self.physio.energy > 0.3:
                    if "EXPLORE" not in self.plan:
                        self.plan.append("EXPLORE")

    def perform_action(self, action: str, world: Any, tick: int):
        """
        Stub: Perform the given action in the simulation context.
        Args:
            action: Action string (e.g., 'MOVE', 'EAT', etc.)
            world: The simulation world object
            tick: Current simulation tick
        """
        # For now, just log the action and update place if MOVE
        if action.startswith("MOVE"):
            import json
            payload = json.loads(action[action.find("(")+1:action.rfind(")")])
            dest = payload.get("to")
            if dest:
                self.place = dest
            # Extend with more action handling as needed
            # Optionally: print or log action
            print(f"Agent {self.persona.name} performs action: {action} at tick {tick}")

    def serialize_state(self) -> dict:
        """Stub: Serialize agent state for saving."""
        # Placeholder for future serialization logic
        return {}

    def load_state(self, state: dict):
        """Stub: Load agent state from saved data."""
        # Placeholder for future loading logic
        pass

    def checkpoint_stub(self):
        """Stub for checkpoint/resume logic."""
        # Placeholder for future checkpoint logic
        pass

    def die(self, tick: int):
        """Mark the agent as deceased and record time of death."""
        self.alive = False
        self.time_of_death = tick

    def mourn_stub(self, deceased_name: str):
        """Stub for mourning/legacy logic when another agent dies."""
        # Placeholder for future mourning/legacy logic
        pass

    def receive_income(self, amount: float):
        """Add income to the agent's inventory as money."""
        from sim.inventory.inventory import ITEMS
        self.inventory.add(ITEMS["money"], int(amount))

    def perform_job_stub(self):
        """Stub for job/career action logic."""
        # Placeholder for future job/career logic
        pass

    def update_life_stage(self):
        """Update the agent's life stage based on age and persona's age_transitions."""
        for stage, threshold in sorted(self.persona.age_transitions.items(), key=lambda x: x[1], reverse=True):
            if self.persona.age >= threshold:
                self.persona.life_stage = stage
                break

    @property
    def money_balance(self) -> int:
        """Return the agent's current money balance (as quantity of 'money' in inventory)."""
        return self.inventory.get_quantity("money")

    def add_money(self, amount: int):
        """Add money to the agent's inventory."""
        from sim.inventory.inventory import ITEMS
        self.inventory.add(ITEMS["money"], amount)

    def remove_money(self, amount: int) -> bool:
        """Remove money from the agent's inventory. Returns True if successful."""
        return self.inventory.remove("money", amount)

    def step_interact(self, world, participants: list, obs: str, tick: int, start_dt, incoming_message: Optional[dict], loglist: Optional[list] = None):
        """
        Cohesive step: agent converses, decays needs, updates moodlets, decides, and acts in the world.
        Returns the conversation decision dict.
        """
        # Decay needs at each tick
        self.physio.decay_needs()
        # Update moodlets
        self.tick_moodlets()
        # Conversation step
        conv_decision = self.decide_conversation(participants, obs, tick, incoming_message, start_dt=start_dt, loglist=loglist)
        if conv_decision and "new_mood" in conv_decision:
            self.physio.mood = conv_decision["new_mood"]
        if conv_decision and "memory_write" in conv_decision and conv_decision["memory_write"]:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="episodic", text=conv_decision["memory_write"], importance=0.5))
        # Action step
        action_decision = self.decide(world, obs, tick, start_dt)
        self.act(world, action_decision, tick)
        return conv_decision
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=lambda: LogicController())
    memory: MemoryStore = field(default_factory=MemoryStore)
    physio: Physio = field(default_factory=Physio)
    plan: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: MemoryManager = field(default_factory=MemoryManager)
    inventory_handler: InventoryHandler = field(default_factory=InventoryHandler)
    decision_controller: DecisionController = field(default_factory=DecisionController)
    movement_controller: MovementController = field(default_factory=MovementController)
    busy_until: int = 0  # Tick until which the agent is busy
    alive: bool = True
    time_of_death: Optional[int] = None
    relationships: Dict[str, float] = field(default_factory=dict)
    social_memory: List[Dict[str, Any]] = field(default_factory=list)

    def perform_action(self, action: str, world: Any, tick: int):
        """
        Stub: Perform the given action in the simulation context.
        Args:
            action: Action string (e.g., 'MOVE', 'EAT', etc.)
            world: The simulation world object
            tick: Current simulation tick
        """
        # For now, just log the action and update place if MOVE
        if action.startswith("MOVE"):
            import json
            payload = json.loads(action[action.find("(")+1:action.rfind(")")])
            dest = payload.get("to")
            if dest:
                    self.place = dest
            # Extend with more action handling as needed
            # Optionally: print or log action
            print(f"Agent {self.persona.name} performs action: {action} at tick {tick}")
    persona: Persona
    place: str
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=lambda: LogicController())
    memory: MemoryStore = field(default_factory=MemoryStore)
    physio: Physio = field(default_factory=Physio)
    plan: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: MemoryManager = field(default_factory=MemoryManager)
    inventory_handler: InventoryHandler = field(default_factory=InventoryHandler)
    decision_controller: DecisionController = field(default_factory=DecisionController)
    movement_controller: MovementController = field(default_factory=MovementController)
    busy_until: int = 0  # Tick until which the agent is busy
    alive: bool = True
    time_of_death: Optional[int] = None
    relationships: Dict[str, float] = field(default_factory=dict)
    social_memory: List[Dict[str, Any]] = field(default_factory=list)

    def serialize_state(self) -> dict:
        """Stub: Serialize agent state for saving."""
        # Placeholder for future serialization logic
        return {}

    def load_state(self, state: dict):
        """Stub: Load agent state from saved data."""
        # Placeholder for future loading logic
        pass

    def checkpoint_stub(self):
        """Stub for checkpoint/resume logic."""
        # Placeholder for future checkpoint logic
        pass

    def die(self, tick: int):
        """Mark the agent as deceased and record time of death."""
        self.alive = False
        self.time_of_death = tick

    def mourn_stub(self, deceased_name: str):
        """Stub for mourning/legacy logic when another agent dies."""
        # Placeholder for future mourning/legacy logic
        pass

    def receive_income(self, amount: float):
        """Add income to the agent's inventory as money."""
        from sim.inventory.inventory import ITEMS
        self.inventory.add(ITEMS["money"], int(amount))

    def perform_job_stub(self):
        """Stub for job/career action logic."""
        # Placeholder for future job/career logic
        pass

    def update_life_stage(self):
        """Update the agent's life stage based on age and persona's age_transitions."""
        for stage, threshold in sorted(self.persona.age_transitions.items(), key=lambda x: x[1], reverse=True):
            if self.persona.age >= threshold:
                self.persona.life_stage = stage
                break


    @property
    def money_balance(self) -> int:
        """Return the agent's current money balance (as quantity of 'money' in inventory)."""
        return self.inventory.get_quantity("money")

    def add_money(self, amount: int):
        """Add money to the agent's inventory."""
        from sim.inventory.inventory import ITEMS
        self.inventory.add(ITEMS["money"], amount)

    def remove_money(self, amount: int) -> bool:
        """Remove money from the agent's inventory. Returns True if successful."""
        return self.inventory.remove("money", amount)

    def update_relationship(self, other: str, delta: float):
        """Update relationship score with another agent."""
        self.relationships[other] = self.relationships.get(other, 0.0) + delta

    def remember_social_interaction(self, interaction: Dict[str, Any]):
        """Add a social interaction to social memory."""
        self.social_memory.append(interaction)

    def group_conversation_stub(self, participants: list, topic: str):
        """Stub for group conversation mechanics."""
        # Placeholder for future group conversation logic
        pass
    # ...existing code...
    def add_moodlet(self, moodlet: str, duration: int):
        """Add or refresh a moodlet for a given duration (in ticks)."""
        self.physio.moodlets[moodlet] = duration

    def tick_moodlets(self):
        """Decrement moodlet durations and remove expired ones."""
        expired = [k for k, v in self.physio.moodlets.items() if v <= 1]
        for k in expired:
            del self.physio.moodlets[k]
        for k in self.physio.moodlets:
            self.physio.moodlets[k] -= 1

    def set_emotional_state(self, state: str):
        """Set the agent's current emotional state."""
        self.physio.emotional_state = state

        @property
        def money_balance(self) -> int:
            """Return the agent's current money balance (as quantity of 'money' in inventory)."""
            return self.inventory.get_quantity("money")

        def add_money(self, amount: int):
            """Add money to the agent's inventory."""
            from sim.inventory.inventory import ITEMS
            self.inventory.add(ITEMS["money"], amount)

        def remove_money(self, amount: int) -> bool:
            """Remove money from the agent's inventory. Returns True if successful."""
            return self.inventory.remove("money", amount)
    persona: Persona
    place: str
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=lambda: LogicController())
    memory: MemoryStore = field(default_factory=MemoryStore)
    physio: Physio = field(default_factory=Physio)
    plan: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: MemoryManager = field(default_factory=MemoryManager)
    inventory_handler: InventoryHandler = field(default_factory=InventoryHandler)
    decision_controller: DecisionController = field(default_factory=DecisionController)
    movement_controller: MovementController = field(default_factory=MovementController)

    busy_until: int = 0  # Tick until which the agent is busy

    def step_interact(self, world, participants: list, obs: str, tick: int, start_dt, incoming_message: Optional[dict], loglist: Optional[list] = None):
        """
        Cohesive step: agent converses, decays needs, updates moodlets, decides, and acts in the world.
        Returns the conversation decision dict.
        """
        # Decay needs at each tick
        self.physio.decay_needs()
        # Update moodlets
        self.tick_moodlets()
        # Conversation step
        conv_decision = self.decide_conversation(participants, obs, tick, incoming_message, start_dt=start_dt, loglist=loglist)
        if conv_decision and "new_mood" in conv_decision:
            self.physio.mood = conv_decision["new_mood"]
        if conv_decision and "memory_write" in conv_decision and conv_decision["memory_write"]:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="episodic", text=conv_decision["memory_write"], importance=0.5))
        # Action step
        action_decision = self.decide(world, obs, tick, start_dt)
        self.act(world, action_decision, tick)
        return conv_decision

    def decide_conversation(self, participants: List[Agent],obs: str, tick: int, incoming_message: Optional[dict],start_dt: Optional[datetime] = None,   loglist: Optional[List[Dict[str, Any]]] = None) -> Dict[str,Any]:
        """
        Decide on a conversational response using LLM, considering conversation history.
        """
        # SYSTEM prompt for conversation
        system_prompt = (
            "You are a human engaged in a conversation. You are not being simulated or in a simulation. You are yourself and your memories are real.\n"
            "If you must recall something in your distant past or childhood, you may invent it. don't reference specific names or places.\n"
            "Respond as naturally as possible, considering your persona, context, and conversation history. 1-3 sentences only.\n"
            "Return ONLY JSON with keys: reply, private_thought, memory_write (nullable).\n"
            "Example: {\"to\":\"David\",\"reply\":\"Hello! How can I help you?\",\"private_thought\":\"I feel helpful.\",\"memory_write\":\"I greeted someone.\",\"new_mood\":\"happy\"}\n"
        )

        # Build conversation history string
        history_str = "\n".join([
            f"{entry['role']}: {entry['content']}" for entry in self.conversation_history[-15:]
        ])

        # USER prompt for conversation
        user_prompt = (
                (
                    f"You are {self.persona.name} (job: {self.persona.job}, city: {self.persona.city}) Bio: {self.persona.bio}.\n" +
                    (f"The date is {now_str(tick,start_dt).split()[0]}.\n" if start_dt else "") +
                    f"Participants: {', '.join(p.persona.name for p in participants if p != self)}.\n" +
                    f"Observations: {obs}\n\n" +
                    f"Time {now_str(tick,start_dt)}. " +
                    f"Location {self.place}. Mood {self.physio.mood}.\n" +
                    f"Conversation history:\n{history_str}\n" +
                    f"My values: {', '.join(self.persona.values)}.\n" +
                    f"My goals: {', '.join(self.persona.goals)}.\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("conversation", k=5)) + "\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("life", k=5)) + "\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("recent", k=5)) + "\n" +
                    f"Incoming message: {json.dumps(incoming_message)}\n\n" +
                    "Craft a thoughtful and context-aware reply.\n"
                )
        )

        out = llm.chat_json(user_prompt, system=system_prompt, max_tokens=256)
        # sanity carve
        if not isinstance(out, dict):
            out = {"reply":"Sorry, I didn't understand.","private_thought":None,"memory_write":None}
        # Update conversation history
        if incoming_message is not None:
            # Handle new format: {'to': ..., 'from': ..., 'text': ...}
            msg_role = "user"
            msg_content = ""
            if isinstance(incoming_message, dict):
                # Compose a readable string for the message
                msg_from = incoming_message.get("from", "Unknown")
                msg_to = incoming_message.get("to", "Unknown")
                msg_text = incoming_message.get("text", "")
                msg_content = f"From: {msg_from}, To: {msg_to}, Text: {msg_text}"
            else:
                msg_content = str(incoming_message)
            self.conversation_history.append({"role": msg_role, "content": json.dumps(incoming_message)})
        out['from']=self.persona.name
        self.conversation_history.append({"role": "agent", "content": json.dumps(out)})
        if loglist is not None:
            loglist.append(out)
        return out

    # runtime
    busy_until: int = -1
    _last_say_tick: int = -999
    _last_diary_tick: int = -999
    _last_diary: str = ""

    def add_observation(self, text: str):
        self.memory_manager.add_observation(text)

    def _maybe_write_diary(self, text: str, tick: int):
        if not text:
            return
        if (tick - self._last_diary_tick) < 6:
            return
        sim = SequenceMatcher(None, self.memory_manager._norm_text(self._last_diary), self.memory_manager._norm_text(text)).ratio()
        if sim < 0.93:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

    def _work_allowed_here(self, world) -> bool:
        expected = JOB_SITE.get(self.persona.job)
        return bool(expected) and self.place == expected

    def _eat_allowed_here(self, world) -> bool:
        p = world.places[self.place]
        return "food" in p.capabilities or "food_home" in p.capabilities

    def decide(self, world, obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        """
        Enhanced decision-making logic for agents, including rule-based and probabilistic choices.

        Notes:
            - Decision logic should only reside in the controller.
            - Enforces schedules using the enforce_schedule function.
        """
        # Check and enforce schedule
        move_command = enforce_schedule(self.calendar, self.place, tick, self.busy_until)
        if move_command:
            return {"action": "MOVE", "params": {"to": move_command.split('"')[3]}, "private_thought": "I need to move to my appointment."}


        # Rule-based decision-making
        if self.physio.hunger > 0.8:
            return {"action": "EAT", "private_thought": "I'm feeling very hungry."}
        elif self.physio.energy < 0.3:
            return {"action": "SLEEP", "private_thought": "I'm too tired to continue."}
        elif self.physio.stress > 0.5:
            return {"action": "RELAX", "private_thought": "I need to relax and reduce my stress."}
        elif self.physio.fun < 0.3:
            return {"action": "EXPLORE", "private_thought": "I'm bored and need to have some fun."}
        elif self.physio.social < 0.3:
            return {"action": "SAY", "private_thought": "I'm feeling lonely and want to talk to someone.", "params": {}}


        # Incorporate persona values, goals, and traits into decision-making
        traits = self.persona.traits if hasattr(self.persona, 'traits') else {}
        # Conscientiousness: more likely to work
        if traits.get("conscientiousness", 0.5) > 0.7 and random.random() < traits["conscientiousness"]:
            return {"action": "WORK", "private_thought": "My conscientiousness drives me to work diligently."}
        # Openness: more likely to explore
        if traits.get("openness", 0.5) > 0.6 and random.random() < traits["openness"]:
            return {"action": "EXPLORE", "private_thought": "My openness makes me want to explore new things."}
        # Extraversion: more likely to socialize
        if traits.get("extraversion", 0.5) > 0.6 and random.random() < traits["extraversion"]:
            return {"action": "SAY", "private_thought": "I feel like socializing with others.", "params": {}}
        # Neuroticism: more likely to relax
        if traits.get("neuroticism", 0.5) > 0.6 and random.random() < traits["neuroticism"]:
            return {"action": "RELAX", "private_thought": "I need to relax and manage my stress."}
        # Agreeableness: more likely to help/interact
        if traits.get("agreeableness", 0.5) > 0.6 and random.random() < traits["agreeableness"]:
            return {"action": "INTERACT", "private_thought": "I want to help or interact with others.", "params": {"action_type": "help"}}

        # Existing value/goal-based logic
        if "ambition" in self.persona.values and "achieve goal" in self.persona.goals:
            if random.random() < 0.3:
                return {"action": "WORK", "private_thought": "I feel motivated to work on my goals."}
        if "curiosity" in self.persona.values:
            if random.random() < 0.4:
                return {"action": "EXPLORE", "private_thought": "My curiosity drives me to explore."}
        if self.physio.stress > 0.7 and "relaxation" in self.persona.values:
            return {"action": "RELAX", "private_thought": "I value relaxation and need to reduce stress."}

        # Probabilistic decision-making for exploration
        if random.random() < 0.2:
            return {"action": "EXPLORE", "private_thought": "I feel like exploring the area."}

        # Default action
        return {"action": "IDLE", "private_thought": "I have nothing to do right now."}

    def enforce_schedule(self, tick: int):
        """
        Integrates the `busy_until` attribute with the scheduler to enforce appointments and schedules.
        """
        if self.busy_until > tick:
            return  # Agent is busy

        for appointment in self.calendar:
            if appointment.start_tick == tick:
                self.place = appointment.location
                self.busy_until = appointment.end_tick
                break

    def update_relationships(self, world):
        """
        Updates item ownership using the world's `item_ownership` dictionary.
        """
        for item_stack in self.inventory.stacks:
            world.item_ownership[item_stack.item.id] = self.persona.name

    def act(self, world, decision: Dict[str, Any], tick: int):
        """
        Perform the action decided by the agent.
        Supports actions: MOVE, EAT, SLEEP, RELAX, EXPLORE, WORK, SAY, INTERACT, THINK, CONTINUE.
        """
        from sim.actions.actions import get_action_duration, get_action_effects, ACTION_DURATIONS
        
        action = decision.get("action", "").upper()
        params = decision.get("params", {})

        # Get action duration and effects
        duration = get_action_duration(action, params)
        effects = get_action_effects(action, params)

        # Modulate action effects by personality traits
        traits = self.persona.traits
        if action == "RELAX":
            # More extraverted/agreeable agents relax more efficiently
            relax_boost = 0.1 * (traits.get("extraversion",0.5) + traits.get("agreeableness",0.5) - 1.0)
            self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.2) + relax_boost)
        elif action == "WORK":
            # Conscientiousness increases work energy cost, neuroticism increases stress
            work_penalty = 0.05 * (traits.get("conscientiousness",0.5) - 0.5)
            stress_penalty = 0.05 * (traits.get("neuroticism",0.5) - 0.5)
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.15) - work_penalty)
            self.physio.stress = min(1.0, self.physio.stress + effects.get("stress", 0.1) + stress_penalty)
        elif action == "SAY":
            # Extraversion increases social gain
            social_boost = 0.1 * (traits.get("extraversion",0.5) - 0.5)
            self.physio.social = min(1.0, self.physio.social + social_boost)
        # ...existing code for other actions...
            def personality_memory_importance(self, item: MemoryItem) -> float:
                """
                Adjust memory importance by personality traits (e.g., neuroticism boosts negative, openness boosts novel).
                """
                traits = self.persona.traits
                importance = item.importance
                if "sad" in item.text or "failure" in item.text:
                    importance += 0.2 * traits.get("neuroticism",0.5)
                if "new" in item.text or "explore" in item.text:
                    importance += 0.2 * traits.get("openness",0.5)
                if "friend" in item.text or "talk" in item.text:
                    importance += 0.2 * traits.get("extraversion",0.5)
                return max(0.0, min(1.0, importance))
        if action == "MOVE":
            destination = params.get("to")
            if destination:
                self.movement_controller.move_to(self, world, destination)
            self.busy_until = tick + duration

        elif action == "EAT":
            self.physio.hunger = max(0.0, self.physio.hunger + effects.get("hunger", -0.5))
            self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.1))
            self.busy_until = tick + duration

        elif action == "SLEEP":
            self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.8))
            self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.3))
            self.busy_until = tick + duration

        elif action == "RELAX":
            self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.2))
            self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.05))
            self.busy_until = tick + duration

        elif action == "EXPLORE":
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.1))
            self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.05))
            self.busy_until = tick + duration

        elif action == "WORK":
            # Validate work location
            if self._work_allowed_here(world):
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.15))
                self.physio.stress = min(1.0, self.physio.stress + effects.get("stress", 0.1))
                self.physio.hunger = min(1.0, self.physio.hunger + effects.get("hunger", 0.1))
                self.busy_until = tick + duration
                # Add work reward (money)
                from sim.inventory.inventory import ITEMS
                money_item = ITEMS.get("money")
                if money_item:
                    reward = params.get("reward", 10)
                    self.inventory.add(money_item, reward)
            else:
                # Cannot work here, reduce to think action
                self.busy_until = tick + 1

        elif action == "SAY":
            text = params.get("text", "")
            target = params.get("to")
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.01))
            self.busy_until = tick + duration
            # Record in memory
            if text:
                self.memory_manager.write_memory(MemoryItem(
                    t=tick,
                    kind="episodic",
                    text=f"I said '{text}'" + (f" to {target}" if target else ""),
                    importance=0.3
                ))

        elif action == "INTERACT":
            target = params.get("target", "")
            action_type = params.get("action_type", "observe")
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.02))
            self.busy_until = tick + duration
            # Record interaction in memory
            if target:
                self.memory_manager.write_memory(MemoryItem(
                    t=tick,
                    kind="episodic",
                    text=f"I {action_type}d {target}",
                    importance=0.4
                ))

        elif action == "THINK":
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.01))
            self.busy_until = tick + duration

        elif action == "CONTINUE":
            # Do nothing, maintain current state
            pass

        else:
            # Unknown action, default to think
            self.busy_until = tick + 1

        # Broadcast the action to the world
        world.broadcast(self.place, {"actor": self.persona.name, "action": action, "params": params, "tick": tick})

    def move_to(self, world, destination: str) -> bool:
        """
        Move the agent to a new location if valid.
        """
        return self.movement_controller.move_to(self, world, destination)

    def use_item(self, item: Item) -> bool:
        """
        Use an item from the agent's inventory.
        """
        if self.inventory.has(item.id):
            self.inventory.remove(item.id, 1)
            if item.effects:
                for effect, value in item.effects.items():
                    if hasattr(self.physio, effect):
                        current_value = getattr(self.physio, effect)
                        setattr(self.physio, effect, max(0.0, current_value + value))
            return True
        return False

    def initialize_schedule(self, schedule_data):
        """
        Initialize the agent's schedule from the provided data.
        Args:
            schedule_data (list): List of schedule entries (dicts or Appointment objects).
        """
        self.calendar = []
        for entry in schedule_data:
            if isinstance(entry, Appointment):
                self.calendar.append(entry)
            elif isinstance(entry, dict):
                try:
                    appt = Appointment(
                        start_tick=entry.get("start_tick", 0),
                        end_tick=entry.get("end_tick", 0),
                        location=entry.get("location", ""),
                        label=entry.get("label", "")
                    )
                    self.calendar.append(appt)
                except (TypeError, KeyError):
                    pass  # Skip invalid entries

    def deposit_item_to_place(self, world, item_name, quantity):
        """
        Deposit an item from agent's inventory to the current place's inventory.
        """
        from sim.inventory.inventory import ITEMS
        if self.inventory.get_quantity(item_name) >= quantity:
            self.inventory.remove(item_name, quantity)
            place_obj = world.places[self.place]
            item_obj = ITEMS[item_name]
            place_obj.inventory.add(item_obj, quantity)
            return True
        return False

    def withdraw_item_from_place(self, world, item_name, quantity):
        """
        Withdraw an item from the current place's inventory to agent's inventory.
        """
        from sim.inventory.inventory import ITEMS
        place_obj = world.places[self.place]
        if place_obj.inventory.get_quantity(item_name) >= quantity:
            place_obj.inventory.remove(item_name, quantity)
            item_obj = ITEMS[item_name]
            self.inventory.add(item_obj, quantity)
            return True
        return False
