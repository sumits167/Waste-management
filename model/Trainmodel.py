import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor

df = pd.read_csv("waste_data.csv")

# fixed price mapping (same as dataset generation)
price_mapping = {
    "Plastic": 10,
    "Metal": 50,
    "Paper": 10,
    "Glass": 10,
    "Electronics": 250,
    "Organic": 2,
    "Textile": 10,
    "Wood": 10,
    "Battery": 200,
    "Rubber": 15
}

# keep waste_encoder (to match your existing code)
waste_encoder = LabelEncoder()
df["waste_encoded"] = waste_encoder.fit_transform(df["Waste Type"])

# dummy regression training (not really needed now)
x = df[["waste_encoded", "Weight (kg)"]]
y = df["Amount Earned (₹)"]
model = DecisionTreeRegressor()
model.fit(x, y)

def mod(Waste_Type, Weight):
    global model

    if Waste_Type not in price_mapping:
        return "Unknown Waste Type"

    # exact formula (faster + accurate)
    amount = Weight * price_mapping[Waste_Type]

    return round(amount, 2)
