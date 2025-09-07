import argparse
import yaml
import random
import os
from sim.llm.llm import llm

def timeout_heuristic(num_names, batch_size=100):
    # Based on observed: 94s for 100 names (worst case)
    # Scale linearly, round up to nearest 10s, min 30s
    base = 94
    per_name = base / batch_size  # ~0.94s per name
    timeout = int(per_name * num_names)
    timeout = ((timeout + 9) // 10) * 10  # round up to nearest 10s
    return max(30, timeout)


def base_name_prompt(kind: str, n: int, city: str, year: int, exclude_str: str):
    if kind == "first":
        label = "first_names"
        expert = "historical names"
        example = "John1, John2"
    else:
        label = "last_names"
        expert = "historical surnames"
        example = "Smith1, Smith2"
    system_prompt = (
        f"You are an expert in {expert}. You generate lists of unique, realistic names appropriate for residents of a given city and year. "
        f"Names must be authentic to the time and place, diverse, and should NOT repeat, use numeric suffixes, or be modern/international outliers. "
        f"Each name must be a single word (no spaces). Avoid using the same name with numbers (e.g., {example})."
    )
    user_prompt = (
        f"Generate a list of {n} unique {'first' if kind == 'first' else 'last'} names for {city} in {year}. Exclude these names: [{exclude_str}]. "
        f"Return ONLY a JSON array: {{{label}: [name1, name2, ...]}}"
    )
    return system_prompt, user_prompt, label

def generate_names(kind: str, city: str, year: int, num_names: int, seed: int, rng=None, max_tokens=2000, timeout=None, batch_size=100):
    if rng is None:
        rng = random
    names = set()
    excluded = set()
    label = "first_names" if kind == "first" else "last_names"
    batch_num = 1
    while len(names) < num_names:
        n = min(batch_size, num_names - len(names))
        exclude_str = ', '.join(sorted(excluded))
        system_prompt, user_prompt, label = base_name_prompt(kind, n, city, year, exclude_str)
        llm_seed = seed if seed is not None else rng.randint(-5000,5000)
        print(f"[DEBUG] Batch {batch_num}: Requesting {n} names, {len(names)} collected so far. Excluded: {len(excluded)}")
        batch_names = llm.chat_json(user_prompt, system=system_prompt, seed=llm_seed, max_tokens=max_tokens, timeout=timeout).get(label, [])
        if not batch_names or not isinstance(batch_names, list):
            print(f"[DEBUG] Batch {batch_num}: LLM returned no valid list.")
            batch_num += 1
            continue
        batch_names = [name for name in batch_names if name not in excluded and isinstance(name, str) and len(name.split()) == 1]
        new_names = set(batch_names) - excluded
        print(f"[DEBUG] Batch {batch_num}: {len(new_names)} new names added.")
        if new_names:
            names.update(new_names)
            excluded.update(new_names)
            batch_num += 1
        else:
            print(f"[DEBUG] No new names found in batch {batch_num}. Stopping.")
            break
    print(f"[DEBUG] Total names collected: {len(names)}")
    return sorted(names)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate city/time-period appropriate names and output to YAML.")
    parser.add_argument('--city', default='Lumière')
    parser.add_argument('--year', type=int, default=1900)
    parser.add_argument('--num_first', type=int, default=500)
    parser.add_argument('--num_last', type=int, default=500)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--out', default='configs/names.yaml')
    parser.add_argument('--max_tokens', type=int, default=2000, help='Maximum output tokens for LLM')
    parser.add_argument('--timeout', type=int, default=None, help='Timeout for LLM calls (seconds)')
    parser.add_argument('--batch_size', type=int, default=200, help='Batch size for name generation')
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Use heuristic for timeout if not provided
    if args.timeout is None:
        args.timeout = timeout_heuristic(max(args.num_first, args.num_last), batch_size=args.batch_size)
    print(f"Heuristic timeout for {max(args.num_first, args.num_last)} names: {args.timeout} seconds")

    # Generate all names in batches
    first_names = sorted(generate_names('first', args.city, args.year, args.num_first, args.seed, rng, max_tokens=args.max_tokens, timeout=args.timeout, batch_size=args.batch_size))
    last_names = sorted(generate_names('last', args.city, args.year, args.num_last, args.seed, rng, max_tokens=args.max_tokens, timeout=args.timeout, batch_size=args.batch_size))

    names_dict = {
        'first_names': first_names,
        'last_names': last_names
    }
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        yaml.safe_dump(names_dict, f, allow_unicode=True, sort_keys=False)
    print(f"Wrote {len(first_names)} first names and {len(last_names)} last names to {args.out}")
