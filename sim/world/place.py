import random


categories = [
    "government",
    "public_space",
    "religious",
    "business",
    "education",
    "healthcare"
]


def GetRolesForPlace(place_role, year=1900):
    """
    Retrieves roles for a given place.
    
    Args:
        place_name (str): The name of the place.
    
    Returns:
        list: A list of role and their description for the given place.
    """
    
    # Check if the place name exists in the dictionary
    
    from sim.llm.llm_ollama import llm
    system_prompt = "You are an expert in historical occupations. Your task is to provide a list of realistic job roles for a given place in a specific year. The roles should be appropriate for the time period and location. Names should be words only. exclude slang. Return ONLY a JSON array of job titles."
    prompt = (f"Provide a list of realistic job roles for '{place_role}' in the year {year}. List most common roles first. "
                    "example: { 'roles': [{'role1':[{'description':'description of role duties'},{'role2':[{'description':'description of role duties'}]}]}]}")
    llm_seed =  random.randint(-5000,5000)
    #print(f"[DEBUG] Prompt for LLM: {prompt}")
    #print(f"[DEBUG] Initial LLM seed: {llm_seed}")
    num_attempts = 5
    role_counts = {}
    role_descriptions = {}
    valid_responses = []
    for attempt in range(num_attempts):
        llm_seed = random.randint(-5000, 5000)
        #print(f"[role_gen] LLM attempt {attempt+1}/{num_attempts} for '{place_role}'")
        roles = llm.chat_json(prompt, system=system_prompt, seed=llm_seed, max_tokens=512, timeout=50)
        roles = roles.get("roles", []) if roles else []
        if roles and isinstance(roles, list):
            valid_responses.append(roles)
            total_roles = len(roles)
            for idx, role in enumerate(roles):
                if isinstance(role, dict):
                    for k, v in role.items():
                        normalized = k.strip().lower()
                        role_counts[normalized] = role_counts.get(normalized, 0) + 1
                        desc = ""
                        if isinstance(v, list):
                            for item in v:
                                if isinstance(item, dict) and "description" in item:
                                    desc = item["description"]
                                    break
                        if desc != "":
                            role_descriptions[normalized] = desc
                        percent = int((idx+1)/total_roles*100) if total_roles else 100
                        #print(f"[role_gen] Generated role {idx+1}/{total_roles}: {k} | Progress: {percent}% of roles for {place_role} (LLM attempt {attempt+1})")
    if role_counts:
        # Sort roles by frequency (descending) and keep top 5
        sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
        top_roles = [role for role, count in sorted_roles if role in role_descriptions][:5]
        result = [(role, role_descriptions[role]) for role in top_roles]
        #print(f"[role_gen] Selected top {len(result)} roles for place '{place_role}': {[r[0] for r in result]}")
        return result
    print(f"[role_gen] Failed to get any valid roles after {num_attempts} attempts. Returning None.")
    return None