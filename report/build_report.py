import json
import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


# ============================================================
# HEALTHINFRAAI - COURSE-END PROJECT REPORT (CBIT EDAV FORMAT)
# ============================================================
#
# Usage: python report/build_report.py [page_numbers.json]
# The optional JSON maps contents items to page numbers.
# ============================================================

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(HERE, "figures")
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "HealthInfraAI_CEP_Report.docx")

S = json.load(open(os.path.join(FIG, "stats.json")))
PAGES = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}

STUDENT = "Samudrala Diya Nanda"
ROLL = "160125737047"
TITLE = ("HealthInfraAI: Exploratory Data Analysis and Geospatial Visualization "
         "of Healthcare Infrastructure across Telangana Districts")
FONT = "Times New Roman"
BLUE_RULE = "1F4E79"

doc = Document()

# ------------------------------------------------------------
# Page setup, base style, footer "Page N"
# ------------------------------------------------------------

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(2.0), Cm(2.0)
sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.0)
sec.footer_distance = Cm(1.0)

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.15


def add_field(run, instr):
    for tag, text in [("begin", None), (None, instr), ("separate", None), ("end", None)]:
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = fp.add_run("Page ")
r2 = fp.add_run()
add_field(r2, "PAGE")
for run in (r, r2):
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x7F, 0x7F, 0x7F)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def para(text="", size=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         before=0, after=6, spacing=None, underline=False):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if spacing:
        p.paragraph_format.line_spacing = spacing
    if text:
        add_rich(p, text, size, bold, italic, underline)
    return p


def add_rich(p, text, size=12, bold=False, italic=False, underline=False):
    """Text with **bold** segments."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        run = p.add_run(part)
        run.font.size = Pt(size)
        run.bold = bold or (i % 2 == 1)
        run.italic = italic
        run.underline = underline
    return p


def heading(text, size=14, before=10, after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = para(text, size=size, bold=True, align=align, before=before, after=after)
    p.paragraph_format.keep_with_next = True
    return p


def sub(text):
    return heading(text, size=12, before=8, after=2)


def numbered(items, bullet=False):
    for i, item in enumerate(items, 1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        p.paragraph_format.space_after = Pt(2)
        add_rich(p, ("•\t" if bullet else f"{i}.\t") + item)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(1.27))


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def rule(p, where="bottom"):
    pPr = p._p.get_or_add_pPr()
    bdr = pPr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = OxmlElement("w:pBdr")
        pPr.append(bdr)
    el = OxmlElement(f"w:{where}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), "12")
    el.set(qn("w:space"), "8")
    el.set(qn("w:color"), BLUE_RULE)
    bdr.append(el)


def banner():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(ASSETS, "assets_banner.png"), width=Cm(17.0))
    p.paragraph_format.space_after = Pt(14)


FIG_NO = [0]
TAB_NO = [0]


def figure(name, caption, width=15.5):
    FIG_NO[0] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, name), width=Cm(width))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(6)
    r = c.add_run(f"Figure {FIG_NO[0]}: ")
    r.bold = True
    r = c.add_run(caption)
    r.italic = True


def set_cell_border(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "BFBFBF")
        borders.append(el)
    tblPr.append(borders)


def table(caption, header, rows, widths=None, center_cols=()):
    TAB_NO[0] += 1
    cp = para(f"Table {TAB_NO[0]}: {caption}", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
              before=6, after=2)
    cp.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_cell_border(t)
    for i, row in enumerate([header] + rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            if j in center_cols and i > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.size = Pt(12 if len(header) <= 4 else 11)
            run.bold = i == 0
            if widths:
                cell.width = Cm(widths[j])
    para(after=4)
    return t


def fmt(x, d=2):
    return f"{x:,.{d}f}"


# ============================================================
# PAGE 1 - COVER
# ============================================================

banner()
para("C O U R S E - E N D   P R O J E C T   R E P O R T", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("O n", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)
p = para(TITLE, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=10)
rule(p, "top")
rule(p, "bottom")
p = para("Submitted to fulfill the requirements for the Award of CIE Marks (10) for the "
         "B.E.(IT), III-SEM,", align=WD_ALIGN_PARAGRAPH.CENTER, before=10, after=0)
p = para("Couse: **Exploratory Data Analysis & Visualization - EDAV (22ADC31N)**",
         align=WD_ALIGN_PARAGRAPH.CENTER, after=10)
para("By", align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para(f"{STUDENT}        {ROLL}", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
para("Under the guidance of", bold=True, underline=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("Dr Ramakrishna Kolikipogu, Ph.D(CSE), SMIEEE", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("Professor, Dept. Of IT, CBIT", align=WD_ALIGN_PARAGRAPH.CENTER, after=24)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(os.path.join(ASSETS, "assets_logo.png"), width=Cm(4.8))
p.paragraph_format.space_after = Pt(24)
para("CHAITANYA BHARATHI INSTITUTE OF TECHNOLOGY (CBIT)", size=14, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("DEPARTMENT OF INFORMATION TECHNOLOGY (IT)", size=14, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("KOKAPET (V), GANDIPETA, RANGA REDDY, HYDERABAD – 500075",
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("www.cbit.ac.in", underline=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
para("A.Y: 2026-27", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
page_break()

# ============================================================
# PAGE 2 - CERTIFICATE
# ============================================================

banner()
para("CERTIFICATE", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
para("This is to certify that the course-end project report entitled "
     f"**“{TITLE}”** is a bonafide record of the work carried out by "
     f"**{STUDENT}({ROLL})**, in partial fulfilment of the requirements of the course "
     "**Exploratory Data Analysis and Visualization (22ADC31N)**  of the programme "
     "**B.E(IT), III-SEM**, during the academic year **2026–2027**.",
     spacing=1.5, after=12)
para("The project was carried out under my guidance and supervision. To the best of my "
     "knowledge, the work reported here is original and has not been submitted to any other "
     "institution or university for the award of any degree, diploma or certificate.",
     spacing=1.5, after=6)
para("**Place:** Hyderabad", spacing=1.5, after=0)
para("**Date:** ___/___/_____", spacing=1.5, after=30)
para("Course Faculty", align=WD_ALIGN_PARAGRAPH.RIGHT, spacing=1.5, after=6)
para("(Prof Ramakrishna Kolikipogu)", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, spacing=1.5)
page_break()

# ============================================================
# PAGE 3 - DECLARATION
# ============================================================

banner()
para("DECLARATION", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=12, after=6)
para(f"I hereby declare that the project report entitled “{TITLE}” submitted to Dept of IT, "
     "CBIT is a record of original work done by me under the guidance of Dr Ramakrishna "
     "Kolikipogu, Professor, IT, CBIT.", spacing=1.5, after=6)
para("The data used was taken from the public healthcare facility register of Telangana and "
     "Census-based district demographic data; all external sources, tools and libraries have "
     "been acknowledged in the References. This work has not been submitted, in part or in "
     "full, for any other course, degree or diploma.", spacing=1.5, after=18)
para("Place: Hyderabad", spacing=1.5, after=12)
para("Date: ___/___/_____", spacing=1.5, after=40)
para("Signature of the Student", align=WD_ALIGN_PARAGRAPH.RIGHT, after=0)
para(f"{STUDENT} ({ROLL})", align=WD_ALIGN_PARAGRAPH.RIGHT)
page_break()

# ============================================================
# PAGE 4 - ACKNOWLEDGEMENT
# ============================================================

para("ACKNOWLEDGEMENT", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
para("I express my sincere gratitude to my project guide and course faculty, Prof Ramakrishna "
     "Kolikipogu, IT, CBIT, for valuable guidance, encouragement and constructive feedback "
     "throughout this project. I thank the Head of the Department, the faculty members and the "
     "management of Chaitanya Bharathi Institute of Technology (CBIT) for providing the "
     "facilities and the learning environment that made this work possible.", spacing=1.5)
para("I am also grateful to the open-source community behind Python, pandas, Matplotlib, "
     "Seaborn, Plotly, scikit-learn, GeoPy and Streamlit, and to the publishers of the "
     "Telangana healthcare facility register and the Census of India, without which this "
     "analysis would not have been possible. Finally, I thank my family and friends for their "
     "constant support.", spacing=1.5, after=12)
para(STUDENT, bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)
page_break()

# ============================================================
# PAGE 5 - CONTENTS
# ============================================================

CONTENTS = [
    ("1", "Abstract"), ("2", "Introduction"), ("3", "Problem Statement and Objectives"),
    ("4", "Dataset Description"), ("5", "Methodology and Tools"),
    ("6", "Data Quality Assessment and Cleaning"), ("7", "Exploratory Data Analysis"),
    ("8", "Geospatial Visualization and Spatial Analytics"), ("9", "Key Findings"),
    ("10", "Recommendations"), ("11", "Limitations"), ("12", "Conclusion"),
    ("13", "Future Scope"), ("", "References"), ("", "Appendix A – Project Source Code"),
    ("", "Appendix B – How to Run"),
]
para("Contents", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
t = doc.add_table(rows=1 + len(CONTENTS), cols=3)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.style = "Table Grid"
for i, (no, item) in enumerate([("S.No.", "Item")] + CONTENTS):
    vals = [no, item, "Page No" if i == 0 else str(PAGES.get(item, ""))]
    for j, v in enumerate(vals):
        c = t.cell(i, j)
        c.width = Cm([2.2, 11.0, 2.8][j])
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        if j != 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(v)
        run.bold = True if (i == 0 or j < 2) else False
page_break()

# ============================================================
# PAGE 6 - ABSTRACT
# ============================================================

rus = S["rural_urban_share"]
para("Abstract", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=18, after=18)
para("Access to hospitals, beds and doctors is one of the most basic determinants of health, "
     "yet healthcare infrastructure in India is unevenly spread between cities and villages and "
     "between districts. This project, **HealthInfraAI**, analyses the public healthcare "
     f"facility register of Telangana ({S['raw_rows']:,} facilities across all 33 districts) "
     "together with district demographic data (population, rural/urban split, households) to "
     "understand how healthcare capacity is distributed across the state and where it is "
     "thin.", spacing=1.5, after=12)
para("The work follows an end-to-end data-science workflow in Python: a data-quality audit, "
     "harmonisation of pre-2021 district names, construction of a district master table, "
     "Exploratory Data Analysis (EDA) with population-adjusted indicators, geospatial mapping "
     "of facility coordinates, nearest-hospital distance analysis, K-Means clustering of "
     "districts, a Random Forest model of bed capacity, and an interactive Streamlit dashboard "
     "with a facility search tool.", spacing=1.5, after=12)
para(f"**Main results.** Telangana’s {S['raw_rows']:,} public facilities serve about "
     f"{S['population']/1e7:.2f} crore people. Sub-centres alone make up "
     f"{S['type_counts']['SubCentre']/S['raw_rows']*100:.0f}% of the register, so "
     f"{rus['Facilities']['Rural']:.0f}% of facilities are rural although only "
     f"{rus['Population']['Rural']:.0f}% of people are. Capacity is the reverse: an "
     f"estimated {rus['Hospital beds (est.)']['Urban']:.0f}% of beds and "
     f"{rus['Doctors (est.)']['Urban']:.0f}% of doctors are in urban areas, giving "
     f"{S['urban_beds_per_1000']:.2f} beds per 1,000 people in towns against "
     f"{S['rural_beds_per_1000']:.2f} in villages. Hyderabad has the most beds per head "
     f"({S['Beds_per_1000']['top']['Hyderabad']:.2f}) and Jayashankar Bhupalpally the fewest "
     f"({S['Beds_per_1000']['bottom']['Jayashankar Bhupalpally']:.2f}). A sub-centre or PHC "
     f"is a median {S['nn_median']} km from the nearest bedded facility, rising to "
     f"{S['nn_district_worst']['Jogulamba Gadwal']} km in Jogulamba Gadwal. K-Means separates "
     "the districts into three clear groups: 28 largely rural districts, four urban-fringe "
     "districts and Hyderabad.", spacing=1.5, after=12)
para("**Keywords:** healthcare infrastructure; exploratory data analysis; geospatial "
     "visualization; Telangana; rural–urban gap; K-Means; Random Forest; Streamlit.",
     spacing=1.5)
page_break()

# ============================================================
# 1. INTRODUCTION
# ============================================================

heading("1. Introduction", before=0)
para("Healthcare infrastructure – facilities, hospital beds and doctors – decides how far a "
     "patient must travel and how long they must wait for care. India organises public care "
     "in tiers: Sub-Centres (SC) at village level, Primary Health Centres (PHC) for groups of "
     "villages, Community Health Centres (CHC) at block level, and Area, District and Teaching "
     "hospitals in towns. Urban areas additionally have Urban PHCs and Basti Dawakhanas "
     "(urban health and wellness centres) and most of the private hospitals.")
para("Telangana, formed in 2014 and reorganised into 33 districts in 2016–2021, provides a "
     "useful case study: it combines one of India’s largest medical hubs (Hyderabad) with "
     "forested, tribal and agricultural districts. Raw counts of facilities can be misleading "
     "here – a district with many small sub-centres may still have very few hospital beds – "
     "so the project emphasises population-adjusted indicators and capacity rather than "
     "counts alone. It also requires every stage of a real analysis: auditing, harmonising "
     "names, merging, exploring, mapping and modelling.")

heading("2. Problem Statement and Objectives")
para("**Problem statement.** To describe and visualise how healthcare infrastructure varies "
     "across the districts of Telangana and between rural and urban areas, and to identify "
     "where capacity is concentrated, thin or far away.")
sub("2.1 Objectives")
numbered([
    "Audit the facility register and demographic data and document their quality problems.",
    "Clean, harmonise and merge the data into an analysis-ready district master table.",
    "Perform EDA on counts, population-adjusted indicators, rural–urban distribution and "
    "inequality of provision.",
    "Map facility locations and measure distance from primary facilities to the nearest "
    "hospital.",
    "Apply machine learning: K-Means clustering of districts and Random Forest regression of "
    "bed capacity.",
    "Build an interactive dashboard and derive evidence-based findings and recommendations.",
])
sub("2.2 Research questions")
numbered([
    "Which districts have the most and fewest facilities, beds and doctors, and is provision "
    "proportional to population?",
    "Why do rural areas have more facilities than urban areas, and does this hold for beds "
    "and doctors?",
    "How unequal is bed provision across districts?",
    "How far are village-level facilities from a hospital, and which districts are most "
    "remote?",
    "Which districts share a similar infrastructure profile?",
], bullet=True)

heading("3. Dataset Description")
para("The analysis integrates three sources stored in the project’s data folder. The main "
     f"source is the facility register geolocation.csv, with {S['raw_rows']:,} rows (one row "
     "per public healthcare facility) and 14 columns covering all 33 districts. It is joined "
     "to Demographics.csv (33 districts × 9 columns: males, females, sex ratio, rural and "
     "urban population, households) and to a district infrastructure table, Hospitals.csv "
     "(33 × 13). A small directory of 37 major hospitals (major_hospitals.csv) supports the "
     "search feature of the dashboard.")
table("Columns of the facility register (geolocation.csv)",
      ["Column", "Type", "Description"], [
          ["id", "Number", "Serial number added during cleaning"],
          ["State, District, Taluka", "Text", "Administrative location (33 districts; mandal "
                                              "name for Taluka)"],
          ["Facility Name", "Text", "Official name, e.g. “Community Health Centre, Utnoor”"],
          ["Facility Type", "Text", f"One of {S['clean_types']} types (SubCentre, PHC, CHC, "
                                    "UPHC, District Hospital …)"],
          ["Latitude, longitude", "Number", "Coordinates of the facility (decimal degrees)"],
          ["Street, Landmark, Locality", "Text", "Address details (partially filled)"],
          ["Region Indicator", "Text", "Rural or Urban"],
          ["Operational Status", "Text", "Functional status of the facility"],
          ["Ownership Authority", "Text", "State Government, Private, Central Government …"],
      ], widths=[4.6, 2.2, 10.2])

heading("4. Methodology and Tools")
para("The project follows a seven-step pipeline: (1) load and inspect, (2) audit data "
     "quality, (3) clean, harmonise and merge into a district master table, (4) EDA, "
     "(5) geospatial mapping and distance analysis, (6) machine learning, and (7) an "
     "interactive dashboard and synthesis of findings. Each step is a Python script "
     "(build_data.py → eda.py → ml.py → app.py) so that results are reproducible.")
table("Tools used", ["Purpose", "Library"], [
    ["Data handling", "pandas, NumPy"],
    ["Static charts", "Matplotlib, Seaborn"],
    ["Interactive charts", "Plotly Express"],
    ["Machine learning", "scikit-learn (K-Means, Random Forest)"],
    ["Distance calculation", "GeoPy (geodesic), haversine formula"],
    ["Dashboard / front-end", "Streamlit"],
], widths=[7.0, 10.0])
para("Key technical choices: a mapping dictionary converts pre-2021 district names to the "
     "current 33 districts; facility counts per district and type are built with crosstabs; "
     "indicators are normalised per 1,000 or per 100,000 people; beds and doctors are "
     "estimated from Indian Public Health Standards (IPHS) norms per facility type plus a "
     "private-sector component; and distances are computed with the haversine formula.")

heading("5. Data Quality Assessment and Cleaning")
para("Auditing before analysing revealed several issues. They are summarised in Table 3, "
     "together with the treatment adopted. A guiding rule was never to fill silently: every "
     "estimate is labelled as an estimate in the report and the dashboard.")
m = S["raw_missing"]
table("Data-quality issues and treatment", ["Issue", "Evidence", "Treatment"], [
    ["Old district names", "Register uses pre-2021 names (Warangal Urban, Warangal Rural, "
     "Jangoan, Jagitial, Mahbubnagar …); 8 names do not match the demographic table",
     "Mapping dictionary to current names (Warangal Urban → Hanumakonda, Warangal Rural → "
     "Warangal)"],
    ["Missing region tag", f"{m['Region Indicator']} facilities have no Rural/Urban value",
     "Assigned by facility type: SC, PHC and CHC → Rural, others → Urban"],
    ["Missing / wrong coordinates", f"{m['Latitude']} rows lack latitude and longitude; "
     f"{S['dropped_coords'] - m['Latitude']} more fall outside Telangana",
     "Kept in all counts, excluded only from maps and distance analysis"],
    ["Inconsistent labels", "“Unani  dispensary” (double space); 9 ownership labels incl. "
     f"“Hospital”; {m['Ownership Authority']} blank ownership",
     "Whitespace normalised; blanks set to “Unknown”"],
    ["No capacity data", "Register lists facilities only – no beds or doctors",
     "Estimated from IPHS norms per type plus a private share; labelled “(est.)”"],
    ["Census pre-dates districts", "Census 2011 has 10 districts; populations of Mulugu, "
     "Narayanpet, Hanumakonda and Warangal are rounded estimates", "Used as given and listed "
     "as a limitation"],
    ["Placeholder data in an earlier version", "Doctors per 100,000 nearly identical (5–7) "
     "in every district; rural/urban tags random", "Replaced with the real register; old "
     "files backed up"],
], widths=[3.8, 7.0, 6.2])
para("After cleaning, the data was reshaped into three working tables: the cleaned facility "
     "register (one row per facility), a district master table (33 rows, 36 columns including "
     "the population-adjusted indicators) and a district–cluster table produced by the "
     "machine-learning step.")

# ============================================================
# 6. EDA
# ============================================================

fd = S["fac_desc"]
heading("6. Exploratory Data Analysis")
sub("6.1 Facilities by district")
para(f"The register records {S['raw_rows']:,} facilities across 33 districts: mean "
     f"{fd['mean']:.0f}, median {fd['50%']:.0f}, standard deviation {fd['std']:.0f}, minimum "
     f"{fd['min']:.0f} (Narayanpet) and maximum {fd['max']:.0f} (Rangareddy) per district.")
figure("fig01_facilities.png", "Public healthcare facilities by district.", width=14)
para("Large, mostly rural districts – Rangareddy, Nalgonda, Sangareddy, Nizamabad and "
     "Bhadradri Kothagudem – have the most facilities. Hyderabad, despite having over 39 lakh "
     "people (more than twice any other district), ranks only sixth, because a city is served "
     "by fewer but much larger hospitals rather than by many village sub-centres.")

sub("6.2 Composition by facility type")
tc = S["type_counts"]
figure("fig02_types.png", "Facility register by facility type (log scale).", width=14.5)
para(f"Sub-centres ({tc['SubCentre']:,}) and PHCs ({tc['Primary Health Centre']:,}) make up "
     f"{(tc['SubCentre'] + tc['Primary Health Centre'])/S['raw_rows']*100:.0f}% of all "
     f"facilities. By contrast there are only {tc['Community Health Center']} CHCs, "
     f"{tc['Sub-District Hospital']} area hospitals, {tc['District Hospital']} district "
     f"hospitals and {tc['Medical Colleges Hospital']} medical-college hospitals. Counting "
     "facilities therefore mostly counts small village clinics with no beds.")

sub("6.3 Provision relative to population")
b, dct = S["Beds_per_1000"], S["Doctors_per_100000"]
para("Raw counts are unfair across districts of very different size, so beds were divided "
     "by population (per 1,000 people) and doctors per 100,000 people. Statewide there are "
     f"about {S['beds_per_1000_state']:.2f} beds per 1,000 and "
     f"{S['doctors_per_100k_state']:.0f} doctors per 100,000 people.")
figure("fig03_per_capita.png", "Hospital beds per 1,000 and doctors per 100,000 population "
       "by district (dashed line = median).", width=16)
bt, bb = list(b["top"].items()), list(b["bottom"].items())[::-1]
table("Best- and least-served districts (beds per 1,000 people)",
      ["Best served", "Beds / 1,000", "Least served", "Beds / 1,000"],
      [[bt[i][0], fmt(bt[i][1]), bb[i][0], fmt(bb[i][1])] for i in range(5)],
      widths=[4.8, 3.6, 4.8, 3.6], center_cols=(1, 3))
para(f"Hyderabad ({b['top']['Hyderabad']:.2f} beds, {dct['top']['Hyderabad']:.0f} doctors) "
     "is far ahead because it hosts most teaching and private hospitals. Warangal and "
     "Hanumakonda follow (MGM and CKM teaching hospitals in Warangal city), and Adilabad "
     "ranks fifth because of RIMS Medical College Hospital. The least served are forested "
     "and tribal districts – Jayashankar Bhupalpally, Kumuram Bheem, Jogulamba Gadwal and "
     "Mahabubabad – with roughly one bed per 1,000 people, a quarter of Hyderabad’s level.")

sub("6.4 Population versus bed capacity")
figure("fig04_pop_beds.png", "Population vs hospital beds (bubble size = urban population %).",
       width=14)
para(f"Beds rise with population (r = {S['pop_beds_corr']}), but the more urban districts "
     "(larger bubbles) sit above the trend and the rural districts below it: urbanisation, "
     "not just population, drives bed capacity.")

sub("6.5 Rural versus urban provision")
table("Rural and urban shares of population and healthcare capacity",
      ["Measure", "Rural (%)", "Urban (%)"],
      [[k, f"{v['Rural']:.1f}", f"{v['Urban']:.1f}"] for k, v in rus.items()],
      widths=[7.0, 4.0, 4.0], center_cols=(1, 2))
figure("fig05_rural_urban.png", "Rural vs urban share of population, facilities, beds and "
       "doctors.", width=15)
para(f"This is the central result of the project. Rural areas hold {rus['Facilities']['Rural']:.0f}% "
     f"of facilities – because every 3,000–5,000 villagers are served by a sub-centre – but "
     f"only about {rus['Hospital beds (est.)']['Rural']:.0f}% of beds and "
     f"{rus['Doctors (est.)']['Rural']:.0f}% of doctors. Per head, an urban resident has "
     f"{S['urban_beds_per_1000']:.2f} beds per 1,000 against {S['rural_beds_per_1000']:.2f} for "
     f"a rural resident (about {S['urban_beds_per_1000']/S['rural_beds_per_1000']:.0f}×), and "
     f"{S['urban_docs_per_100k']:.0f} doctors per 100,000 against {S['rural_docs_per_100k']:.0f}. "
     "More facilities in villages does not mean more care.")

sub("6.6 Inequality of provision")
figure("fig06_lorenz.png", "Lorenz curve of hospital beds across districts (sorted by beds "
       "per 1,000).", width=10)
para(f"The Gini coefficient of beds against population is {S['gini_beds']}, indicating mild "
     "to moderate inequality at district level. District averages hide the much larger "
     "rural–urban gap within districts shown in Section 6.5.")

sub("6.7 Correlation analysis")
cr = S["corr"]
figure("fig07_corr.png", "Correlation matrix of healthcare infrastructure indicators.",
       width=14)
para(f"Beds are strongly correlated with teaching hospitals "
     f"(r = {cr['Beds in all Hospitals']['Teaching Hospitals']}) and urban population share "
     f"(r = {cr['Beds in all Hospitals']['Urban Population (%)']}), but negatively with "
     f"sub-centres (r = {cr['Beds in all Hospitals']['Health Sub-Centres']}) and PHCs "
     f"(r = {cr['Beds in all Hospitals']['Primary Health Centres']}). Districts with many "
     "village clinics are the ones with fewest beds, confirming that facility counts and "
     "capacity measure different things.")

# ============================================================
# 7. GEOSPATIAL
# ============================================================

heading("7. Geospatial Visualization and Spatial Analytics")
sub("7.1 Coordinates")
para(f"Unlike many public datasets, the register already contains latitude and longitude for "
     f"almost every facility, so no geocoding was needed. Of {S['raw_rows']:,} facilities, "
     f"{S['mapped_points']:,} have valid coordinates inside Telangana; "
     f"{S['dropped_coords']} were excluded from maps (missing or outside the state) but kept "
     "in all counts.")
sub("7.2 Point map of facility locations")
figure("fig08_map.png", f"Public healthcare facility locations, Telangana "
       f"({S['mapped_points']:,} points). Triangles mark hospitals.", width=14)
para("Even without district boundaries the outline of Telangana is visible. Rural facilities "
     "(blue) cover the state almost uniformly, reflecting the population-based placement of "
     "sub-centres. Urban facilities (orange) and hospitals (red) cluster tightly in Hyderabad "
     "and Warangal, with smaller nodes at district headquarters. The forested north-east "
     "(Bhadradri Kothagudem, Mulugu, Jayashankar Bhupalpally) and the south-west (Jogulamba "
     "Gadwal, Narayanpet) have few hospital triangles.")
sub("7.3 Interactive dashboard")
para("The Streamlit application (app.py) presents the same analysis interactively: "
     "(i) a Home page with headline figures; (ii) Healthcare Analytics with capacity, "
     "population-adjusted and rural/urban tabs (Plotly charts); (iii) a District Explorer "
     "that profiles any one district; (iv) ML Insights showing the clusters; and (v) a Find "
     "Healthcare tool that filters major hospitals and public facilities by district, type, "
     "ownership, service and region, and sorts them by geodesic distance from the user.")
sub("7.4 Access: distance to the nearest bedded facility")
para(f"For each of the {S['n_primary']:,} sub-centres and PHCs, the great-circle (haversine) "
     f"distance to the nearest of the {S['n_bedded']} bedded facilities (CHC, area, district, "
     f"women’s or teaching hospital) was computed. The median is {S['nn_median']} km and the "
     f"mean {S['nn_mean']} km; {S['nn_over_20']}% of primary facilities are more than 20 km "
     "from a bedded facility.")
nw = list(S["nn_district_worst"].items())
table("Districts where primary facilities are furthest from a bedded facility",
      ["District", "Median distance (km)"], [[k, f"{v:.1f}"] for k, v in nw],
      widths=[8.0, 6.0], center_cols=(1,))
figure("fig09_distance.png", "Distribution of distance from sub-centres/PHCs to the nearest "
       "CHC or hospital.", width=14)
para("Remoteness is greatest in Jogulamba Gadwal, Kumuram Bheem, Jangaon and Mahabubabad, "
     f"and lowest in Hyderabad ({S['nn_district_best']['Hyderabad']} km) and "
     f"Medchal-Malkajgiri ({S['nn_district_best']['Medchal-Malkajgiri']} km). Several of the "
     "remote districts are also among the least served by beds per head (Section 6.3), so "
     "their residents face both lower capacity and longer travel.")

sub("7.5 K-Means district clusters")
cl = S["clusters"]
para("K-Means was applied to four standardised indicators – beds per 1,000, doctors per "
     "100,000, facilities per 100,000 and the rural share of facilities. The elbow method "
     "supported k = 3.")
table("K-Means district clusters (k = 3)",
      ["Cluster", "Districts", "Beds / 1,000", "Doctors / 100k", "Rural fac. %"],
      [[f"{k} – {['Rural', 'Urban fringe', 'Metro'][int(k)]}", v["Districts"],
        fmt(v["Beds_per_1000"]), f"{v['Doctors_per_100000']:.1f}",
        f"{v['Rural_Facility_Percent']:.1f}"] for k, v in cl.items()],
      widths=[4.2, 2.4, 3.2, 3.4, 3.2], center_cols=(1, 2, 3, 4))
figure("fig10_kmeans.png", "Elbow method (left) and K-Means district clusters (right).",
       width=16.5)
para(f"Cluster 0 (28 districts) is the rural majority: about {cl['0']['Beds_per_1000']:.1f} "
     f"beds per 1,000 and {cl['0']['Rural_Facility_Percent']:.0f}% rural facilities. Cluster 1 "
     f"is the urban fringe – {cl['1']['Members']} – with twice the bed density. Cluster 2 is "
     "Hyderabad alone, a clear outlier on every indicator.")

sub("7.6 Random Forest model of bed capacity")
imp = list(S["rf_importance"].items())
para(f"A Random Forest regressor (300 trees) was trained to predict district bed capacity "
     f"from population and facility counts ({S['rf_train']} training and {S['rf_test']} test "
     f"districts). On the test set it achieved MAE = {S['rf_mae']:,.0f} beds, RMSE = "
     f"{S['rf_rmse']:,.0f} beds and R² = {S['rf_r2']}. The most important features were "
     f"{imp[0][0].lower()} ({imp[0][1]:.2f}) and {imp[1][0].lower()} ({imp[1][1]:.2f}).")
figure("fig11_rf.png", "Random Forest feature importance (left) and actual vs predicted "
       "beds (right).", width=16.5)
para("With only 33 districts the model is a demonstration rather than a forecasting tool: a "
     "moderate R² on seven test districts is expected. Its value is in confirming which "
     "factors explain capacity – doctors and population – while counts of sub-centres add "
     "little.")

# ============================================================
# 8 - 12
# ============================================================

heading("8. Key Findings")
numbered([
    f"Telangana’s register lists {S['raw_rows']:,} public healthcare facilities in 33 "
    f"districts; {(tc['SubCentre'] + tc['Primary Health Centre'])/S['raw_rows']*100:.0f}% are "
    "sub-centres or PHCs.",
    f"Rural areas have {rus['Facilities']['Rural']:.0f}% of facilities but only about "
    f"{rus['Hospital beds (est.)']['Rural']:.0f}% of beds and "
    f"{rus['Doctors (est.)']['Rural']:.0f}% of doctors; urban residents have about "
    f"{S['urban_beds_per_1000']/S['rural_beds_per_1000']:.0f}× as many beds per head.",
    f"Hyderabad leads with {b['top']['Hyderabad']:.2f} beds per 1,000 and "
    f"{dct['top']['Hyderabad']:.0f} doctors per 100,000; Jayashankar Bhupalpally is lowest "
    f"({b['bottom']['Jayashankar Bhupalpally']:.2f} beds, "
    f"{dct['bottom']['Jayashankar Bhupalpally']:.0f} doctors).",
    f"Beds track population (r = {S['pop_beds_corr']}) and teaching hospitals, and are "
    "negatively related to the number of sub-centres.",
    f"District-level inequality of beds is moderate (Gini = {S['gini_beds']}).",
    f"Primary facilities are a median {S['nn_median']} km from a bedded facility; "
    f"{S['nn_over_20']}% are over 20 km away, mostly in Jogulamba Gadwal, Kumuram Bheem, "
    "Jangaon and Mahabubabad.",
    "K-Means identifies three profiles: 28 rural districts, four urban-fringe districts "
    "and Hyderabad.",
    "Data caveats: beds and doctors are estimates, some district populations are rounded, "
    f"and {S['dropped_coords']} facilities lack usable coordinates.",
])
heading("9. Recommendations")
numbered([
    "**Strengthen the middle tier.** Upgrade selected PHCs to 30-bed CHCs in the remote, "
    "low-bed districts (Jayashankar Bhupalpally, Kumuram Bheem, Jogulamba Gadwal, "
    "Mahabubabad) to cut both travel distance and the bed gap.",
    "**Measure capacity, not counts.** Plan and report with beds and doctors per head; "
    "facility counts overstate rural provision.",
    "**Target long-distance catchments.** Use the distance analysis to locate new CHCs or "
    "ambulance bases where primary facilities are more than 20 km from a hospital.",
    "**Extend specialist reach.** Link district hospitals to Hyderabad’s teaching hospitals "
    "through tele-consultation, since doctors are concentrated in the capital.",
    "**Publish better data.** Add sanctioned and functional beds, doctors in position, "
    "and up-to-date populations for the new districts to the register.",
])
heading("10. Limitations")
numbered([
    "Beds and doctors are not in the register; they are estimated from IPHS norms and a "
    "private-sector share, so they show the pattern rather than exact values.",
    "Population figures are Census 2011 based; four new districts use rounded estimates.",
    "The register covers public facilities; private clinics and hospitals are only "
    "represented through the estimate and the small major-hospital directory.",
    "Distances are straight-line, not road travel times, and no boundary polygons are used.",
    "With 33 districts the machine-learning models are illustrative.",
], bullet=True)
heading("11. Conclusion")
para("Healthcare infrastructure in Telangana is plentiful in number but uneven in capacity. "
     "Villages are well covered by small sub-centres and PHCs, which is why rural areas have "
     "more facilities than urban ones, but beds and doctors are concentrated in Hyderabad and "
     "the urban fringe. Combining EDA, population-adjusted indicators, geospatial distance "
     "analysis and clustering turns a 7,001-row facility list into practical planning "
     "insight: it shows which districts are short of beds, which primary facilities are far "
     "from a hospital, and which districts share a profile. The project also showed the value "
     "of auditing data first – checking district names, regions and placeholder values "
     "changed the conclusions of the analysis.")
heading("12. Future Scope")
numbered([
    "Add official district boundary files and build choropleth maps of beds per head.",
    "Replace estimated beds and doctors with actual figures from the Health, Medical & "
    "Family Welfare Department and private hospital registries.",
    "Use road-network travel times (e.g. OpenStreetMap) instead of straight-line distance.",
    "Add utilisation data (OPD visits, bed occupancy) to move from availability to demand.",
    "Use population projections for 2026 and age-specific needs (maternal, elderly care).",
    "Deploy the Streamlit dashboard publicly for planners and citizens.",
], bullet=True)

heading("References")
numbered([
    "Office of the Registrar General & Census Commissioner, India. Census of India 2011 – "
    "Primary Census Abstract (district-wise population).",
    "Telangana health facility register with geo-locations (geolocation.csv).",
    "Ministry of Health & Family Welfare, Government of India. Indian Public Health Standards "
    "(IPHS) Guidelines, 2022.",
    "The pandas development team. pandas documentation. https://pandas.pydata.org",
    "Hunter, J. D. Matplotlib documentation. https://matplotlib.org",
    "Waskom, M. seaborn documentation. https://seaborn.pydata.org",
    "Plotly Python documentation. https://plotly.com/python",
    "Pedregosa, F. et al. Scikit-learn: Machine Learning in Python. Journal of Machine "
    "Learning Research 12, 2011. https://scikit-learn.org",
    "GeoPy documentation. https://geopy.readthedocs.io",
    "Streamlit documentation. https://docs.streamlit.io",
])

# ============================================================
# APPENDICES
# ============================================================

heading("Appendix A – Project Source Code")
para("The project consists of the following Python files. The data-preparation and "
     "machine-learning scripts are reproduced below; app.py (Streamlit dashboard, about "
     "1,400 lines) is submitted with the project files.")
table("Project files", ["File", "Purpose"], [
    ["build_data.py", "Cleans the facility register and builds the district master table"],
    ["eda.py", "Exploratory data analysis and charts"],
    ["ml.py", "Random Forest bed model and K-Means district clustering"],
    ["recommendation.py", "Facility search and distance-based recommendation"],
    ["app.py", "Streamlit dashboard"],
], widths=[4.5, 12.5])


def code_listing(path, title):
    sub(title)
    for line in open(os.path.join(ROOT, path), encoding="utf-8").read().rstrip().split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line if line else " ")
        r.font.name = "Courier New"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
        r.font.size = Pt(8)


code_listing("build_data.py", "A.1 build_data.py")
code_listing("ml.py", "A.2 ml.py")

heading("Appendix B – How to Run")
sub("B.1 Running the project")
numbered([
    "Install the libraries: pip install pandas numpy matplotlib seaborn plotly "
    "scikit-learn geopy streamlit",
    "Keep the data folder (and data_old for the raw register) next to the scripts.",
    "Run python build_data.py, then python eda.py, then python ml.py to rebuild the master "
    "table, charts and clusters.",
    "Start the dashboard with streamlit run app.py and open http://localhost:8501 in a "
    "browser.",
])

doc.save(OUT)
print("Saved", OUT)
