import streamlit as st
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import requests, os

model = genai.GenerativeModel("gemini-pro")
SYMBOLS = ["AAPL", "AMZN", "META", "MSFT", "NFLX"]
fmp_api_key = os.environ["fmp_api_key"]
genai.configure(api_key=os.environ["gemini_api_key"])

def click_button():
    st.session_state.clicked = True
    st.session_state.select_disabled = True
    st.session_state.button_disabled = True

def reset_states():
    st.session_state.clicked = False
    st.session_state.select_disabled = False
    st.session_state.button_disabled = False
    st.session_state.symbol = None

if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'symbol' not in st.session_state:
    st.session_state.symbol = None
if 'select_disabled' not in st.session_state:
    st.session_state.select_disabled = False
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

st.title("Earnings Call Assistant")
st.write("Made with ❄️ from MN.")
symbol = st.selectbox(
    label="Which company would you like to analyze?",
    options=tuple(s for s in SYMBOLS),
    index=None,
    key='symbol',
    disabled=st.session_state.select_disabled,
    placeholder="Choose a ticker..."
)

if symbol:
    st.button(
        label=f"Summarize Latest Earnings Call for {symbol}",
        type="primary",
        on_click=click_button,
        disabled=st.session_state.button_disabled,
        use_container_width=True
    )
    if st.session_state.clicked:
        url_transcription = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?apikey={fmp_api_key}"
        response_transcription = requests.get(url_transcription)
        transcript = response_transcription.json()[0]
        content = transcript["content"]
        symbol = transcript["symbol"]
        year = transcript["year"]
        quarter = transcript["quarter"]
        try:
            response_gemini = model.generate_content([
                "You are a financial analyst reviewing earnings call transcripts. ",
                f"Your job is to provide a Markdown-formatted summary of the following transcript for {symbol}. ",
                f"Begin the summary with the Ticker ({symbol}), Year ({year}), and Quarter {quarter}. ",
                f"You should be looking for insights related to the financial performance of {symbol}. ",
                "Additionally, you should highlight management's commentary in terms of confidence and optimism, as well as risk factors for future growth. ",
                "Finally, you should provide a summary of the investment implications in the short term and long term. ",
                "Remember to format your response as Markdown and should read as an esay-to-digest financial article. ",
                content
            ]).text
        except Exception as e:
            response_gemini = f"Sorry, there was an error in processing your request. This happens sometimes. Please reset and try again :) \n\n {e}"
        st.markdown(response_gemini.replace("$", "\$"))
        st.button(
            label="Reset",
            on_click=reset_states,
            use_container_width=True
        )
