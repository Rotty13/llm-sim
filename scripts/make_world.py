

import argparse
from scripts.make_personas import make_personas
from scripts.make_city import make_city

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', default='Redwood')
    parser.add_argument('--personas', default='configs/personas.yaml')
    parser.add_argument('--city_out', default='configs/city.yaml')
    parser.add_argument('--num_personas', type=int, default=20)
    args = parser.parse_args()

    # Step 1: Generate personas
    print("[make_world] Generating personas...")
    make_personas(city=args.city, n=args.num_personas, out=args.personas)

    # Step 2: Generate city using personas
    print("[make_world] Generating city...")
    make_city(personas_path=args.personas, city=args.city, out=args.city_out)

    print("[make_world] World generation complete.")

if __name__ == "__main__":
    main()
