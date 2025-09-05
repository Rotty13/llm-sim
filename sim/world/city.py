def GetCityDefaultPlaces(start_year):
    if start_year < 1850:
        places = [
            {"name": "Town Hall {cityname}", "role": "Town Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square {cityname}", "role": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church {cityname}", "role": "Church", "category": "religious", "prob": 1.0},
            {"name": "Blacksmith Shop {cityname}", "role": "Blacksmith Shop", "category": "business", "prob": 0.6},
            {"name": "Schoolhouse {cityname}", "role": "Schoolhouse", "category": "education", "prob": 0.5},
            {"name": "General Store {cityname}", "role": "General Store", "category": "business", "prob": 0.7},
            {"name": "Bakery {cityname}", "role": "Bakery", "category": "business", "prob": 0.4},
            {"name": "Tavern {cityname}", "role": "Tavern", "category": "business", "prob": 0.6},
            {"name": "Stables {cityname}", "role": "Stables", "category": "business", "prob": 0.5},
            {"name": "Apothecary {cityname}", "role": "Apothecary", "category": "business", "prob": 0.3}
        ]
    elif start_year < 1920:
        places = [
            {"name": "City Hall {cityname}", "role": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Market Square {cityname}", "role": "Market Square", "category": "public_space", "prob": 1.0},
            {"name": "Church {cityname}", "role": "Church", "category": "religious", "prob": 1.0},
            {"name": "Central Park {cityname}", "role": "Central Park", "category": "public_space", "prob": 0.7},
            {"name": "Library {cityname}", "role": "Library", "category": "education", "prob": 0.6},
            {"name": "General Hospital {cityname}", "role": "General Hospital", "category": "healthcare", "prob": 0.5},
            {"name": "Elementary School {cityname}", "role": "Elementary School", "category": "education", "prob": 0.8},
            {"name": "Police Station {cityname}", "role": "Police Station", "category": "government", "prob": 0.7},
            {"name": "Community Center {cityname}", "role": "Community Center", "category": "public_space", "prob": 0.4},
            {"name": "Main Bakery {cityname}", "role": "Main Bakery", "category": "business", "prob": 0.5},
            {"name": "Restaurant {cityname}", "role": "Restaurant", "category": "business", "prob": 0.6},
            {"name": "Public Bath {cityname}", "role": "Public Bath", "category": "public_space", "prob": 0.3}
        ]
    else:
        places = [
            {"name": "City Hall {cityname}", "role": "City Hall", "category": "government", "prob": 1.0},
            {"name": "Central Park {cityname}", "role": "Central Park", "category": "public_space", "prob": 0.8},
            {"name": "Library {cityname}", "role": "Library", "category": "education", "prob": 0.85},
            {"name": "General Hospital {cityname}", "role": "General Hospital", "category": "healthcare", "prob": 0.8},
            {"name": "Elementary School {cityname}", "role": "Elementary School", "category": "education", "prob": 0.9},
            {"name": "Police Station {cityname}", "role": "Police Station", "category": "government", "prob": 0.85},
            {"name": "Community Center {cityname}", "role": "Community Center", "category": "public_space", "prob": 0.6},
            {"name": "Main Bakery {cityname}", "role": "Main Bakery", "category": "business", "prob": 0.6},
            {"name": "Popular Restaurant {cityname}", "role": "Popular Restaurant", "category": "business", "prob": 0.8},
            {"name": "Public Pool {cityname}", "role": "Public Pool", "category": "public_space", "prob": 0.5}
        ]
    return places

def generate_default_places(cityname, start_year):
    places = GetCityDefaultPlaces(start_year)
    import random
    result = {"places": []}
    for place in places:
        if random.random() <= place["prob"]:
            result["places"].append({
                "name": f"{cityname} {place['name']}",
                "category": place["category"],
                "role": place["role"],
                "description": f"A notable location in {cityname}."
            })
    return result
