import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pickle
import streamlit as st

import datetime

COVID_AVG = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv"
COVID_HOSP = "https://healthdata.gov/resource/g62h-syeh.csv"
INFEC_DIS = "data/health-infectious-disease-2001-2014/rows.csv"


def map_us_abbrev(state: str):

    with open("data/states_dict.pickle", "rb") as filehandle:
        states_dict = pickle.load(filehandle)

    state_abbrev = states_dict[state]
    if state_abbrev is not None:
        return state_abbrev

    return None


def covid_avg(state: str):

    covid_avg = pd.read_csv(COVID_AVG)

    covid_avg["date"] = pd.to_datetime(covid_avg["date"])

    past_day_case = covid_avg[
        covid_avg.date > datetime.datetime.now() - pd.to_timedelta("90day")
    ]

    state_data = past_day_case.groupby(["state"]).filter(
        lambda x: (x["state"] == state).any()
    )

    fig = make_subplots(rows=2, cols=1)

    fig.add_trace(
        go.Scatter(
            x=state_data["date"], y=state_data["cases_avg"], name="Daily Avg Cases"
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=state_data["date"], y=state_data["deaths_avg"], name="Daily Avg Deaths"
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=0.75),
        height=600,
        width=700,
        title_text="Daily average cases and deaths",
    )

    latest_case = state_data["cases_avg"].iloc[-1]
    before_14_case = state_data["cases_avg"].iloc[-15]
    latest_death = state_data["deaths_avg"].iloc[-1]
    before_14_death = state_data["deaths_avg"].iloc[-15]

    cases_diff = latest_case - before_14_case
    past_14_case = round((cases_diff / before_14_case) * 100, 2)
    death_diff = latest_death - before_14_death
    past_14_death = round((death_diff / before_14_death) * 100, 2)
    stats = (latest_case, past_14_case, latest_death, past_14_death)

    return stats, fig


def hospitalization(state: str):

    covid_hosp = pd.read_csv(COVID_HOSP)
    covid_hosp["date"] = pd.to_datetime(covid_hosp["date"])

    abbrev_state = map_us_abbrev(state)

    state_hops = covid_hosp.groupby("state").filter(
        lambda x: (x["state"] == abbrev_state).any()
    )

    prev_day_confirmed = round(
        state_hops["previous_day_admission_adult_covid_confirmed"].iloc[-7:].mean(), 2
    )
    prev_day_suspected = round(
        state_hops["previous_day_admission_adult_covid_suspected"].iloc[-7:].mean(), 2
    )
    total_conf_sus = round(
        state_hops["total_adult_patients_hospitalized_confirmed_covid"]
        .iloc[-7:]
        .mean(),
        2,
    )

    state_covid = round(state_hops["inpatient_bed_covid_utilization"].mean(), 2)
    state_inf = round(
        state_hops["total_patients_hospitalized_confirmed_influenza"].mean(), 2
    )

    stats = (
        prev_day_confirmed,
        prev_day_suspected,
        total_conf_sus,
        state_covid,
        state_inf,
    )

    covid2 = covid_hosp.groupby("state").mean().reset_index()

    bed_state = px.bar(
        covid2,
        x="state",
        y="inpatient_bed_covid_utilization",
        labels={"state": "State", "inpatient_bed_covid_utilization": "Bed Utilization"},
        title="Hospitalization Bed efficiency by State (average)",
    )
    bed_state.update_layout(xaxis={"categoryorder": "total descending"})

    inf_bed_state = px.bar(
        covid2,
        x="state",
        y="total_patients_hospitalized_confirmed_influenza",
        labels={
            "state": "State",
            "total_patients_hospitalized_confirmed_influenza": "Counts",
        },
        title="Influenza Hospitalization by State (average)",
    )
    inf_bed_state.update_layout(xaxis={"categoryorder": "total descending"})

    covid3 = pd.melt(
        covid2,
        id_vars=[
            "state",
        ],
        value_vars=[
            "previous_day_admission_adult_covid_confirmed_18_19",
            # "previous_day_admission_adult_covid_confirmed_18_19_coverage",
            "previous_day_admission_adult_covid_confirmed_20_29",
            # "previous_day_admission_adult_covid_confirmed_20_29_coverage",
            "previous_day_admission_adult_covid_confirmed_30_39",
            # "previous_day_admission_adult_covid_confirmed_30_39_coverage",
            "previous_day_admission_adult_covid_confirmed_40_49",
            # "previous_day_admission_adult_covid_confirmed_40_49_coverage",
            "previous_day_admission_adult_covid_confirmed_50_59",
            # "previous_day_admission_adult_covid_confirmed_50_59_coverage",
            "previous_day_admission_adult_covid_confirmed_60_69",
            # "previous_day_admission_adult_covid_confirmed_60_69_coverage",
            "previous_day_admission_adult_covid_confirmed_70_79",
            # "previous_day_admission_adult_covid_confirmed_70_79_coverage",
            "previous_day_admission_adult_covid_confirmed_80",
            # "previous_day_admission_adult_covid_confirmed_80_coverage",
        ],
    )
    covid3["coverage"] = [
        "covered" if "coverage" in i.split("_") else "not covered"
        for i in covid3["variable"]
    ]
    covid3["variable"] = [
        "-".join(i.split("_")[-3:-1])
        if i.split("_")[-1] == "coverage"
        else "-".join(i.split("_")[-2:])
        for i in covid3["variable"]
    ]
    covid3["variable"] = [
        i.split("-")[-1] if i.split("-")[-2] == "confirmed" else i
        for i in covid3["variable"]
    ]

    us_state_to_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI",
    }

    bed_age = px.bar(
        covid3[covid3["state"] == us_state_to_abbrev[state]],
        x="variable",
        y="value",
        labels={"variable": "age group", "value": "Counts"},
        title="Hospitalization Bed efficiency by Age Group (" + state + ")",
    )

    return stats, bed_state, inf_bed_state, bed_age


def med_care():
    delay = pd.read_csv("data/med-delay.csv")

    # removing columns with only one unique value
    drop_heads = []

    for header in delay:
        if len(delay[header].value_counts()) == 1:
            drop_heads.append(header)
    delay = delay.drop(columns=drop_heads)

    # Drop flags because over 90% of it was missing
    delay = delay.drop(columns=["FLAG"])

    age_graph = delay.groupby("AGE").mean()

    reorderlist = [
        "Under 6 years",
        "6-17 years",
        "Under 18 years",
        "Under 19 years",
        "18-24 years",
        "19-25 years",
        "25-34 years",
        "35-44 years",
        "45-54 years",
        "45-64 years",
        "55-64 years",
        "65-74 years",
        "65 years and over",
        "75 years and over",
        "All ages",
    ]

    age_graph = age_graph.reindex(reorderlist)
    age_graph.reset_index(level=0, inplace=True)
    med_age = px.bar(
        age_graph,
        x="AGE",
        y="ESTIMATE",
        labels={"AGE": "Age Group (years)", "ESTIMATE": "Percentage"},
        title="Delay/Nonreceipt of Medical Care vs Age",
    )

    sex_df = delay[delay["STUB_NAME"] == "Sex (18-64 years)"]

    med_sex = px.bar(
        sex_df,
        x="YEAR",
        y="ESTIMATE",
        color="STUB_LABEL",
        barmode="group",
        labels={"STUB_LABEL": "Gender", "ESTIMATE": "Percentage", "YEAR": "Year"},
        title="Delay/Nonreceipt of Medical Care (due to cost) vs Gender",
    )

    loc_df = (
        delay[
            delay["STUB_NAME"]
            == "Health insurance status prior to interview (18-64 years)"
        ]
        .groupby("STUB_LABEL")
        .mean()
    )
    loc_df.reset_index(level=0, inplace=True)
    med_time = px.bar(
        loc_df,
        y="STUB_LABEL",
        x="ESTIMATE",
        orientation="h",
        labels={"STUB_LABEL": "Length of Insurance Held", "ESTIMATE": "Percentage"},
        title="Delay/Nonreceipt of Medical Care (due to cost) vs Insurance Time Duration",
    )

    loc_df = (
        delay[
            delay["STUB_NAME"]
            == "Health insurance status at the time of interview (18-64 years)"
        ]
        .groupby("STUB_LABEL")
        .mean()
    )
    loc_df.reset_index(level=0, inplace=True)
    med_type = px.bar(
        loc_df,
        x="STUB_LABEL",
        y="ESTIMATE",
        labels={"STUB_LABEL": "Type of Insurance Held", "ESTIMATE": "Percentage"},
        title="Delay/Nonreceipt of Medical Care (due to cost) vs Type of Insurance",
    )
    med_type.update_layout(xaxis={"categoryorder": "total descending"})

    return med_age, med_sex, med_time, med_type


def infec_dis():
    infec = pd.read_csv(INFEC_DIS)
    infec1 = (
        infec.groupby(["Sex", "Disease"])
        .mean()
        .reset_index()
        .sort_values(["Rate"], ascending=False)
    )
    infec2 = (
        infec.groupby("Disease")["Rate"]
        .mean()
        .reset_index()
        .sort_values("Rate", ascending=False)
        .head(15)
    )
    diseases = list(infec2.Disease)
    infec1 = infec1[
        infec1["Disease"].isin(diseases) & infec1["Sex"].isin(["Male", "Female"])
    ]

    mf_fig = px.bar(
        infec[infec["Sex"] != "Total"]
        .groupby(["Sex", "Year"])
        .mean()
        .reset_index()
        .sort_values(by="Sex", ascending=False),
        x="Year",
        y="Rate",
        color="Sex",
        barmode="group",
        labels={"Rate": "Average # infections every 100,000 people"},
        title="Crude Rate of Infectious Diseases by Yearly Reports",
    )

    top_fig = px.bar(
        infec1,
        x="Disease",
        y="Rate",
        color="Sex",
        labels={"Rate": "Average # infections every 100,000 people (log)"},
        title="Top 15 most infectious diseases by Gender",
        log_y=True,
    )

    top_fig.update_layout(
        barmode="stack",
        # add linear log buttons
        # https://chart-studio.plotly.com/~empet/15608/relayout-method-to-change-the-layout-att/#/
        updatemenus=[
            dict(
                direction="right",
                active=0,
                x=1,
                y=1.1,
                buttons=[
                    dict(
                        label="Linear",
                        method="relayout",
                        args=[{"yaxis.type": "linear"}],
                    ),
                    dict(label="Log", method="relayout", args=[{"yaxis.type": "log"}]),
                ],
                showactive=False,
                type="buttons",
            )
        ],
        xaxis=dict(
            categoryorder="total descending",
        ),
    )

    return mf_fig, top_fig


def injuries():
    fatal = pd.read_csv("data/Injury/fatal_injuries.csv")
    nonfatal = pd.read_csv("data/Injury/nonfatal_injuries.csv")

    rm_cols = []
    for header in fatal:
        if len(set(fatal[header].value_counts())) == 1:
            rm_cols.append(header)

    # remove null and non-numerical values
    fatal = fatal.drop(columns=rm_cols)
    fatal = fatal.dropna()
    fatal = fatal[pd.to_numeric(fatal["Crude Rate"], errors="coerce").notnull()]

    rm_cols = []
    for header in nonfatal:
        if len(set(nonfatal[header].value_counts())) == 1:
            rm_cols.append(header)

    rm_cols.append("Number of$Cases (Sample)")
    nonfatal = nonfatal.drop(columns=rm_cols)
    nonfatal = nonfatal.dropna()

    # removing '.' in population column
    nonfatal["Population"] = (
        nonfatal[nonfatal["Population"] != "."]["Population"]
        .str.replace(",", "")
        .astype(float)
    )

    # removing non numerical values from columns
    for i in ["Population", "Injuries", "records"]:
        nonfatal = nonfatal[pd.to_numeric(nonfatal[i], errors="coerce").notnull()]

    nonfatal["Crude Rate (estimated)"] = [
        100000 * float(i) / float(j)
        for i, j in zip(nonfatal["Injuries"], nonfatal["Population"])
    ]
    nonfatal["Crude Rate (recorded)"] = [
        100000 * float(i) / float(j)
        for i, j in zip(nonfatal["records"], nonfatal["Population"])
    ]
    nonfatal = nonfatal[nonfatal["Sex"] != "B"]
    nonfatal["Race/Ethnicity"].value_counts()

    fatal = px.scatter(
        fatal,
        x="Age in Years",
        y="Crude Rate",
        color="Race",
        facet_col="Sex",
        title="Count of Fatal Injuries (per 100,000 people)",
        log_y=False,
    )

    fatal.update_layout(autotypenumbers="convert types")
    for a in fatal.layout.annotations:
        a.text = a.text.split("=")[1]
    fatal.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=0.75),
        height=450,
        width=750,
    )

    non_fatal = px.scatter(
        nonfatal,
        x="Age in Years",
        y="Crude Rate (estimated)",
        color="Race/Ethnicity",
        facet_col="Sex",
        title="Count of Non-Fatal Injuries (per 100,000 people)",
        log_y=False,
    )
    non_fatal.update_layout(autotypenumbers="convert types")
    non_fatal.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=0.75),
        height=450,
        width=750,
    )
    newnames = {"W": "White", "A": "Asian", "B": "Black", "H": "Hispanic", "O": "Other"}
    non_fatal.for_each_trace(
        lambda t: t.update(
            name=newnames[t.name],
            legendgroup=newnames[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name]),
        )
    )
    newgender = {"B": "Both", "M": "Males", "F": "Females"}

    for a in non_fatal.layout.annotations:
        a.text = newgender[a.text.split("=")[1]]

    return fatal, non_fatal