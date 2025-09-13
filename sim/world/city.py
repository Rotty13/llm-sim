def GetCityDefaultPlaces(start_year):
    if start_year < 1850:
        places = [
            {"name": "Town Hall", "purpose": "Town Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square", "purpose": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church", "purpose": "Church", "category": "religious", "prob": 1.0},
            {"name": "Blacksmith Shop", "purpose": "Blacksmith Shop", "category": "business", "prob": 0.6},
            {"name": "Schoolhouse", "purpose": "Schoolhouse", "category": "education", "prob": 0.5},
            {"name": "General Store", "purpose": "General Store", "category": "business", "prob": 0.7},
            {"name": "Apothecary", "purpose": "Apothecary", "category": "business", "prob": 0.3}
        ]
    elif start_year < 1920:
        places = [
            {"name": "City Hall", "purpose": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square", "purpose": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church", "purpose": "Church", "category": "religious", "prob": 1.0},
            {"name": "Central Park", "purpose": "Central Park", "category": "public_space", "prob": 0.7},
            {"name": "Library", "purpose": "Library", "category": "education", "prob": 0.6},
            {"name": "General Hospital", "purpose": "General Hospital", "category": "healthcare", "prob": 0.5},
            {"name": "Elementary School", "purpose": "Elementary School", "category": "education", "prob": 0.8},
            {"name": "Police Station", "purpose": "Police Station", "category": "government", "prob": 0.7},
            {"name": "Community Center", "purpose": "Community Center", "category": "public_space", "prob": 0.4},
            {"name": "Public Bath", "purpose": "Public Bath", "category": "public_space", "prob": 0.3}
        ]
    else:
        places = [
            {"name": "City Hall", "purpose": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Central Park", "purpose": "Central Park", "category": "public_space", "prob": 0.8},
            {"name": "Library", "purpose": "Library", "category": "education", "prob": 0.85},
            {"name": "General Hospital", "purpose": "General Hospital", "category": "healthcare", "prob": 0.8},
            {"name": "Elementary School", "purpose": "Elementary School", "category": "education", "prob": 0.9},
            {"name": "Police Station", "purpose": "Police Station", "category": "government", "prob": 0.85},
            {"name": "Community Center", "purpose": "Community Center", "category": "public_space", "prob": 0.6},
            {"name": "Public Pool", "purpose": "Public Pool", "category": "public_space", "prob": 0.5}
        ]
    return places

def generate_default_places(cityname, start_year):
    places = GetCityDefaultPlaces(start_year)
    import random
    result = {"places": []}
    total_places = len(places)
    added_places = 0
    for idx, place in enumerate(places):
        place["name"]=f"{cityname} {place['name']}"
        #print(f"[place_gen] Considering place {idx+1}/{total_places}: {place['name']} (prob={place['prob']})")
        if random.random() <= place["prob"]:
            result["places"].append({
                "name": place['name'],
                "category": place["category"],
                "purpose": place["purpose"],
                "description": f"A notable location in {cityname}."
            })
            added_places += 1
            percent = int(added_places/total_places*100) if total_places else 100
            print(f"[place_gen] Added place {added_places}: {place['name']}")
    print(f"[place_gen] Finished default place generation. Total added: {added_places}/{total_places} | {percent}% of possible places")
    return result
