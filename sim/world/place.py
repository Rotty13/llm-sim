import random


categories = [
    "government",
    "public_space",
    "religious",
    "business",
    "education",
    "healthcare"
]

placeRole_employees = {
    # Pre-1850 and later overlaps
    "Town Hall": ["Mayor", "Council Members", "Town Clerk"],
    "City Hall": ["Mayor", "Council Members", "City Clerk"],
    "Market Square": ["Market Master", "Vendors", "Street Performers"],
    "Church": ["Priest/Pastor", "Deacons/Ministers", "Choir Members"],
    "Blacksmith Shop": ["Blacksmith", "Apprentice"],
    "Schoolhouse": ["Teacher", "Students"],
    "General Store": ["Store Owner", "Clerk/Cashier"],
    "Bakery": ["Baker", "Assistant Baker"],
    "Main Bakery": ["Baker", "Assistant Baker"],
    "Tavern": ["Barkeep", "Waitstaff"],
    "Stables": ["Stablemaster", "Farrier", "Groom"],
    "Apothecary": ["Pharmacist", "Apprentice"],

    # 1850–1920 and later
    "Central Park": ["Park Manager", "Groundskeeper", "Park Ranger"],
    "Library": ["Head Librarian", "Assistant Librarian"],
    "General Hospital": ["Hospital Administrator", "Physician", "Nurse"],
    "Elementary School": ["Principal", "Teacher", "Students"],
    "Police Station": ["Police Chief", "Detective", "Patrol Officer", "Dispatcher"],
    "Community Center": ["Center Director", "Program Coordinator", "Volunteers"],
    "Restaurant": ["Chef", "Server", "Manager"],
    "Popular Restaurant": ["Chef", "Server", "Manager"],
    "Public Bath": ["Bath Attendant", "Cashier", "Maintenance Worker"],
    "Public Pool": ["Pool Manager", "Lifeguard", "Swim Instructor"]
}


def GetRolesForPlace(place_role, year=1900):
    """
    Retrieves roles for a given place.
    
    Args:
        place_name (str): The name of the place.
    
    Returns:
        list: A list of role and their description for the given place.
    """
    
    # Check if the place name exists in the dictionary
    #print(f"[DEBUG] GetRolesForPlace called with place_role='{place_role}', year={year}")
    if place_role in placeRole_employees:
        roles = placeRole_employees[place_role]
        print(f"[role_gen] Static roles for '{place_role}': {roles}")
        total_roles = len(roles)
        for idx, role in enumerate(roles):
            percent = int((idx+1)/total_roles*100) if total_roles else 100
            print(f"[role_gen] Generated role {idx+1}/{total_roles}: {role} | Progress: {percent}% of roles for {place_role}")
        return roles
    #else:
        from sim.llm.llm import llm
        prompt = f"You are an expert in historical occupations. Your task is to provide a list of realistic job roles for a place called '{place_role}' in the year {year}. The roles should be appropriate for the time period and location. Names should be words only. exclude slang. Return ONLY a JSON array of job titles. {{ 'roles': [{{'role1':[{{'description':'description of role duties'}},{{'role2':[{{'description':'description of role duties'}}]}}]}}]}}"
        llm_seed =  random.randint(-5000,5000)
        #print(f"[DEBUG] Prompt for LLM: {prompt}")
        #print(f"[DEBUG] Initial LLM seed: {llm_seed}")
        num_attempts = 5
        role_counts = {}
        role_descriptions = {}
        valid_responses = []
        for attempt in range(num_attempts):
            llm_seed = random.randint(-5000, 5000)
            print(f"[role_gen] LLM attempt {attempt+1}/{num_attempts} for '{place_role}'")
            roles = llm.chat_json(prompt, system="Return strict JSON only.", seed=llm_seed)
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
                            print(f"[role_gen] Generated role {idx+1}/{total_roles}: {k} | Progress: {percent}% of roles for {place_role} (LLM attempt {attempt+1})")
        if role_counts:
            # Sort roles by frequency (descending) and keep top 5
            sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
            top_roles = [role for role, count in sorted_roles if role in role_descriptions][:5]
            result = [(role, role_descriptions[role]) for role in top_roles]
            return result
        #print(f"[DEBUG] Failed to get any valid roles after {num_attempts} attempts. Returning None.")
    return None