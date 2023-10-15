from google.cloud import language_v1
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import json
import base64
import streamlit as st

load_dotenv()

def init_google_nlp(local=False):
    
    json_creds = os.environ.get("GOOGLE_SERVICE_KEY")

    final_json_creds = json.loads(json_creds)

    credentials = service_account.Credentials.from_service_account_info(final_json_creds)
    client = language_v1.LanguageServiceClient(credentials=credentials)

    return client


def google_nlp(text, explain=True):

    # use this if you're on local machine
    # client = init_google_nlp(local=True)

    client = init_google_nlp(local=False)

    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )

    sentiment = client.analyze_sentiment(
        request={"document": document}
    ).document_sentiment

    score = round(sentiment.score, 2)

    if score >= 0.25 <= 1.0:
        response = "You seem to be have positive thoughts 😀 about healthcare"

    elif score >= -0.25 < 0.25:
        response = "It appears you are neutral 😐 about the healthcare industry"
    else:
        response = "It looks like you have some anger 😡 towards the healthcare industry"

    if explain == True:
        print("Text: {}".format(text))
        print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

    return response, score
