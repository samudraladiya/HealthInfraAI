import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ============================================================
# HEALTHINFRAAI - FIGURES AND STATISTICS FOR THE REPORT
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
BLUE, LIGHT = "#245F84", "#9CC6D8"

master = pd.read_csv(os.path.join(DATA_DIR, "master.csv"))
ml = pd.read_csv(os.path.join(DATA_DIR, "master_ml.csv"))
geo = pd.read_csv(os.path.join(DATA_DIR, "geolocation.csv"))
raw_geo = pd.read_csv(
    os.path.join(BASE_DIR, "data_old", "geolocation.csv"),
    encoding="utf-8-sig"
)

stats = {}


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, f"{name}.png"), dpi=200, bbox_inches="tight")
    plt.close()


# ------------------------------------------------------------
# Data quality facts (raw register)
# ------------------------------------------------------------

stats["raw_rows"], stats["raw_cols"] = raw_geo.shape
stats["raw_missing"] = raw_geo.isna().sum().to_dict()
stats["raw_duplicates"] = int(raw_geo.duplicated().sum())
stats["raw_types"] = int(raw_geo["Facility Type"].nunique())
stats["clean_types"] = int(geo["Facility Type"].nunique())
stats["raw_districts"] = int(raw_geo["District"].nunique())
stats["ownership_labels"] = raw_geo["Ownership Authority"].value_counts().to_dict()

# ------------------------------------------------------------
# Snapshot statistics
# ------------------------------------------------------------

pop = master["Population"].sum()
stats["population"] = int(pop)
stats["facilities"] = int(master["Total_Facilities"].sum())
stats["beds"] = int(master["Beds in all Hospitals"].sum())
stats["doctors"] = int(master["Doctors in all Hospitals"].sum())
stats["beds_per_1000_state"] = stats["beds"] / pop * 1000
stats["doctors_per_100k_state"] = stats["doctors"] / pop * 100000
stats["fac_desc"] = master["Total_Facilities"].describe().round(2).to_dict()
stats["type_counts"] = geo["Facility Type"].value_counts().to_dict()

for col in ["Beds_per_1000", "Doctors_per_100000", "Facilities_per_100000"]:
    s = master.set_index("District")[col].sort_values(ascending=False)
    stats[col] = {
        "top": s.head(5).round(2).to_dict(),
        "bottom": s.tail(5).round(2).to_dict(),
        "mean": round(s.mean(), 2),
        "median": round(s.median(), 2),
    }

# ------------------------------------------------------------
# Figure 1: facilities by district
# ------------------------------------------------------------

d = master.sort_values("Total_Facilities")
plt.figure(figsize=(9, 9))
plt.barh(d["District"], d["Total_Facilities"], color=BLUE)
for y, v in enumerate(d["Total_Facilities"]):
    plt.text(v + 3, y, str(v), va="center", fontsize=8)
plt.xlabel("Number of public healthcare facilities")
plt.title("Public healthcare facilities by district")
save("fig01_facilities")

# ------------------------------------------------------------
# Figure 2: facility type composition
# ------------------------------------------------------------

t = geo["Facility Type"].value_counts().sort_values()
plt.figure(figsize=(9, 6.5))
plt.barh(t.index, t.values, color=BLUE)
for y, v in enumerate(t.values):
    plt.text(v + 30, y, f"{v:,}", va="center", fontsize=8)
plt.xscale("log")
plt.xlabel("Number of facilities (log scale)")
plt.title("Facility register by facility type")
save("fig02_types")

# ------------------------------------------------------------
# Figure 3: beds per 1,000 and doctors per 100,000
# ------------------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(12, 9), sharey=False)
for ax, col, color, label in [
    (axes[0], "Beds_per_1000", BLUE, "Beds per 1,000 people"),
    (axes[1], "Doctors_per_100000", "#3C7FA2", "Doctors per 100,000 people"),
]:
    s = master.sort_values(col)
    ax.barh(s["District"], s[col], color=color)
    ax.axvline(s[col].median(), color="#C0392B", ls="--", lw=1, label="Median")
    ax.set_xlabel(label)
    ax.legend(loc="lower right")
axes[0].set_title("Hospital beds per 1,000 population")
axes[1].set_title("Doctors per 100,000 population")
save("fig03_per_capita")

# ------------------------------------------------------------
# Figure 4: population vs beds
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))
plt.scatter(master["Population"] / 1e6, master["Beds in all Hospitals"],
            s=master["Urban Population (%)"] * 6 + 20, color=BLUE, alpha=0.7)
for _, r in master.iterrows():
    if r["Population"] > 1.5e6 or r["Beds_per_1000"] > 2.3:
        plt.annotate(r["District"], (r["Population"] / 1e6, r["Beds in all Hospitals"]),
                     fontsize=8, xytext=(4, 4), textcoords="offset points")
corr = master["Population"].corr(master["Beds in all Hospitals"])
stats["pop_beds_corr"] = round(corr, 2)
plt.xlabel("Population (millions)")
plt.ylabel("Hospital beds")
plt.title(f"Population vs hospital beds (bubble size = urban %, r = {corr:.2f})")
save("fig04_pop_beds")

# ------------------------------------------------------------
# Figure 5: rural vs urban share
# ------------------------------------------------------------

rows = [
    ("Population", master["Rural"].sum(), master["Urban"].sum()),
    ("Facilities", master["Rural_Facilities"].sum(), master["Urban_Facilities"].sum()),
    ("Hospital beds (est.)", master["Rural_Beds"].sum(), master["Urban_Beds"].sum()),
    ("Doctors (est.)", master["Rural_Doctors"].sum(), master["Urban_Doctors"].sum()),
]
share = pd.DataFrame(rows, columns=["Measure", "Rural", "Urban"]).set_index("Measure")
share = share.div(share.sum(axis=1), axis=0) * 100
stats["rural_urban_share"] = share.round(1).to_dict("index")
rp, up = master["Rural"].sum(), master["Urban"].sum()
stats["rural_beds_per_1000"] = master["Rural_Beds"].sum() / rp * 1000
stats["urban_beds_per_1000"] = master["Urban_Beds"].sum() / up * 1000
stats["rural_docs_per_100k"] = master["Rural_Doctors"].sum() / rp * 1e5
stats["urban_docs_per_100k"] = master["Urban_Doctors"].sum() / up * 1e5

ax = share[::-1].plot(kind="barh", stacked=True, color=[BLUE, LIGHT], figsize=(9, 4))
for c in ax.containers:
    ax.bar_label(c, fmt="%.0f%%", label_type="center", color="black", fontsize=9)
plt.xlabel("Share (%)")
plt.ylabel("")
plt.title("Rural vs urban share of population and healthcare capacity")
plt.legend(loc="lower right")
save("fig05_rural_urban")

# ------------------------------------------------------------
# Figure 6: Lorenz curve of beds vs population
# ------------------------------------------------------------

s = master.sort_values("Beds_per_1000")
cum_pop = np.insert((s["Population"].cumsum() / s["Population"].sum()).values, 0, 0)
cum_beds = np.insert((s["Beds in all Hospitals"].cumsum() / s["Beds in all Hospitals"].sum()).values, 0, 0)
gini = 1 - np.sum((cum_pop[1:] - cum_pop[:-1]) * (cum_beds[1:] + cum_beds[:-1]))
stats["gini_beds"] = round(gini, 2)
plt.figure(figsize=(6.5, 6))
plt.plot(cum_pop, cum_beds, color=BLUE, lw=2, label="Districts (sorted by beds per 1,000)")
plt.plot([0, 1], [0, 1], ls="--", color="grey", label="Perfect equality")
plt.fill_between(cum_pop, cum_beds, cum_pop, alpha=0.15, color=BLUE)
plt.xlabel("Cumulative share of population")
plt.ylabel("Cumulative share of hospital beds")
plt.title(f"Lorenz curve of hospital beds (Gini = {gini:.2f})")
plt.legend()
save("fig06_lorenz")

# ------------------------------------------------------------
# Figure 7: correlation heatmap
# ------------------------------------------------------------

cols = ["Population", "Total_Facilities", "Beds in all Hospitals", "Doctors in all Hospitals",
        "Health Sub-Centres", "Primary Health Centres", "Community Health Centres",
        "Area Hospitals", "Teaching Hospitals", "Urban Population (%)"]
c = master[cols].corr()
stats["corr"] = c.round(2).to_dict()
plt.figure(figsize=(10, 8))
sns.heatmap(c, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation matrix of healthcare infrastructure indicators")
save("fig07_corr")

# ------------------------------------------------------------
# Figure 8: facility location map
# ------------------------------------------------------------

g = geo.dropna(subset=["Latitude", "longitude"])
g = g[g["Latitude"].between(15.5, 20.0) & g["longitude"].between(77.0, 81.5)]
stats["mapped_points"] = len(g)
stats["dropped_coords"] = len(geo) - len(g)
big = g["Facility Type"].isin(["District Hospital", "Medical Colleges Hospital",
                                "Sub-District Hospital", "Women Hospital"])
plt.figure(figsize=(8, 8))
for region, color, size in [("Rural", BLUE, 3), ("Urban", "#E67E22", 5)]:
    p = g[(g["Region Indicator"] == region) & ~big]
    plt.scatter(p["longitude"], p["Latitude"], s=size, color=color, alpha=0.55, label=f"{region} facility")
plt.scatter(g[big]["longitude"], g[big]["Latitude"], s=40, marker="^", color="#C0392B",
            edgecolor="white", lw=0.5, label="Hospital (SDH / DH / MCH / Women)")
for name, lat, lon in [("Hyderabad", 17.385, 78.487), ("Warangal", 17.97, 79.59),
                       ("Karimnagar", 18.44, 79.13), ("Nizamabad", 18.67, 78.10),
                       ("Khammam", 17.25, 80.15), ("Mahabubnagar", 16.74, 78.0),
                       ("Adilabad", 19.66, 78.53)]:
    plt.annotate(name, (lon, lat), fontsize=9, weight="bold", xytext=(5, 5), textcoords="offset points")
plt.xlabel("Longitude (°E)")
plt.ylabel("Latitude (°N)")
plt.title(f"Public healthcare facility locations, Telangana ({len(g):,} points)")
plt.legend(loc="lower left", markerscale=2)
plt.gca().set_aspect("equal")
save("fig08_map")

# ------------------------------------------------------------
# Figure 9: distance from primary facilities to nearest hospital
# ------------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * np.arcsin(np.sqrt(a))

primary = g[g["Facility Type"].isin(["SubCentre", "Primary Health Centre"])].copy()
bedded = g[g["Facility Type"].isin(["Community Health Center", "Sub-District Hospital",
                                    "District Hospital", "Medical Colleges Hospital",
                                    "Women Hospital"])]
dist = haversine(primary["Latitude"].values[:, None], primary["longitude"].values[:, None],
                 bedded["Latitude"].values[None, :], bedded["longitude"].values[None, :])
primary["km"] = dist.min(axis=1)
stats["nn_median"] = round(primary["km"].median(), 1)
stats["nn_mean"] = round(primary["km"].mean(), 1)
stats["nn_over_20"] = round((primary["km"] > 20).mean() * 100, 1)
stats["nn_over_30"] = round((primary["km"] > 30).mean() * 100, 1)
by_d = primary.groupby("District")["km"].median().sort_values(ascending=False)
stats["nn_district_worst"] = by_d.head(6).round(1).to_dict()
stats["nn_district_best"] = by_d.tail(4).round(1).to_dict()
stats["n_primary"] = len(primary)
stats["n_bedded"] = len(bedded)

plt.figure(figsize=(9, 5))
plt.hist(primary["km"], bins=40, color=BLUE, edgecolor="white")
plt.axvline(primary["km"].median(), color="#C0392B", ls="--", label=f"Median = {primary['km'].median():.1f} km")
plt.xlabel("Distance to nearest bedded facility (km)")
plt.ylabel("Number of sub-centres / PHCs")
plt.title("Distance from primary facilities to the nearest CHC or hospital")
plt.legend()
save("fig09_distance")

# ------------------------------------------------------------
# Figure 10-11: K-Means elbow + clusters
# ------------------------------------------------------------

feats = ["Beds_per_1000", "Doctors_per_100000", "Facilities_per_100000", "Rural_Facility_Percent"]
X = StandardScaler().fit_transform(master[feats])
inertia = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).inertia_ for k in range(2, 7)]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
axes[0].plot(range(2, 7), inertia, marker="o", color=BLUE)
axes[0].set_xlabel("Number of clusters (k)")
axes[0].set_ylabel("Inertia")
axes[0].set_title("Elbow method")
palette = {0: BLUE, 1: "#E67E22", 2: "#C0392B"}
for cl, sub in ml.groupby("Cluster"):
    axes[1].scatter(sub["Rural_Facility_Percent"], sub["Beds_per_1000"], s=70,
                    color=palette.get(cl, "grey"), label=f"Cluster {cl}")
for _, r in ml.iterrows():
    if r["Cluster"] != 0 or r["Beds_per_1000"] > 1.9 or r["Beds_per_1000"] < 0.85:
        axes[1].annotate(r["District"], (r["Rural_Facility_Percent"], r["Beds_per_1000"]),
                         fontsize=8, xytext=(4, 3), textcoords="offset points")
axes[1].set_xlabel("Rural share of facilities (%)")
axes[1].set_ylabel("Beds per 1,000 people")
axes[1].set_title("K-Means district clusters (k = 3)")
axes[1].legend()
save("fig10_kmeans")

prof = ml.groupby("Cluster")[feats].mean().round(2)
prof["Districts"] = ml.groupby("Cluster").size()
prof["Members"] = ml.groupby("Cluster")["District"].apply(lambda s: ", ".join(sorted(s)))
stats["clusters"] = prof.to_dict("index")

# ------------------------------------------------------------
# Figure 12: Random Forest
# ------------------------------------------------------------

rf_feats = ["Population", "Total_Facilities", "Doctors in all Hospitals", "Health Sub-Centres",
            "Primary Health Centres", "Community Health Centres", "Area Hospitals",
            "District Hospitals", "Teaching Hospitals", "Ayurveda Hospitals (incl. Dispensaries)",
            "Homeopathic Hospitals (incl. Dispensaries)", "Unani Hospitals (incl. Dispensaries)",
            "Naturopathy Hospitals (incl. Dispensaries)"]
Xtr, Xte, ytr, yte = train_test_split(master[rf_feats], master["Beds in all Hospitals"],
                                      test_size=0.2, random_state=42)
rf = RandomForestRegressor(n_estimators=300, random_state=42).fit(Xtr, ytr)
pred = rf.predict(Xte)
stats["rf_mae"] = round(mean_absolute_error(yte, pred), 1)
stats["rf_rmse"] = round(float(np.sqrt(((yte - pred) ** 2).mean())), 1)
stats["rf_r2"] = round(r2_score(yte, pred), 2)
stats["rf_train"], stats["rf_test"] = len(Xtr), len(Xte)
imp = pd.Series(rf.feature_importances_, index=rf_feats).sort_values()
stats["rf_importance"] = imp.sort_values(ascending=False).round(3).head(6).to_dict()

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
axes[0].barh(imp.index, imp.values, color=BLUE)
axes[0].set_xlabel("Importance")
axes[0].set_title("Random Forest feature importance")
axes[1].scatter(yte, pred, color=BLUE, s=60)
lim = [0, max(yte.max(), pred.max()) * 1.1]
axes[1].plot(lim, lim, ls="--", color="grey")
axes[1].set_xlabel("Actual beds")
axes[1].set_ylabel("Predicted beds")
axes[1].set_title(f"Actual vs predicted (test set, R² = {stats['rf_r2']})")
save("fig11_rf")

with open(os.path.join(FIG_DIR, "stats.json"), "w") as f:
    json.dump(stats, f, indent=1, default=float)

print(json.dumps(stats, indent=1, default=float))
