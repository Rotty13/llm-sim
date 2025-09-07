def GetCityDefaultPlaces(start_year):
    if start_year < 1850:
        places = [
            {"name": "Town Hall", "role": "Town Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square", "role": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church", "role": "Church", "category": "religious", "prob": 1.0},
            {"name": "Blacksmith Shop", "role": "Blacksmith Shop", "category": "business", "prob": 0.6},
            {"name": "Schoolhouse", "role": "Schoolhouse", "category": "education", "prob": 0.5},
            {"name": "General Store", "role": "General Store", "category": "business", "prob": 0.7},
            {"name": "Bakery", "role": "Bakery", "category": "business", "prob": 0.4},
            {"name": "Tavern", "role": "Tavern", "category": "business", "prob": 0.6},
            {"name": "Stables", "role": "Stables", "category": "business", "prob": 0.5},
            {"name": "Apothecary", "role": "Apothecary", "category": "business", "prob": 0.3}
        ]
    elif start_year < 1920:
        places = [
            {"name": "City Hall", "role": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square", "role": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church", "role": "Church", "category": "religious", "prob": 1.0},
            {"name": "Central Park", "role": "Central Park", "category": "public_space", "prob": 0.7},
            {"name": "Library", "role": "Library", "category": "education", "prob": 0.6},
            {"name": "General Hospital", "role": "General Hospital", "category": "healthcare", "prob": 0.5},
            {"name": "Elementary School", "role": "Elementary School", "category": "education", "prob": 0.8},
            {"name": "Police Station", "role": "Police Station", "category": "government", "prob": 0.7},
            {"name": "Community Center", "role": "Community Center", "category": "public_space", "prob": 0.4},
            {"name": "Main Bakery", "role": "Main Bakery", "category": "business", "prob": 0.5},
            {"name": "Restaurant", "role": "Restaurant", "category": "business", "prob": 0.6},
            {"name": "Public Bath", "role": "Public Bath", "category": "public_space", "prob": 0.3}
        ]
    else:
        places = [
            {"name": "City Hall", "role": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Central Park", "role": "Central Park", "category": "public_space", "prob": 0.8},
            {"name": "Library", "role": "Library", "category": "education", "prob": 0.85},
            {"name": "General Hospital", "role": "General Hospital", "category": "healthcare", "prob": 0.8},
            {"name": "Elementary School", "role": "Elementary School", "category": "education", "prob": 0.9},
            {"name": "Police Station", "role": "Police Station", "category": "government", "prob": 0.85},
            {"name": "Community Center", "role": "Community Center", "category": "public_space", "prob": 0.6},
            {"name": "Main Bakery", "role": "Main Bakery", "category": "business", "prob": 0.6},
            {"name": "Popular Restaurant", "role": "Popular Restaurant", "category": "business", "prob": 0.8},
            {"name": "Public Pool", "role": "Public Pool", "category": "public_space", "prob": 0.5}
        ]
    return places

def generate_default_places(cityname, start_year):
    places = GetCityDefaultPlaces(start_year)
    import random
    result = {"places": []}
    total_places = len(places)
    added_places = 0
    for idx, place in enumerate(places):
        print(f"[place_gen] Considering place {idx+1}/{total_places}: {place['name']} (prob={place['prob']})")
        if random.random() <= place["prob"]:
            result["places"].append({
                "name": f"{cityname} {place['name']}",
                "category": place["category"],
                "role": place["role"],
                "description": f"A notable location in {cityname}."
            })
            added_places += 1
            percent = int(added_places/total_places*100) if total_places else 100
            print(f"[place_gen] Added place {added_places}/{total_places}: {place['name']} | Progress: {percent}% of places")
    print(f"[place_gen] Finished place generation. Total added: {added_places}/{total_places}")
    return result
