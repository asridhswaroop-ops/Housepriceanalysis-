"""
Generate a realistic housing dataset for house price prediction and analysis.
"""
import numpy as np
import pandas as pd

def generate_housing_dataset(n_samples=1500, random_seed=42):
    np.random.seed(random_seed)

    locations = {
        "Downtown Core": {"base_price_sqft": 8500, "weight": 0.15},
        "Green Valley Suburbs": {"base_price_sqft": 4800, "weight": 0.18},
        "Tech Park Enclave": {"base_price_sqft": 7200, "weight": 0.20},
        "Lakeside Boulevard": {"base_price_sqft": 6500, "weight": 0.14},
        "Midtown Heights": {"base_price_sqft": 5800, "weight": 0.15},
        "Metro Outskirts": {"base_price_sqft": 3600, "weight": 0.18}
    }

    loc_names = list(locations.keys())
    loc_weights = [locations[k]["weight"] for k in loc_names]

    chosen_locations = np.random.choice(loc_names, size=n_samples, p=loc_weights)
    
    # Area between 600 and 4200 sqft
    areas = np.random.normal(loc=1650, scale=650, size=n_samples)
    areas = np.clip(areas, 550, 4500).astype(int)

    # Bedrooms correlated with Area
    bedrooms = []
    for a in areas:
        if a < 900:
            b = np.random.choice([1, 2], p=[0.75, 0.25])
        elif a < 1400:
            b = np.random.choice([2, 3], p=[0.60, 0.40])
        elif a < 2200:
            b = np.random.choice([2, 3, 4], p=[0.15, 0.65, 0.20])
        elif a < 3000:
            b = np.random.choice([3, 4, 5], p=[0.20, 0.65, 0.15])
        else:
            b = np.random.choice([4, 5], p=[0.45, 0.55])
        bedrooms.append(b)
    bedrooms = np.array(bedrooms)

    # Bathrooms correlated with Bedrooms
    bathrooms = []
    for b in bedrooms:
        if b == 1:
            ba = 1
        elif b == 2:
            ba = np.random.choice([1, 2], p=[0.3, 0.7])
        elif b == 3:
            ba = np.random.choice([2, 3], p=[0.45, 0.55])
        elif b == 4:
            ba = np.random.choice([3, 4], p=[0.4, 0.6])
        else:
            ba = np.random.choice([4, 5], p=[0.5, 0.5])
        bathrooms.append(ba)
    bathrooms = np.array(bathrooms)

    # Year Built (1995 to 2024)
    year_built = np.random.randint(1995, 2025, size=n_samples)

    # Parking: Yes / No
    parking_opts = ["Yes", "No"]
    parking = np.random.choice(parking_opts, size=n_samples, p=[0.78, 0.22])

    # Furnishing: Furnished, Semi-Furnished, Unfurnished
    furnish_opts = ["Furnished", "Semi-Furnished", "Unfurnished"]
    furnishing = np.random.choice(furnish_opts, size=n_samples, p=[0.32, 0.46, 0.22])

    # Price Calculation with realistic economic dynamics
    prices = []
    current_year = 2026
    for i in range(n_samples):
        loc = chosen_locations[i]
        area = areas[i]
        beds = bedrooms[i]
        baths = bathrooms[i]
        yr = year_built[i]
        park = parking[i]
        furn = furnishing[i]

        base_rate = locations[loc]["base_price_sqft"]
        
        # Base price
        price = area * base_rate

        # Bedroom premium (larger layout efficiency)
        price += (beds - 2) * 120000

        # Bathroom premium
        price += (baths - 1) * 90000

        # Age depreciation / appreciation factor
        age = current_year - yr
        if age < 5:
            price *= 1.10  # Brand new premium
        elif age < 15:
            price *= 1.02
        else:
            price *= (1.0 - (age - 15) * 0.007)

        # Parking premium
        if park == "Yes":
            price += 250000

        # Furnishing premium
        if furn == "Furnished":
            price += 400000
        elif furn == "Semi-Furnished":
            price += 180000

        # Market variance noise (+/- 7%)
        noise = np.random.normal(0, 0.05)
        price = price * (1 + noise)

        # Round to nearest 10,000
        price = int(round(price / 10000.0) * 10000)
        prices.append(price)

    df = pd.DataFrame({
        "House ID": [f"HSE-{1001 + i}" for i in range(n_samples)],
        "Area": areas,
        "Bedrooms": bedrooms,
        "Bathrooms": bathrooms,
        "Location": chosen_locations,
        "Year Built": year_built,
        "Parking": parking,
        "Furnishing": furnishing,
        "Price": prices
    })

    return df

if __name__ == "__main__":
    df = generate_housing_dataset(n_samples=1500)
    output_path = "data/house_prices.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records into {output_path}")
    print(df.head())
    print("\nSummary Statistics:")
    print(df.describe())
