"""
AgentSchedule module for managing agent schedule enforcement.
Handles busy_until logic and appointment movement.
"""
class AgentSchedule:
    def __init__(self, agent):
        self.agent = agent

    def enforce_schedule(self, tick):
        if self.agent.busy_until > tick:
            return  # Agent is busy
        for appointment in self.agent.calendar:
            if appointment.start_tick == tick:
                self.agent.place = appointment.location
                self.agent.busy_until = appointment.end_tick
                break
