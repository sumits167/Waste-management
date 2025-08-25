import pandas as pd

from sklearn.preprocessing import LabelEncoder

from sklearn.tree import DecisionTreeClassifier

df=pd.read_csv("waste_data.csv")



amount_encoder=LabelEncoder()

df["Amount Earned_encoded"]=amount_encoder.fit_transform(df["Amount Earned (₹)"])

waste_encoder=LabelEncoder()

df["waste_encoded"]=waste_encoder.fit_transform(df["Waste Type"])

# weight_encoder=LabelEncoder()

# df["weight_encoded"]=weight_encoder.fit_transform(df["Weight (kg)"])



x=df[["waste_encoded","Weight (kg)"]]
y=df["Amount Earned_encoded"]

model=DecisionTreeClassifier()

model.fit(x,y)


def mod(Waste_Type,Weight):
        global model
        print("Df=",df.to_dict())
        
        if Waste_Type not in df["Waste Type"].values:
                return "Unknown Plastic Type"
        print("Waste_Type=",Waste_Type)
        print("Weight=",Weight)
        

        waste_encoded=waste_encoder.transform([Waste_Type])[0]

        

        # weight_encoded=weight_encoder.fit_transform([Weight])[0]

        print("waste_encoded=",waste_encoded)
        # print("weight_encoded=",weight_encoded)

        prediction=model.predict([[waste_encoded,Weight]])
        print("Prediction=",prediction)
        label=dict(zip(df["Amount Earned_encoded"],df["Amount Earned (₹)"]))
        print("label=",label)
        print("Response=",label[prediction[0]])
        return label[prediction[0]]

