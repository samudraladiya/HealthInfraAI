import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# HEALTHINFRAAI - MACHINE LEARNING
# ============================================================

print("=" * 60)
print("HEALTHINFRAAI - MACHINE LEARNING")
print("=" * 60)


# ============================================================
# 1. LOAD MASTER DATA
# ============================================================

master = pd.read_csv("data/master_final.csv")

print("\nDataset Shape:")
print(master.shape)

print("\nNumber of Districts:")
print(master["District"].nunique())


# ============================================================
# 2. RANDOM FOREST - BED CAPACITY PREDICTION
# ============================================================

print("\n" + "=" * 60)
print("RANDOM FOREST - HOSPITAL BED CAPACITY PREDICTION")
print("=" * 60)


# Features used to predict hospital beds
features = [
    "Population",
    "Total_Facilities",
    "Doctors in all Hospitals",
    "Health Sub-Centres",
    "Primary Health Centres",
    "Community Health Centres",
    "Area Hospitals",
    "District Hospitals",
    "Teaching Hospitals",
    "Ayurveda Hospitals (incl. Dispensaries)",
    "Homeopathic Hospitals (incl. Dispensaries)",
    "Unani Hospitals (incl. Dispensaries)",
    "Naturopathy Hospitals (incl. Dispensaries)"
]

target = "Beds in all Hospitals"


# Remove rows with missing values
ml_data = master[features + [target]].dropna()

X = ml_data[features]
y = ml_data[target]


print("\nFeatures used:")
for feature in features:
    print("-", feature)

print("\nTarget:")
print("-", target)


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 4. RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)


# ============================================================
# 5. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 6. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)


print("\nModel Performance:")
print("-----------------------------")
print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("R²  :", round(r2, 4))


# ============================================================
# 7. ACTUAL VS PREDICTED
# ============================================================

results = pd.DataFrame({
    "Actual_Beds": y_test.values,
    "Predicted_Beds": y_pred
})

print("\nActual vs Predicted:")
print(results)


# ============================================================
# 8. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance)


# ============================================================
# 9. FEATURE IMPORTANCE GRAPH
# ============================================================

plt.figure(figsize=(10, 7))

plt.barh(
    importance["Feature"],
    importance["Importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Random Forest Feature Importance")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()


# ============================================================
# 10. ACTUAL VS PREDICTED GRAPH
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    y_pred
)

plt.xlabel("Actual Hospital Beds")
plt.ylabel("Predicted Hospital Beds")
plt.title("Actual vs Predicted Hospital Bed Capacity")

plt.tight_layout()
plt.show()


# ============================================================
# 11. K-MEANS CLUSTERING
# ============================================================

print("\n" + "=" * 60)
print("K-MEANS - DISTRICT INFRASTRUCTURE CLUSTERING")
print("=" * 60)


# Create infrastructure indicators
cluster_data = master[
    [
        "District",
        "Beds_per_1000",
        "Doctors_per_100000",
        "Facilities_per_100000",
        "Rural_Facility_Percent"
    ]
].dropna().copy()


# Features for clustering
cluster_features = [
    "Beds_per_1000",
    "Doctors_per_100000",
    "Facilities_per_100000",
    "Rural_Facility_Percent"
]

X_cluster = cluster_data[cluster_features]


# ============================================================
# 12. STANDARDIZE DATA
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X_cluster)


# ============================================================
# 13. ELBOW METHOD
# ============================================================

inertia = []

for k in range(2, 7):

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    kmeans.fit(X_scaled)

    inertia.append(kmeans.inertia_)


plt.figure(figsize=(8, 5))

plt.plot(
    range(2, 7),
    inertia,
    marker="o"
)

plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("K-Means Elbow Method")

plt.tight_layout()
plt.show()


# ============================================================
# 14. CREATE 3 DISTRICT CLUSTERS
# ============================================================

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

cluster_data["Cluster"] = kmeans.fit_predict(X_scaled)


# ============================================================
# 15. DISPLAY CLUSTERS
# ============================================================

print("\nDistrict Clusters:")

print(
    cluster_data[
        [
            "District",
            "Beds_per_1000",
            "Doctors_per_100000",
            "Facilities_per_100000",
            "Rural_Facility_Percent",
            "Cluster"
        ]
    ].sort_values("Cluster")
)


# ============================================================
# 16. CLUSTER PROFILES
# ============================================================

cluster_profile = cluster_data.groupby("Cluster")[
    cluster_features
].mean()

print("\nCluster Profiles:")
print(cluster_profile)


# ============================================================
# 17. SAVE CLUSTER RESULTS
# ============================================================

cluster_data.to_csv(
    "data/district_clusters.csv",
    index=False
)

print("\nSaved:")
print("data/district_clusters.csv")


# ============================================================
# 18. ADD CLUSTER TO MASTER DATA
# ============================================================

master_with_clusters = master.merge(
    cluster_data[["District", "Cluster"]],
    on="District",
    how="left"
)

master_with_clusters.to_csv(
    "data/master_ml.csv",
    index=False
)

print("data/master_ml.csv")


# ============================================================
# 19. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("MACHINE LEARNING COMPLETE")
print("=" * 60)