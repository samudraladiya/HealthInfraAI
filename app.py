import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from recommendation import (
    find_healthcare,
    load_data
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HealthInfraAI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_master():

    return pd.read_csv(
        os.path.join(DATA_DIR, "master.csv")
    )


@st.cache_data
def load_ml():

    path = os.path.join(
        DATA_DIR,
        "master_ml.csv"
    )

    if os.path.exists(path):
        return pd.read_csv(path)

    return None


@st.cache_data
def load_hospitals():

    path = os.path.join(
        DATA_DIR,
        "major_hospitals.csv"
    )

    if os.path.exists(path):
        return pd.read_csv(path)

    return pd.DataFrame()


master = load_master()
ml_data = load_ml()
hospitals = load_hospitals()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def page_header(kicker, title, description):

    st.caption(kicker.upper())

    st.title(title)

    st.write(description)

    st.divider()


def format_number(value):

    if pd.isna(value):
        return "—"

    return f"{value:,.0f}"


def plot_layout(fig, height=450):

    fig.update_layout(
        template="simple_white",
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=45,
            b=20
        ),
        font=dict(
            family="Arial",
            color="#183D5B"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("HealthInfraAI")

    st.caption(
        "Telangana Healthcare Infrastructure "
        "Intelligence"
    )

    st.divider()

    page = st.radio(
        "EXPLORE",
        [
            "Home",
            "Healthcare Analytics",
            "District Explorer",
            "ML Insights",
            "Find Healthcare",
            "About"
        ]
    )

    st.divider()

    st.caption(
        "Data-driven healthcare intelligence"
    )


# =========================================================
# HOME
# =========================================================

if page == "Home":

    st.caption(
        "HEALTHCARE INTELLIGENCE · TELANGANA"
    )

    st.title(
        "Understanding Healthcare\n"
        "Infrastructure Across Telangana."
    )

    st.write(
        "Explore healthcare capacity through "
        "facilities, beds, doctors, population "
        "and infrastructure patterns."
    )

    st.divider()

    # -----------------------------------------------------
    # KEY NUMBERS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Districts",
            master["District"].nunique()
        )

    with c2:

        st.metric(
            "Mapped Facilities",
            f"{master['Total_Facilities'].sum():,.0f}"
        )

    with c3:

        st.metric(
            "Hospital Beds",
            f"{master['Beds in all Hospitals'].sum():,.0f}"
        )

    with c4:

        st.metric(
            "Doctors",
            f"{master['Doctors in all Hospitals'].sum():,.0f}"
        )

    st.divider()

    # -----------------------------------------------------
    # INTRO
    # -----------------------------------------------------

    left, right = st.columns(
        [1.4, 1],
        gap="large"
    )

    with left:

        st.subheader(
            "From raw numbers to meaningful insights."
        )

        st.write(
            """
            HealthInfraAI brings together healthcare
            facility, infrastructure and demographic
            data to understand healthcare capacity
            across Telangana.
            """
        )

        st.write(
            """
            Instead of relying only on raw facility
            counts, the platform uses population-adjusted
            indicators such as beds per 1,000 people,
            doctors per 100,000 people and facilities
            per 100,000 people.
            """
        )

    with right:

        st.info(
            """
            **What HealthInfraAI analyzes**

            • Healthcare facilities  
            • Hospital beds  
            • Doctors  
            • Population  
            • Rural / urban coverage  
            • District infrastructure  
            • Machine learning patterns
            """
        )

    st.divider()

    # -----------------------------------------------------
    # QUICK EXPLORE
    # -----------------------------------------------------

    st.subheader("Explore the platform")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(
            """
            ### 01 · Analytics

            Compare healthcare capacity,
            population and infrastructure
            across districts.
            """
        )

    with c2:

        st.info(
            """
            ### 02 · District Explorer

            Explore the healthcare profile
            of an individual district.
            """
        )

    with c3:

        st.info(
            """
            ### 03 · Find Healthcare

            Search major hospitals and
            public healthcare facilities.
            """
        )


# =========================================================
# HEALTHCARE ANALYTICS
# =========================================================

elif page == "Healthcare Analytics":

    page_header(
        "DATA ANALYSIS",
        "Healthcare Analytics",
        "Explore healthcare capacity and population-adjusted "
        "indicators across Telangana districts."
    )

    # -----------------------------------------------------
    # TABS
    # -----------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Capacity",
            "Population-adjusted",
            "Rural / Urban"
        ]
    )

    # =====================================================
    # CAPACITY
    # =====================================================

    with tab1:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Facilities by District"
            )

            temp = (
                master
                .sort_values(
                    "Total_Facilities",
                    ascending=False
                )
                .head(15)
            )

            fig = px.bar(
                temp,
                x="Total_Facilities",
                y="District",
                orientation="h",
                title="Top districts by mapped facilities",
                color_discrete_sequence=[
                    "#245F84"
                ]
            )

            fig = plot_layout(fig, 520)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "Hospital Beds"
            )

            temp = (
                master
                .sort_values(
                    "Beds in all Hospitals",
                    ascending=False
                )
                .head(15)
            )

            fig = px.bar(
                temp,
                x="Beds in all Hospitals",
                y="District",
                orientation="h",
                title="Total reported hospital beds",
                color_discrete_sequence=[
                    "#65A8C5"
                ]
            )

            fig = plot_layout(fig, 520)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader(
            "Population vs Hospital Beds"
        )

        fig = px.scatter(
            master,
            x="Population",
            y="Beds in all Hospitals",
            hover_name="District",
            size="Population",
            color_discrete_sequence=[
                "#245F84"
            ]
        )

        fig = plot_layout(fig, 500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # NORMALIZED
    # =====================================================

    with tab2:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Beds per 1,000 People"
            )

            temp = (
                master
                .sort_values(
                    "Beds_per_1000",
                    ascending=False
                )
                .head(15)
            )

            fig = px.bar(
                temp,
                x="Beds_per_1000",
                y="District",
                orientation="h",
                color_discrete_sequence=[
                    "#245F84"
                ]
            )

            fig = plot_layout(fig, 520)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "Doctors per 100,000 People"
            )

            temp = (
                master
                .sort_values(
                    "Doctors_per_100000",
                    ascending=False
                )
                .head(15)
            )

            fig = px.bar(
                temp,
                x="Doctors_per_100000",
                y="District",
                orientation="h",
                color_discrete_sequence=[
                    "#65A8C5"
                ]
            )

            fig = plot_layout(fig, 520)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader(
            "Facilities per 100,000 People"
        )

        temp = (
            master
            .sort_values(
                "Facilities_per_100000",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            temp,
            x="Facilities_per_100000",
            y="District",
            orientation="h",
            color_discrete_sequence=[
                "#3C7FA2"
            ]
        )

        fig = plot_layout(fig, 520)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # RURAL / URBAN
    # =====================================================

    with tab3:

        rural = master[
            "Rural_Facilities"
        ].sum()

        urban = master[
            "Urban_Facilities"
        ].sum()

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Rural Facilities",
                f"{rural:,.0f}"
            )

        with c2:

            st.metric(
                "Urban Facilities",
                f"{urban:,.0f}"
            )

        fig = px.pie(
            names=[
                "Rural",
                "Urban"
            ],
            values=[
                rural,
                urban
            ],
            hole=0.55,
            color_discrete_sequence=[
                "#245F84",
                "#9CC6D8"
            ]
        )

        fig = plot_layout(fig, 500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Rural areas have more facilities because every "
            "village cluster gets a small sub-centre or PHC. "
            "Urban facilities are fewer but much larger, so "
            "compare capacity below."
        )

        # -------------------------------------------------
        # CAPACITY SHARE
        # -------------------------------------------------

        capacity_cols = [
            "Rural_Beds",
            "Urban_Beds",
            "Rural_Doctors",
            "Urban_Doctors"
        ]

        if all(c in master.columns for c in capacity_cols):

            st.subheader(
                "Share of population vs healthcare capacity"
            )

            share_rows = []

            for measure, rural_value, urban_value in [
                (
                    "Population",
                    master["Rural"].sum(),
                    master["Urban"].sum()
                ),
                (
                    "Facilities",
                    rural,
                    urban
                ),
                (
                    "Hospital beds (est.)",
                    master["Rural_Beds"].sum(),
                    master["Urban_Beds"].sum()
                ),
                (
                    "Doctors (est.)",
                    master["Rural_Doctors"].sum(),
                    master["Urban_Doctors"].sum()
                )
            ]:

                total = rural_value + urban_value

                share_rows.append({
                    "Measure": measure,
                    "Region": "Rural",
                    "Share (%)": rural_value / total * 100
                })

                share_rows.append({
                    "Measure": measure,
                    "Region": "Urban",
                    "Share (%)": urban_value / total * 100
                })

            fig = px.bar(
                pd.DataFrame(share_rows),
                x="Share (%)",
                y="Measure",
                color="Region",
                orientation="h",
                barmode="stack",
                text_auto=".0f",
                color_discrete_sequence=[
                    "#245F84",
                    "#9CC6D8"
                ]
            )

            fig = plot_layout(fig, 380)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            rural_pop = master["Rural"].sum()
            urban_pop = master["Urban"].sum()

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Beds / 1,000 (rural)",
                    f"{master['Rural_Beds'].sum() / rural_pop * 1000:.2f}"
                )

                st.metric(
                    "Doctors / 100,000 (rural)",
                    f"{master['Rural_Doctors'].sum() / rural_pop * 100000:.1f}"
                )

            with c2:

                st.metric(
                    "Beds / 1,000 (urban)",
                    f"{master['Urban_Beds'].sum() / urban_pop * 1000:.2f}"
                )

                st.metric(
                    "Doctors / 100,000 (urban)",
                    f"{master['Urban_Doctors'].sum() / urban_pop * 100000:.1f}"
                )

            st.caption(
                "Facility counts are from the public facility "
                "register. Beds and doctors are estimated from "
                "IPHS norms per facility type plus a private-"
                "sector share concentrated in urban areas."
            )


# =========================================================
# DISTRICT EXPLORER
# =========================================================

elif page == "District Explorer":

    page_header(
        "DISTRICT INTELLIGENCE",
        "District Explorer",
        "Explore the healthcare infrastructure profile "
        "of an individual Telangana district."
    )

    district = st.selectbox(
        "Select a district",
        sorted(
            master["District"]
            .dropna()
            .unique()
        )
    )

    row = master[
        master["District"] == district
    ].iloc[0]

    st.subheader(district)

    st.caption(
        "Healthcare infrastructure profile"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Population",
            format_number(
                row["Population"]
            )
        )

    with c2:

        st.metric(
            "Facilities",
            format_number(
                row["Total_Facilities"]
            )
        )

    with c3:

        st.metric(
            "Hospital Beds",
            format_number(
                row["Beds in all Hospitals"]
            )
        )

    with c4:

        st.metric(
            "Doctors",
            format_number(
                row["Doctors in all Hospitals"]
            )
        )

    st.divider()

    # -----------------------------------------------------
    # NORMALIZED INDICATORS
    # -----------------------------------------------------

    st.subheader(
        "Population-adjusted indicators"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Beds / 1,000",
            f"{row['Beds_per_1000']:.2f}"
        )

    with c2:

        st.metric(
            "Doctors / 100,000",
            f"{row['Doctors_per_100000']:.2f}"
        )

    with c3:

        st.metric(
            "Facilities / 100,000",
            f"{row['Facilities_per_100000']:.2f}"
        )

    st.divider()

    # -----------------------------------------------------
    # INFRASTRUCTURE
    # -----------------------------------------------------

    st.subheader(
        "Infrastructure breakdown"
    )

    infrastructure_cols = [
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

    available = [
        c for c in infrastructure_cols
        if c in master.columns
    ]

    values_df = pd.DataFrame({
        "Infrastructure": available,
        "Count": [
            row[c]
            for c in available
        ]
    })

    fig = px.bar(
        values_df,
        x="Count",
        y="Infrastructure",
        orientation="h",
        color_discrete_sequence=[
            "#245F84"
        ]
    )

    fig = plot_layout(fig, 550)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# ML INSIGHTS
# =========================================================

elif page == "ML Insights":

    page_header(
        "MACHINE LEARNING",
        "ML Insights",
        "Explore bed-capacity modelling and district "
        "infrastructure patterns."
    )

    if ml_data is None:

        st.warning(
            "Run ml.py first to generate the ML dataset."
        )

    else:

        tab1, tab2 = st.tabs(
            [
                "District Clusters",
                "Infrastructure Indicators"
            ]
        )

        # -------------------------------------------------
        # CLUSTERS
        # -------------------------------------------------

        with tab1:

            if "Cluster" in ml_data.columns:

                cluster_counts = (
                    ml_data["Cluster"]
                    .value_counts()
                    .sort_index()
                )

                st.subheader(
                    "District infrastructure profiles"
                )

                c1, c2, c3 = st.columns(3)

                for col, (cluster, count) in zip(
                    [c1, c2, c3],
                    cluster_counts.items()
                ):

                    with col:

                        st.metric(
                            f"Cluster {cluster}",
                            f"{count} districts"
                        )

                st.divider()

                selected_cluster = st.selectbox(
                    "Explore a cluster",
                    sorted(
                        ml_data["Cluster"]
                        .dropna()
                        .unique()
                    )
                )

                cluster_df = ml_data[
                    ml_data["Cluster"]
                    == selected_cluster
                ]

                st.dataframe(
                    cluster_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Clusters represent districts with similar "
                    "infrastructure characteristics based on "
                    "the selected normalized indicators."
                )

        # -------------------------------------------------
        # INDICATORS
        # -------------------------------------------------

        with tab2:

            indicators = [
                c for c in [
                    "Beds_per_1000",
                    "Doctors_per_100000",
                    "Facilities_per_100000",
                    "Rural_Facility_Percent"
                ]
                if c in ml_data.columns
            ]

            if indicators:

                selected = st.selectbox(
                    "Select an indicator",
                    indicators
                )

                temp = (
                    ml_data
                    .sort_values(
                        selected,
                        ascending=False
                    )
                )

                fig = px.bar(
                    temp,
                    x=selected,
                    y="District",
                    orientation="h",
                    color_discrete_sequence=[
                        "#245F84"
                    ]
                )

                fig = plot_layout(fig, 650)

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


# =========================================================
# FIND HEALTHCARE
# =========================================================

elif page == "Find Healthcare":

    page_header(
        "FACILITY DISCOVERY",
        "Find Healthcare",
        "Search major hospitals and public healthcare "
        "facilities across Telangana."
    )

    category = st.radio(
        "I am looking for",
        [
            "Major Hospitals",
            "Public Healthcare Facilities"
        ],
        horizontal=True
    )

    st.divider()

    # =====================================================
    # MAJOR HOSPITALS
    # =====================================================

    if category == "Major Hospitals":

        st.subheader(
            "Search major hospitals"
        )

        col1, col2 = st.columns(2)

        with col1:

            districts = [
                "All"
            ] + sorted(
                hospitals["District"]
                .dropna()
                .unique()
            )

            district = st.selectbox(
                "District",
                districts
            )

        with col2:

            hospital_types = [
                "All"
            ] + sorted(
                hospitals["Hospital Type"]
                .dropna()
                .unique()
            )

            hospital_type = st.selectbox(
                "Hospital type",
                hospital_types
            )

        col1, col2 = st.columns(2)

        with col1:

            ownerships = [
                "All"
            ] + sorted(
                hospitals["Ownership"]
                .dropna()
                .unique()
            )

            ownership = st.selectbox(
                "Ownership",
                ownerships
            )

        with col2:

            services = ["All"]

            for value in (
                hospitals["Services"]
                .dropna()
            ):

                for service in str(value).split(";"):

                    service = service.strip()

                    if (
                        service
                        and service not in services
                    ):
                        services.append(service)

            service = st.selectbox(
                "Service / specialty",
                sorted(services)
            )

        search = st.button(
            "Find Hospitals",
            type="primary",
            use_container_width=True
        )

        if search:

            results = find_healthcare(
                category="Major Hospitals",
                district=district,
                hospital_type=hospital_type,
                ownership=ownership,
                service=service,
                top_n=15
            )

            if results.empty:

                st.warning(
                    "No hospitals match these filters."
                )

            else:

                st.success(
                    f"{len(results)} hospitals found."
                )

                for _, hospital in results.iterrows():

                    with st.container(
                        border=True
                    ):

                        st.subheader(
                            hospital["Hospital Name"]
                        )

                        st.caption(
                            f"{hospital['District']} · "
                            f"{hospital['Area']}"
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:

                            st.write(
                                f"**Type:** "
                                f"{hospital['Hospital Type']}"
                            )

                        with c2:

                            st.write(
                                f"**Ownership:** "
                                f"{hospital['Ownership']}"
                            )

                        with c3:

                            st.write(
                                f"**Beds:** "
                                f"{hospital['Beds']:,}"
                            )

                        st.write(
                            f"**Services:** "
                            f"{hospital['Services']}"
                        )

                        st.write(
                            f"**Emergency:** "
                            f"{hospital['Emergency']}"
                        )

    # =====================================================
    # PUBLIC FACILITIES
    # =====================================================

    else:

        facilities, _ = load_data()

        st.subheader(
            "Search public healthcare facilities"
        )

        col1, col2 = st.columns(2)

        with col1:

            districts = [
                "All"
            ] + sorted(
                facilities["District"]
                .dropna()
                .unique()
            )

            district = st.selectbox(
                "District",
                districts
            )

        with col2:

            facility_types = [
                "All"
            ] + sorted(
                facilities["Facility Type"]
                .dropna()
                .unique()
            )

            facility_type = st.selectbox(
                "Facility type",
                facility_types
            )

        region = st.selectbox(
            "Region",
            [
                "All",
                "Rural",
                "Urban"
            ]
        )

        search = st.button(
            "Find Facilities",
            type="primary",
            use_container_width=True
        )

        if search:

            results = find_healthcare(
                category="Public Healthcare Facilities",
                district=district,
                facility_type=facility_type,
                region=region,
                top_n=20
            )

            if results.empty:

                st.warning(
                    "No facilities match these filters."
                )

            else:

                st.success(
                    f"{len(results)} facilities found."
                )

                for _, facility in results.iterrows():

                    with st.container(
                        border=True
                    ):

                        st.subheader(
                            facility["Facility Name"]
                        )

                        st.caption(
                            facility["District"]
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:

                            st.write(
                                f"**Type:** "
                                f"{facility['Facility Type']}"
                            )

                        with c2:

                            st.write(
                                f"**Region:** "
                                f"{facility.get(
                                    'Region Indicator',
                                    'Unknown'
                                )}"
                            )

                        with c3:

                            st.write(
                                f"**Status:** "
                                f"{facility.get(
                                    'Operational Status',
                                    'Unknown'
                                )}"
                            )

                        st.write(
                            f"**Ownership:** "
                            f"{facility.get(
                                'Ownership Authority',
                                'Unknown'
                            )}"
                        )


# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    page_header(
        "ABOUT THE PROJECT",
        "About HealthInfraAI",
        "A data-driven platform for understanding "
        "healthcare infrastructure across Telangana."
    )

    col1, col2 = st.columns(
        [1.3, 1],
        gap="large"
    )

    with col1:

        st.subheader(
            "Why HealthInfraAI?"
        )

        st.write(
            """
            Healthcare infrastructure is not evenly
            distributed across regions, and raw counts
            alone do not always show the full picture.
            HealthInfraAI combines facility,
            infrastructure and demographic data to
            provide a more meaningful view of healthcare
            capacity.
            """
        )

        st.write(
            """
            The platform uses population-adjusted
            indicators, exploratory data analysis and
            machine learning to identify infrastructure
            patterns across Telangana.
            """
        )

    with col2:

        st.info(
            """
            **Technology Stack**

            **Data**
            NumPy · Pandas

            **Visualisation**
            Matplotlib · Seaborn · Plotly

            **Machine Learning**
            Scikit-learn

            **Frontend**
            Streamlit

            **Geospatial**
            GeoPy
            """
        )

    st.divider()

    st.subheader(
        "Project modules"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.write(
            """
            **01 · Healthcare Analytics**

            Population-adjusted healthcare indicators
            and infrastructure comparisons.

            **02 · District Explorer**

            District-level healthcare profiles.

            **03 · ML Insights**

            Random Forest and K-Means analysis.
            """
        )

    with c2:

        st.write(
            """
            **04 · Find Healthcare**

            Major hospitals and public facilities.

            **05 · Data Integration**

            Facility, infrastructure and demographic
            datasets combined into a unified analytical
            workflow.
            """
        )

    st.divider()

    st.caption(
        "HealthInfraAI · Telangana Healthcare "
        "Infrastructure Intelligence & Facility "
        "Recommendation Platform"
    )