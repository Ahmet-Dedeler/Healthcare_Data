import streamlit as st
import streamlit.components.v1 as components

import pandas as pd

from google_nlp import *
import pickle

from visualizations import *


def main():
    st.set_page_config(
        page_title="Healthcare Data Insights",
        page_icon="📊",
        initial_sidebar_state="expanded",
    )

    st.title("Healthcare Data Insights 🏥📊")
    st.caption("Empowering you with Healthcare Data! 💪")

    st.write(
        "Healthcare Information holds valuable insights into risks we encounter in our daily lives. Our application examines this data to provide insights into the risks you might face in your everyday routine. 🧐"
    )

    st.subheader("Tell us about yourself 🧑🏻👩🏾")

    user_info = ()
    response = ""
    score = 0
    submit = False

    with st.form("user_info"):
        with open("data/states_dict.pickle", "rb") as filehandle:
            us_dict = pickle.load(filehandle)
            states_list = us_dict.keys()

        col1, col2, col3 = st.columns(3)

        gender = col1.selectbox("Please select your gender 👨‍🦰👩‍🦱", ("Male 👨", "Female 👩"))
        age = col2.number_input("Your age? 🎂", min_value=18, max_value=90, step=1)
        state = col3.selectbox("Where do you live? 🏠", states_list)

        txt = st.text_area(
            "What are your thoughts on the Healthcare Industry? 🤔",
            placeholder="I believe healthcare industry needs a significant reform. 💉",
        )
        submitted = st.form_submit_button("Submit 🚀")

        if submitted:
            user_info = (gender, age, state)
            response, score = google_nlp(txt)
            submit = True

    if submit:

        st.success("Thank you for your submission! 🙏")

        st.subheader(response)

        with st.expander("See detailed analysis 🔍", expanded=True):
            st.markdown(f"Sentiment score for your response: `{score}` 📈")
            st.image("media/score-range.png")
            st.caption("Natural Language API by Google Cloud 🌩️")

        st.header("Now let's explore the risks you may encounter 👇")

        gender = user_info[0]
        age = user_info[1]
        state = user_info[2]

        med_age, med_sex, med_time, med_type = med_care()

        st.markdown(f"#### You are a/an `{age}` y/o `{gender}` residing in `{state}` 📍")

        st.header(f"Let's delve into your age group 🧑‍🦳")

        st.subheader("Key insights for your age group 📈")

        st.plotly_chart(med_age)

        st.write(
            "Individuals in the age range of 25-34 are most likely to experience delays in medical care. ⏰"
        )

        st.subheader(f"As a {gender},")

        st.plotly_chart(med_sex)

        if gender == "Female":
            st.write(
                "Females may experience more delays in medical care compared to males. ⏰"
            )
        else:
            st.write("Males are less likely than females to experience delays in medical care. ⏰")

        mf_fig, top_fig = infec_dis()

        st.plotly_chart(mf_fig)

        if gender == "Female":
            st.write(
                "Females may have a higher likelihood of contracting infectious diseases compared to males. 🦠"
            )
            st.write(
                "They are also more likely to experience delays in medical care compared to males. ⏰"
            )
        else:
            st.write("Males are less likely than females to contract infectious diseases. 🦠")

        st.plotly_chart(top_fig)

        if gender == "Female":
            st.write("Be cautious about Chlamydia and gonorrhea. 🚨")
        else:
            st.write("You may be more susceptible to contracting HIV and early syphilis. 🚨")

        st.subheader("Injury Risks 💥")

        fatal, nonfatal = injuries()

        st.plotly_chart(fatal)

        if gender == "Female":
            st.write("Females have a lower likelihood of fatal injuries compared to males. 💔")
        else:
            st.write("Between ages 23-40, you might be more at risk for fatal injuries. 💔")

        st.plotly_chart(nonfatal)

        if gender == "Female":
            st.write("Females have a lower likelihood of non-fatal injuries compared to males. 🤕")
        else:
            st.write("Between ages 23-50, you might be more at risk for non-fatal injuries. 🤕")

        st.subheader("We hope you found the visualizations informative! 🤓")

        st.markdown(
            """
            ---
            ### Datasets used for visualizations:
            1. Infectious Disease 2001-2014 - dataset by health by data.world
                - <https://data.world/health/infectious-disease-2001-2014>
            2. Web-based Injury Statistics Query and Reporting System by Injury Center|CDC
                - <https://www.cdc.gov/injury/wisqars/index.html>
            3. Delay or nonreceipt of needed medical care during the past 12 months due to cost by Centers for Disease Control and Prevention
                - <https://data.cdc.gov/NCHS/Delay-or-nonreceipt-of-needed-medical-care-prescri/dmzy-x2ad>)

            """
        )


if __name__ == "__main__":
    main()
