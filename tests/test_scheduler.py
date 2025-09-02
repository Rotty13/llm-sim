from sim.scheduler import enforce_schedule, Appointment

def test_enforce_schedule_move():
    appts = [Appointment(at_min=60, place="Office", label="standup")]
    # tick=9 => 45 minutes after start; at_min=60 => 15min away -> move if not at Office
    forced = enforce_schedule(appts, place="Cafe", tick=9)
    assert forced and "MOVE" in forced
