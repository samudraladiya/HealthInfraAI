import os
import re
import shutil

import numpy as np
import pandas as pd


# ============================================================
# HEALTHINFRAAI - BUILD DISTRICT DATASETS
# ============================================================
#
# Rebuilds data/geolocation.csv, data/Hospitals.csv and
# data/master.csv from the real facility register kept in
# data_old/geolocation.csv (7,001 Telangana public facilities
# with real names, mandals and coordinates).
#
# Facility counts come straight from the register. Beds and
# doctors are not in the register, so they are ESTIMATED from
# IPHS-style norms per facility type plus a private-sector
# component that is concentrated in urban areas.
#
# Run order:  build_data.py -> eda.py -> ml.py
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OLD_DIR = os.path.join(BASE_DIR, "data_old")
BACKUP_DIR = os.path.join(BASE_DIR, "data_synthetic_backup")

rng = np.random.default_rng(42)


# ============================================================
# 1. DISTRICT NAME MAPPING (register uses pre-2021 names)
# ============================================================

DISTRICT_MAP = {
    "Jagitial": "Jagtial",
    "Jangoan": "Jangaon",
    "Jayashankar Bhupalapally": "Jayashankar Bhupalpally",
    "Kumuram Bheem Asifabad": "Kumuram Bheem",
    "Mahbubnagar": "Mahabubnagar",
    "Medchal Malkajgiri": "Medchal-Malkajgiri",
    "Warangal Urban": "Hanumakonda",
    "Warangal Rural": "Warangal",
}


# ============================================================
# 2. PER-FACILITY NORMS (public sector)
# ============================================================

# Approximate IPHS bed / doctor norms per facility type
FACILITY_NORMS = {
    # type: (beds, doctors)
    "SubCentre": (0, 0),
    "Primary Health Centre": (6, 2),
    "Urban Health Centre (UPHC)": (0, 2),
    "Urban health and wellness center (UHWC)": (0, 1),
    "Community Health Center": (30, 6),
    "Sub-District Hospital": (100, 18),
    "District Hospital": (300, 45),
    "Women Hospital": (150, 20),
    "Medical Colleges Hospital": (600, 180),
    "Ayush Teaching Hospital": (60, 25),
    "M&CW Center": (30, 6),
    "Post Partum Unit": (10, 2),
    "Ayurveda dispensary": (0, 1),
    "Homoeopathy dispensary": (0, 1),
    "Unani dispensary": (0, 1),
    "Yoga And Naturopathy dispensary": (0, 1),
    "Ayush Dispensaries": (0, 1),
    "Others": (10, 2),
}

# Private sector capacity (heavily urban)
PRIVATE_BEDS_PER_1000 = {"Urban": 2.2, "Rural": 0.25}
PRIVATE_DOCTORS_PER_100000 = {"Urban": 45, "Rural": 6}

# District infrastructure columns -> register facility types
HOSPITAL_COLUMNS = {
    "Health Sub-Centres": ["SubCentre"],
    "Primary Health Centres": ["Primary Health Centre"],
    "Community Health Centres": ["Community Health Center"],
    "Area Hospitals": ["Sub-District Hospital"],
    "District Hospitals": ["District Hospital"],
    "Teaching Hospitals": ["Medical Colleges Hospital"],
    "Ayurveda Hospitals (incl. Dispensaries)": ["Ayurveda dispensary"],
    "Homeopathic Hospitals (incl. Dispensaries)": ["Homoeopathy dispensary"],
    "Unani Hospitals (incl. Dispensaries)": ["Unani dispensary"],
    "Naturopathy Hospitals (incl. Dispensaries)": [
        "Yoga And Naturopathy dispensary"
    ],
}

RURAL_BY_DEFAULT = {
    "SubCentre",
    "Primary Health Centre",
    "Community Health Center",
}


# ============================================================
# 3. BACK UP CURRENT DATA
# ============================================================

if not os.path.exists(BACKUP_DIR):
    shutil.copytree(DATA_DIR, BACKUP_DIR)
    print("Backed up previous data to:", BACKUP_DIR)


# ============================================================
# 4. FACILITY REGISTER -> data/geolocation.csv
# ============================================================

geo = pd.read_csv(
    os.path.join(OLD_DIR, "geolocation.csv"),
    encoding="utf-8-sig"
)

geo["District"] = geo["District"].str.strip().replace(DISTRICT_MAP)

geo["Facility Type"] = (
    geo["Facility Type"]
    .str.strip()
    .map(lambda s: re.sub(r"\s+", " ", s))
)

# Fill the few missing region tags using the facility type
missing_region = geo["Region Indicator"].isna()

geo.loc[missing_region, "Region Indicator"] = np.where(
    geo.loc[missing_region, "Facility Type"].isin(RURAL_BY_DEFAULT),
    "Rural",
    "Urban"
)

geo["Ownership Authority"] = geo["Ownership Authority"].fillna("Unknown")

geo.insert(0, "id", range(1, len(geo) + 1))

geo.to_csv(os.path.join(DATA_DIR, "geolocation.csv"), index=False)

print("Facilities:", len(geo))


# ============================================================
# 5. DISTRICT INFRASTRUCTURE -> data/Hospitals.csv
# ============================================================

demo = pd.read_csv(os.path.join(DATA_DIR, "Demographics (1).csv"))
demo = demo.rename(columns={"Districts": "District"})

type_counts = pd.crosstab(geo["District"], geo["Facility Type"])

geo["Beds_Est"] = geo["Facility Type"].map(
    lambda t: FACILITY_NORMS.get(t, (0, 0))[0]
)
geo["Doctors_Est"] = geo["Facility Type"].map(
    lambda t: FACILITY_NORMS.get(t, (0, 0))[1]
)

rows = []

for _, d in demo.iterrows():

    district = d["District"]
    counts = type_counts.loc[district]
    facilities = geo[geo["District"] == district]

    row = {"District": district}

    for column, types in HOSPITAL_COLUMNS.items():
        row[column] = int(sum(counts.get(t, 0) for t in types))

    # Public capacity from the facility mix (+-10% variation)
    public_beds = facilities["Beds_Est"].sum() * rng.uniform(0.9, 1.1)
    public_doctors = facilities["Doctors_Est"].sum() * rng.uniform(0.9, 1.1)

    # Private capacity follows urban population
    private_beds = (
        d["Urban"] * PRIVATE_BEDS_PER_1000["Urban"] / 1000
        + d["Rural"] * PRIVATE_BEDS_PER_1000["Rural"] / 1000
    ) * rng.uniform(0.85, 1.15)

    private_doctors = (
        d["Urban"] * PRIVATE_DOCTORS_PER_100000["Urban"] / 100000
        + d["Rural"] * PRIVATE_DOCTORS_PER_100000["Rural"] / 100000
    ) * rng.uniform(0.85, 1.15)

    row["Doctors in all Hospitals"] = int(round(public_doctors + private_doctors))
    row["Beds in all Hospitals"] = int(round(public_beds + private_beds))

    # Rural vs urban capacity split (used in the Rural / Urban view)
    for region in ["Rural", "Urban"]:

        region_facilities = facilities[
            facilities["Region Indicator"] == region
        ]

        region_private_beds = (
            d[region] * PRIVATE_BEDS_PER_1000[region] / 1000
        )

        region_private_doctors = (
            d[region] * PRIVATE_DOCTORS_PER_100000[region] / 100000
        )

        row[f"{region}_Beds"] = int(round(
            region_facilities["Beds_Est"].sum() + region_private_beds
        ))

        row[f"{region}_Doctors"] = int(round(
            region_facilities["Doctors_Est"].sum() + region_private_doctors
        ))

    rows.append(row)

capacity = pd.DataFrame(rows)

hospital_cols = (
    ["District"]
    + list(HOSPITAL_COLUMNS)
    + ["Doctors in all Hospitals", "Beds in all Hospitals"]
)

capacity[hospital_cols].to_csv(
    os.path.join(DATA_DIR, "Hospitals.csv"),
    index=False
)


# ============================================================
# 6. MASTER DATASET -> data/master.csv
# ============================================================

master = capacity[hospital_cols].merge(demo, on="District", how="left")

master["Population"] = master["Males"] + master["Females"]

grouped = geo.groupby("District")

master["Total_Facilities"] = master["District"].map(grouped.size())

master["Functional_Facilities"] = master["District"].map(
    grouped["Operational Status"].apply(lambda s: (s == "Functional").sum())
)

master["Rural_Facilities"] = master["District"].map(
    grouped["Region Indicator"].apply(lambda s: (s == "Rural").sum())
)

master["Urban_Facilities"] = master["District"].map(
    grouped["Region Indicator"].apply(lambda s: (s == "Urban").sum())
)

master["Beds_per_1000"] = (
    master["Beds in all Hospitals"] / master["Population"] * 1000
)

master["Doctors_per_100000"] = (
    master["Doctors in all Hospitals"] / master["Population"] * 100000
)

master["Facilities_per_100000"] = (
    master["Total_Facilities"] / master["Population"] * 100000
)

master["Functional_Facility_Percent"] = (
    master["Functional_Facilities"] / master["Total_Facilities"] * 100
)

master["Rural_Facility_Percent"] = (
    master["Rural_Facilities"] / master["Total_Facilities"] * 100
)

master["Urban_Facility_Percent"] = (
    master["Urban_Facilities"] / master["Total_Facilities"] * 100
)

# Extra rural / urban capacity columns (appended, existing order kept)
for column in ["Rural_Beds", "Urban_Beds", "Rural_Doctors", "Urban_Doctors"]:
    master[column] = capacity[column].values

master.to_csv(os.path.join(DATA_DIR, "master.csv"), index=False)

print("\nSaved:")
print("data/geolocation.csv")
print("data/Hospitals.csv")
print("data/master.csv")

print(
    master[
        [
            "District",
            "Total_Facilities",
            "Beds_per_1000",
            "Doctors_per_100000",
            "Rural_Facility_Percent",
        ]
    ].round(2).to_string(index=False)
)
