#!/usr/bin/env python3
from __future__ import annotations
import argparse, yaml, json
from datetime import datetime, timedelta
from pathlib import Path


from sim.world import World, Place, Vendor
from sim.agents import Agent, Persona, Appointment, now_str

def load_world(world_yaml: Path) -> World:
    data = yaml.safe_load(world_yaml.read_text())
    places = {}
    for p in data.get("places", []):
        vendor = None
        if "vendor" in p:
            v = p["vendor"]
            vendor = Vendor(prices=v.get("prices",{}), stock=v.get("stock",{}), buyback=v.get("buyback",{}))
        places[p["name"]] = Place(
            name=p["name"],
            neighbors=list(p.get("neighbors",[])),
            capabilities=set(p.get("capabilities",[])),
            vendor=vendor,
            purpose=p.get("purpose","")
        )
    return World(places=places)

def load_agents(personas_yaml: Path, city: str) -> list[Agent]:
    data = yaml.safe_load(personas_yaml.read_text())
    agents = []
    for p in data.get("people", []):
        persona = Persona(
            name=p["name"], age=int(p["age"]), job=str(p["job"]),
            city=city, bio=p.get("bio",""), values=list(p.get("values",[])), goals=list(p.get("goals",[]))
        )
        start = p.get("start_place","Street")
        cal = []
        if "dev" in persona.job:
            cal = [Appointment(at_min=60, place="Office", label="standup")]
        elif "barista" in persona.job:
            cal = [Appointment(at_min=0, place="Cafe", label="shift")]
        agents.append(Agent(persona=persona, place=start, calendar=cal))
    return agents

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=str(Path(__file__).resolve().parents[1] / "configs" / "world.yaml"))
    ap.add_argument("--personas", default=str(Path(__file__).resolve().parents[1] / "configs" / "personas.yaml"))
    ap.add_argument("--ticks", type=int, default=36)
    ap.add_argument("--logdir", default=str(Path(__file__).resolve().parents[1] / "data" / "logs"))
    args = ap.parse_args()

    world = load_world(Path(args.world))
    agents = load_agents(Path(args.personas), city=yaml.safe_load(Path(args.world).read_text()).get("city","City"))

    # expose roster to prompt (simple hook)
    world._agents = agents  # used by Agent.decide() to print roster

    start = datetime(2025, 8, 31, 9, 0, 0)

    # run
    for t in range(1, args.ticks+1):
        # perceptions per agent
        perceptions = {}
        for ag in agents:
            obs = []
            for evt in list(world.events):
                if evt.get("place")==ag.place and evt.get("actor")!=ag.persona.name:
                    kind, text = evt.get("kind"), evt.get("text","")
                    obs.append(f"{evt['actor']} {kind} {text}")
            perceptions[ag.persona.name] = "; ".join(obs) if obs else "(quiet)"

        for ag in agents:
            decision = ag.decide(world, perceptions[ag.persona.name], t, start)
            ag.act(world, decision, t)

    # write transcript
    logdir = Path(args.logdir); logdir.mkdir(parents=True, exist_ok=True)
    tslabel = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = logdir / f"run_{tslabel}.log"
    with outpath.open("w", encoding="utf-8") as f:
        f.write("--- Public log (last 30 events) ---\n")
        for evt in list(world.events)[-30:]:
            ts = now_str(evt['t'], start)
            kind = evt.get("kind")
            if kind == "say":
                raw = evt["text"][evt["text"].find("(")+1:evt["text"].rfind(")")]
                try:
                    payload = json.loads(raw)
                except Exception:
                    try:
                        payload = json.loads(raw.replace("'", '"'))
                    except Exception:
                        payload = {}
                msg = payload.get("text","(…)")
                f.write(f"[{ts} @ {evt['place']}] {evt['actor']}: {msg}\n")
            elif kind == "move":
                try:
                    payload = json.loads(evt["text"][evt["text"].find("(")+1:evt["text"].rfind(")")])
                    dest = payload.get("to","?")
                except Exception:
                    dest = "?"
                f.write(f"[{ts} @ {evt['place']}] {evt['actor']} MOVE → {dest}\n")
            else:
                f.write(f"[{ts} @ {evt['place']}] {evt['actor']} {evt['text']}\n")

        # memory summaries
        def print_mem(agent: Agent):
            items = agent.memory.items
            by_kind = {"autobio":0, "episodic":0, "semantic":0, "tom":0}
            for m in items: by_kind[m.kind] = by_kind.get(m.kind, 0) + 1
            f.write(f"\n### {agent.persona.name} – Memory summary\n")
            f.write(f"Counts  | autobio={by_kind.get('autobio',0)}  episodic={by_kind.get('episodic',0)}  semantic={by_kind.get('semantic',0)}  tom={by_kind.get('tom',0)}\n")
            recent = sorted(items, key=lambda m: m.t, reverse=True)[:5]
            for m in recent:
                f.write(f"  - [{now_str(m.t,start)}] {m.kind}: {m.text}\n")

        f.write("\n--- Memory summaries ---\n")
        for ag in agents: print_mem(ag)

        # run summary
        f.write("\n--- Run summary ---\n")
        for ag in agents:
            f.write(f"{ag.persona.name} — place={ag.place}, energy={ag.physio.energy:.2f}, hunger={ag.physio.hunger:.2f}, stress={ag.physio.stress:.2f}, memories={len(ag.memory.items)}\n")

    print(f"Wrote log to {outpath}")

if __name__ == "__main__":
    main()
