import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("detector/events.csv")

# Convert categorical data to numeric
df_encoded = pd.get_dummies(df[["owner", "ip"]])
clf = IsolationForest(contamination=0.1, random_state=42)
df["score"] = clf.fit_predict(df_encoded)
df["anomaly"] = clf.decision_function(df_encoded)
print(df)
