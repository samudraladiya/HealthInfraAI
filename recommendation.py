import pandas as pd
import os
from geopy.distance import geodesic


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_data():
    facility_path = os.path.join(DATA_DIR, "geolocation.csv")
    hospital_path = os.path.join(DATA_DIR, "major_hospitals.csv")

    facilities = pd.read_csv(facility_path)
    hospitals = pd.read_csv(hospital_path)

    return facilities, hospitals


# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------

def clean_data(df):

    df = df.copy()

    if "District" in df.columns:
        df["District"] = (
            df["District"]
            .astype(str)
            .str.strip()
        )

    if "Facility Type" in df.columns:
        df["Facility Type"] = (
            df["Facility Type"]
            .astype(str)
            .str.strip()
        )

    if "Hospital Type" in df.columns:
        df["Hospital Type"] = (
            df["Hospital Type"]
            .astype(str)
            .str.strip()
        )

    if "Ownership" in df.columns:
        df["Ownership"] = (
            df["Ownership"]
            .astype(str)
            .str.strip()
        )

    return df


# ---------------------------------------------------------
# MAJOR HOSPITAL SEARCH
# ---------------------------------------------------------

def search_major_hospitals(
    district=None,
    hospital_type=None,
    ownership=None,
    service=None,
    latitude=None,
    longitude=None,
    top_n=10
):

    _, hospitals = load_data()

    hospitals = clean_data(hospitals)

    # District filter
    if district and district != "All":
        hospitals = hospitals[
            hospitals["District"].str.lower()
            == district.lower()
        ]

    # Hospital type filter
    if hospital_type and hospital_type != "All":
        hospitals = hospitals[
            hospitals["Hospital Type"].str.lower()
            == hospital_type.lower()
        ]

    # Ownership filter
    if ownership and ownership != "All":
        hospitals = hospitals[
            hospitals["Ownership"].str.lower()
            == ownership.lower()
        ]

    # Service filter
    if service and service != "All":
        hospitals = hospitals[
            hospitals["Services"]
            .fillna("")
            .str.lower()
            .str.contains(service.lower(), regex=False)
        ]

    # Distance
    if latitude is not None and longitude is not None:

        def calculate_distance(row):

            try:
                return geodesic(
                    (latitude, longitude),
                    (row["Latitude"], row["Longitude"])
                ).km

            except:
                return None

        hospitals["Distance_km"] = hospitals.apply(
            calculate_distance,
            axis=1
        )

        hospitals = hospitals.sort_values(
            "Distance_km",
            ascending=True
        )

    else:
        hospitals["Distance_km"] = None

    return hospitals.head(top_n)


# ---------------------------------------------------------
# PUBLIC / PRIMARY FACILITY SEARCH
# ---------------------------------------------------------

def search_public_facilities(
    district=None,
    facility_type=None,
    region=None,
    latitude=None,
    longitude=None,
    top_n=10
):

    facilities, _ = load_data()

    facilities = clean_data(facilities)

    # District
    if district and district != "All":

        facilities = facilities[
            facilities["District"].str.lower()
            == district.lower()
        ]

    # Facility type
    if facility_type and facility_type != "All":

        facilities = facilities[
            facilities["Facility Type"].str.lower()
            == facility_type.lower()
        ]

    # Rural / Urban
    if region and region != "All":

        facilities = facilities[
            facilities["Region Indicator"]
            .fillna("")
            .str.lower()
            == region.lower()
        ]

    # Distance
    if latitude is not None and longitude is not None:

        def calculate_distance(row):

            try:

                return geodesic(
                    (latitude, longitude),
                    (row["Latitude"], row["longitude"])
                ).km

            except:

                return None

        facilities["Distance_km"] = facilities.apply(
            calculate_distance,
            axis=1
        )

        facilities = facilities.sort_values(
            "Distance_km",
            ascending=True
        )

    else:

        facilities["Distance_km"] = None

    return facilities.head(top_n)


# ---------------------------------------------------------
# COMBINED SEARCH
# ---------------------------------------------------------

def find_healthcare(
    category="Major Hospitals",
    district=None,
    facility_type=None,
    hospital_type=None,
    ownership=None,
    service=None,
    region=None,
    latitude=None,
    longitude=None,
    top_n=10
):

    if category == "Major Hospitals":

        return search_major_hospitals(
            district=district,
            hospital_type=hospital_type,
            ownership=ownership,
            service=service,
            latitude=latitude,
            longitude=longitude,
            top_n=top_n
        )

    else:

        return search_public_facilities(
            district=district,
            facility_type=facility_type,
            region=region,
            latitude=latitude,
            longitude=longitude,
            top_n=top_n
        )