from scripts.place_controller import load_place_yaml, infer_staff_from_place, build_place_world, generate_staff_personas
p = load_place_yaml('train_station_3')
roles = infer_staff_from_place(p)
world = build_place_world('train_station_3', p)
personas = generate_staff_personas('train_station_3', roles, city_name=p.get('location',{}).get('city','Redwood'))
print('loaded_city=', p.get('location',{}).get('city'))
print('roles=', roles)
print('world_places=', list(world.places.keys()))
print('personas_count=', len(personas))
for x in personas[:3]:
    print(x)
