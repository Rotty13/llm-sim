import argparse
import yaml
import random
import os
from sim.llm.llm_ollama import llm

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
        system_prompt = (
            f"You are an expert in {expert}. You generate lists of unique, realistic first names appropriate for residents of a given city and year. "
            f"Names must be authentic to the time and place, and should be highly diverse, including international, rare, and less common names, as well as names from minority groups. "
            f"Do NOT repeat, use numeric suffixes, or use modern/international outliers inappropriate for the year. "
            f"Each name must be a single word (no spaces). Avoid using the same name with numbers (e.g., {example}). "
            f"For each name, always include a 'sex' field: 'male', 'female', or 'unisex'."
        )
        user_prompt = (
            f"Generate a list of {n} unique and highly diverse first names for {city} in {year}. Include international, rare, and minority names. Exclude these names: [{exclude_str}]. "
            "Return ONLY a JSON array in the following format: {first_names: [ {name: '...', sex: 'male|female|unisex'}, ... ] }"
        )
    else:
        label = "last_names"
        expert = "historical surnames"
        example = "Smith1, Smith2"
        system_prompt = (
            f"You are an expert in {expert}. You generate lists of unique, realistic last names appropriate for residents of a given city and year. "
            f"Names must be authentic to the time and place, diverse, and should NOT repeat, use numeric suffixes, or be modern/international outliers. "
            f"Each name must be a single word (no spaces). Avoid using the same name with numbers (e.g., {example})."
        )
        user_prompt = (
            f"Generate a list of {n} unique last names for {city} in {year}. Exclude these names: [{exclude_str}]. "
            f"Return ONLY a JSON array: {{{label}: [name1, name2, ...]}}"
        )
    return system_prompt, user_prompt, label

def generate_names(kind: str, city: str, year: int, num_names: int, seed: int, rng=None, max_tokens=6000, timeout=None, batch_size=100, excluded_names=None):
    if rng is None:
        rng = random
    names = []
    excluded = set(excluded_names) if excluded_names else set()
    label = "first_names" if kind == "first" else "last_names"
    batch_num = 1
    retries:int=0
    while len(names) < num_names:
        n = batch_size
        exclude_str = ', '.join(sorted(excluded))
        system_prompt, user_prompt, label = base_name_prompt(kind, n, city, year, exclude_str)
        llm_seed = seed if seed is not None else rng.randint(-5000,5000)
        print(f"[DEBUG] Batch {batch_num}: Requesting {n} names, {len(names)} collected so far. Excluded: {len(excluded)}")
        batch_names = llm.chat_json(user_prompt, system=system_prompt, seed=llm_seed, max_tokens=max_tokens, timeout=timeout).get(label, [])
        new_names = []
        if not batch_names or not isinstance(batch_names, list):
            print(f"[DEBUG] Batch {batch_num}: LLM returned no valid list.")
            batch_num += 1
        else:
            if kind == "first":
                # Expect dicts with name and sex
                for entry in batch_names:
                    if (
                        isinstance(entry, dict)
                        and 'name' in entry
                        and 'sex' in entry
                        and isinstance(entry['name'], str)
                        and entry['name'] not in excluded
                        and entry['sex'] in ['male', 'female', 'unisex']
                        and len(entry['name'].split()) == 1
                    ):
                        new_names.append(entry)
            else:
                # Last names: expect strings
                for name in batch_names:
                    if name not in excluded and isinstance(name, str) and len(name.split()) == 1:
                        new_names.append(name)
        print(f"[DEBUG] Batch {batch_num}: {len(new_names)} new names added.")
        if new_names:
            # Only add up to num_names total
            to_add = new_names[:num_names - len(names)]
            if kind == "first":
                names.extend(to_add)
                excluded.update([entry['name'] for entry in to_add])
            else:
                names.extend(to_add)
                excluded.update(to_add)
            batch_num += 1
        else:
            if retries >= 3:
                print(f"[DEBUG] No new names found in batch {batch_num} after {retries} retries. Stopping.")
                break
            print(f"[DEBUG] No new names found in batch {batch_num}. Retrying (attempt {retries+1}/3).")
            retries += 1
    print(f"[DEBUG] Total names collected: {len(names)}")
    # Sort by name for first names, alphabetically for last names
    if kind == "first":
        return sorted(names, key=lambda x: x['name'])
    else:
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
    parser.add_argument('--batch_size', type=int, default=100, help='Batch size for name generation')
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Load existing names for additive generation
    existing_first_names = []
    existing_last_names = []
    if os.path.exists(args.out):
        with open(args.out, 'r', encoding='utf-8') as f:
            try:
                names_data = yaml.safe_load(f)
                ef = names_data.get('first_names', [])
                el = names_data.get('last_names', [])
                # Accept both dict and str for first_names
                for fn in ef:
                    if isinstance(fn, dict) and 'name' in fn and 'sex' in fn:
                        existing_first_names.append(fn)
                    elif isinstance(fn, str):
                        existing_first_names.append({'name': fn, 'sex': 'unisex'})
                for ln in el:
                    if isinstance(ln, str):
                        existing_last_names.append(ln)
            except Exception as e:
                print(f"[WARNING] Could not parse existing names.yaml: {e}")

    # Use heuristic for timeout if not provided
    if args.timeout is None:
        args.timeout = timeout_heuristic(max(args.num_first, args.num_last), batch_size=args.batch_size)
    print(f"Heuristic timeout for {max(args.num_first, args.num_last)} names: {args.timeout} seconds")

    # Prepare exclusion lists
    excluded_first = sorted([fn['name'] for fn in existing_first_names if 'name' in fn])
    excluded_last = sorted(existing_last_names)

    # Helper to sort first names by name
    def sort_first_names(names):
        return sorted(names, key=lambda x: x['name'])

    # Helper to sort last names alphabetically
    def sort_last_names(names):
        return sorted(names)

    # If enough first names, use only those (sorted)
    if len(existing_first_names) >= args.num_first:
        first_names = sort_first_names(existing_first_names[:args.num_first])
    else:
        first_names_new = generate_names('first', args.city, args.year, args.num_first, args.seed, rng, max_tokens=args.max_tokens, timeout=args.timeout, batch_size=args.batch_size, excluded_names=excluded_first)
        def merge_gendered(existing, new):
            seen = set(fn['name'] for fn in existing if 'name' in fn)
            result = existing[:]
            for fn in new:
                if isinstance(fn, dict) and 'name' in fn and fn['name'] not in seen:
                    result.append(fn)
                    seen.add(fn['name'])
            return result
        first_names = sort_first_names(merge_gendered(existing_first_names, first_names_new))

    # If enough last names, use only those (sorted)
    if len(existing_last_names) >= args.num_last:
        last_names = sort_last_names(existing_last_names[:args.num_last])
    else:
        last_names_new = generate_names('last', args.city, args.year, args.num_last, args.seed, rng, max_tokens=args.max_tokens, timeout=args.timeout, batch_size=args.batch_size, excluded_names=excluded_last)
        def merge_last(existing, new):
            seen = set(existing)
            result = existing[:]
            for ln in new:
                if ln not in seen:
                    result.append(ln)
                    seen.add(ln)
            return result
        last_names = sort_last_names(merge_last(existing_last_names, last_names_new))

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
