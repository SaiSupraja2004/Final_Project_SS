import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

# ✅ Load dataset
data = pd.read_csv("dataset.csv")

# ✅ Features and target
X = data.drop(columns=["diseases"])   # all symptom columns
y = data["diseases"]                  # target disease column

# ✅ Handle missing values (if any)
X = X.fillna(0)

# ✅ Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ✅ Train Decision Tree model
model = DecisionTreeClassifier(criterion="entropy", max_depth=10)
model.fit(X_train, y_train)

# ✅ Create model folder if not exists
os.makedirs("model", exist_ok=True)

# ✅ Save model and symptom list
joblib.dump(model, "model/disease_prediction_model.pkl")
joblib.dump(list(X.columns), "model/symptom_list.pkl")

print("✅ Model trained successfully and saved in 'model/' folder.")
