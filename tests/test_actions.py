from sim.actions.actions import normalize_action

def test_normalize_string_ok():
    s=normalize_action("WORK({\"steps\": [\"INTERACT:CoffeeMachine\"]})")
    print(s)
    assert s.startswith("WORK(")

def test_normalize_dict_plan():
    s = normalize_action({"type":"PLAN","steps":["MOVE:Cafe"]})
    print(s)
    assert s.startswith("PLAN(") and "MOVE:Cafe" in s

if __name__ == "__main__":
    test_normalize_string_ok()
    test_normalize_dict_plan()