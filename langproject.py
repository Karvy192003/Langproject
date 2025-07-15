import streamlit as st
import pandas as pd
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# -------------------- CONFIG --------------------
st.set_page_config(page_title="PropGuard AI", page_icon="🔒", layout="centered")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.output-box {
    background-color: #075E54;
    border-radius: 15px;
    padding: 15px;
    margin-top: 20px;
    font-family: monospace;
    color: white;
    border: 1px solid #064c45;
    box-shadow: 0 0 8px rgba(7, 94, 84, 0.5);
}
.map-container {
    background-color: #000000;
    padding: 15px;
    border-radius: 15px;
    margin-top: 20px;
    box-shadow: 0 0 8px rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center; color:#2E8B57;'>🔒 PropGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Detect scams in property listings • Validate rent • See location</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------- API KEYS --------------------
gemini_api_key = "your key"  # Replace with your Gemini API key

if not gemini_api_key:
    st.warning("⚠️ Please provide your Gemini API key.")
    st.stop()

# -------------------- LLM SETUP --------------------
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key, temperature=0.3)

# -------------------- PROMPTS --------------------
detection_template = """
You are a real estate scam detection assistant.

Analyze the listing below and provide:
1. Scam Probability (percentage)
2. Top 3 reasons for your judgment
3. Red Flags
4. Tips to avoid scams

Description: {desc}
Rent: ₹{price}
Location: {location}

Output format:
Scam Probability: xx%
Reasons:
1. ...
2. ...
3. ...
Red Flags:
- ...
Tips:
- ...
"""

expert_template = """
You're a real estate scam expert. Answer the following user question accurately in detail:

Question: {user_input}
"""

detection_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(input_variables=["desc", "price", "location"], template=detection_template)
)

expert_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(input_variables=["user_input"], template=expert_template)
)

# -------------------- TABS --------------------
tab1, tab2, tab3 = st.tabs(["🏠 Scam Detection", "💬 Ask Scam Expert", "📊 Rent Validator"])

# -------------------- TAB 1 --------------------
with tab1:
    st.subheader("🏠 Rental Listing Details")
    desc = st.text_area("📝 Listing Description", height=180)
    price = st.text_input("💰 Rent (₹)")
    location = st.text_input("📍 Location")

    if st.button("🚨 Analyze Listing"):
        if desc and price and location:
            with st.spinner("Analyzing with AI..."):
                result = detection_chain.run({"desc": desc, "price": price, "location": location})
                st.success("✅ Analysis Complete")
                formatted_result = result.strip().replace("\n", "<br>")
                st.markdown(f"<div class='output-box'>{formatted_result}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please fill all fields.")

    # VIEW ON MAP
    if desc and price and location:
        if st.button("🗺️ View on Google Map"):
            map_url = f"https://www.google.com/maps?q={location.replace(' ', '+')}&output=embed"
            st.markdown(f"""
            <div class='map-container'>
                <h4 style='color:white;'>📍 Interactive Location Map</h4>
                <iframe width="100%" height="350" frameborder="0" style="border:0; border-radius:15px;"
                src="{map_url}" allowfullscreen></iframe>
            </div>
            """, unsafe_allow_html=True)

        if len(location.strip().split()) < 2:
            st.warning("⚠️ Location seems too vague. Add proper city and area name.")

# -------------------- TAB 2 --------------------
with tab2:
    st.subheader("💬 Ask a Rental Scam Question")
    user_q = st.text_area("🔎 Enter your question")

    if st.button("🧠 Get Expert Advice"):
        if user_q.strip():
            with st.spinner("AI is answering..."):
                response = expert_chain.run({"user_input": user_q})
                formatted_response = response.strip().replace("\n", "<br>")
                st.success("✅ Response:")
                st.markdown(f"<div class='output-box'>{formatted_response}</div>", unsafe_allow_html=True)
        else:
            st.warning("Type your question first.")

# -------------------- TAB 3 --------------------
with tab3:
    st.subheader("📊 Compare Your Rent with Market Averages")
    city = st.selectbox("📍 Select City", ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Pune"])

    rent_data = {
        "Delhi": 18000,
        "Mumbai": 25000,
        "Bangalore": 20000,
        "Hyderabad": 15000,
        "Pune": 16000
    }

    user_rent = st.number_input("💰 Your Rent (₹)", min_value=1000, max_value=100000, step=500)

    if st.button("📉 Validate Rent"):
        avg = rent_data[city]
        if user_rent < avg * 0.6:
            st.error("🚩 Too Low — Possible Scam")
        elif user_rent > avg * 1.5:
            st.warning("⚠️ Unusually High Rent")
        else:
            st.success("✅ Rent Looks Reasonable")

        df = pd.DataFrame({
            "Category": ["Your Rent", "Market Difference"],
            "Amount": [user_rent, abs(avg - user_rent)]
        })

        fig = px.pie(df, names="Category", values="Amount", title="Rent Comparison Pie Chart",
                     color_discrete_sequence=["#2E8B57", "#A9A9A9"])
        st.plotly_chart(fig)

        st.markdown(f"🏙️ **Average Rent in {city}**: ₹{avg}")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>🔐 Powered by Gemini + LangChain | Built with ❤️ by PropGuard AI</p>", unsafe_allow_html=True)
