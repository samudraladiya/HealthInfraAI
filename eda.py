import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. LOAD DATA
# ==========================================

master = pd.read_csv("data/master.csv")

print("=" * 60)
print("HEALTHINFRAAI - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

print("\nDataset Shape:")
print(master.shape)

print("\nNumber of Districts:")
print(master["District"].nunique())


# ==========================================
# 2. MISSING VALUES
# ==========================================

print("\nMissing Values:")
print(master.isnull().sum())


# ==========================================
# 3. BASIC STATISTICS
# ==========================================

print("\nBasic Statistics:")
print(master.describe())


# ==========================================
# 4. TOP 10 DISTRICTS BY FACILITIES
# ==========================================

print("\nTop 10 Districts by Total Facilities:")

top_facilities = master.sort_values(
    "Total_Facilities",
    ascending=False
)[["District", "Total_Facilities"]].head(10)

print(top_facilities)


# ==========================================
# 5. TOP 10 DISTRICTS BY HOSPITAL BEDS
# ==========================================

print("\nTop 10 Districts by Hospital Beds:")

top_beds = master.dropna(
    subset=["Beds in all Hospitals"]
).sort_values(
    "Beds in all Hospitals",
    ascending=False
)[["District", "Beds in all Hospitals"]].head(10)

print(top_beds)


# ==========================================
# 6. TOP 10 BY BEDS PER 1,000 POPULATION
# ==========================================

print("\nTop 10 Districts by Beds per 1,000 Population:")

top_bed_ratio = master.dropna(
    subset=["Beds_per_1000"]
).sort_values(
    "Beds_per_1000",
    ascending=False
)[["District", "Beds_per_1000"]].head(10)

print(top_bed_ratio)


# ==========================================
# 7. TOP 10 BY DOCTORS PER 100,000
# ==========================================

print("\nTop 10 Districts by Doctors per 100,000:")

top_doctors = master.dropna(
    subset=["Doctors_per_100000"]
).sort_values(
    "Doctors_per_100000",
    ascending=False
)[["District", "Doctors_per_100000"]].head(10)

print(top_doctors)


# ==========================================
# 8. HOSPITAL BEDS PER 1,000 POPULATION
# ==========================================

plot_data = master.dropna(
    subset=["Beds_per_1000"]
).sort_values(
    "Beds_per_1000"
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_data["District"],
    plot_data["Beds_per_1000"]
)

plt.xlabel("Beds per 1,000 Population")
plt.ylabel("District")
plt.title("Hospital Beds per 1,000 Population")

plt.tight_layout()
plt.show()


# ==========================================
# 9. TOTAL HEALTHCARE FACILITIES
# ==========================================

plot_data = master.sort_values(
    "Total_Facilities",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_data["District"],
    plot_data["Total_Facilities"]
)

plt.xlabel("Number of Facilities")
plt.ylabel("District")
plt.title("Healthcare Facilities Across Telangana")

plt.tight_layout()
plt.show()


# ==========================================
# 10. POPULATION VS HOSPITAL BEDS
# ==========================================

plot_data = master.dropna(
    subset=["Population", "Beds in all Hospitals"]
)

plt.figure(figsize=(10, 6))

plt.scatter(
    plot_data["Population"],
    plot_data["Beds in all Hospitals"]
)

plt.xlabel("Population")
plt.ylabel("Hospital Beds")
plt.title("Population vs Hospital Bed Capacity")

plt.tight_layout()
plt.show()


# ==========================================
# 11. DOCTORS PER 100,000 POPULATION
# ==========================================

plot_data = master.dropna(
    subset=["Doctors_per_100000"]
).sort_values(
    "Doctors_per_100000"
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_data["District"],
    plot_data["Doctors_per_100000"]
)

plt.xlabel("Doctors per 100,000 Population")
plt.ylabel("District")
plt.title("Doctors per 100,000 Population")

plt.tight_layout()
plt.show()


# ==========================================
# 12. RURAL SHARE OF FACILITIES
# ==========================================

plot_data = master.sort_values(
    "Rural_Facility_Percent",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_data["District"],
    plot_data["Rural_Facility_Percent"]
)

plt.xlabel("Rural Facilities (%)")
plt.ylabel("District")
plt.title("Rural Share of Healthcare Facilities by District")

plt.tight_layout()
plt.show()


# ==========================================
# 13. OVERALL RURAL VS URBAN FACILITIES
# ==========================================

total_rural = master["Rural_Facilities"].sum()
total_urban = master["Urban_Facilities"].sum()

plt.figure(figsize=(7, 7))

plt.pie(
    [total_rural, total_urban],
    labels=["Rural Facilities", "Urban Facilities"],
    autopct="%1.1f%%"
)

plt.title("Overall Rural vs Urban Healthcare Facility Distribution")

plt.show()


# ==========================================
# 14. CORRELATION ANALYSIS
# ==========================================

correlation_columns = [
    "Population",
    "Total_Facilities",
    "Beds in all Hospitals",
    "Doctors in all Hospitals",
    "Health Sub-Centres",
    "Primary Health Centres",
    "Community Health Centres",
    "Area Hospitals",
    "District Hospitals",
    "Teaching Hospitals"
]

correlation_data = master[correlation_columns].corr()

plt.figure(figsize=(12, 9))

sns.heatmap(
    correlation_data,
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)

plt.title("Healthcare Infrastructure Correlation Matrix")

plt.tight_layout()
plt.show()


# ==========================================
# 15. SAVE FINAL MASTER DATA
# ==========================================

master.to_csv(
    "data/master_final.csv",
    index=False
)

print("\n" + "=" * 60)
print("EDA COMPLETE")
print("=" * 60)

print("Final dataset saved as:")
print("data/master_final.csv")