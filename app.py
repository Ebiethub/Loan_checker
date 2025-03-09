import streamlit as st
import requests
import numpy as np
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# API Keys (Replace with actual keys)
INTEREST_API_KEY = st.secrets["INTEREST_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Function to fetch real-time interest rates
def get_interest_rate():
    url = "https://api.api-ninjas.com/v1/interestrate?name=USD%20LIBOR%20-%203%20months"
    headers = {"X-Api-Key": INTEREST_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("rate", 5.0)  # Default to 5% if unavailable
    return 5.0

# Function to calculate monthly payment
def calculate_monthly_payment(loan_amount, interest_rate, loan_term):
    monthly_rate = (interest_rate / 100) / 12
    months = loan_term * 12
    if monthly_rate == 0:
        return loan_amount / months
    return loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

# Initialize session state for chatbot
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Chatbot function using Groq API
def chatbot_response(user_input):
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-specdec",
        temperature=0.7,
        max_tokens=4000
    )
    prompt = PromptTemplate(
        input_variables=["query"],
        template="You are a helpful loan advisor. Answer clearly: {query}"
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(query=user_input)

# Streamlit UI
st.set_page_config(page_title="Loan Eligibility Checker", layout="centered")
st.title("🏦 Loan Eligibility & AI Chatbot")

# Layout
col1, col2 = st.columns(2)
with col1:
    income = st.number_input("💰 Monthly Income ($)", min_value=0, value=3000)
    loan_amount = st.number_input("💵 Loan Amount ($)", min_value=0, value=10000)
    credit_score = st.slider("📊 Credit Score", 300, 850, 700)
    loan_term = st.selectbox("📆 Loan Term (Years)", [5, 10, 15, 20, 25, 30])

# Fetch real-time interest rate
interest_rate = get_interest_rate()
monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term)

# Display results
with col2:
    st.metric("📈 Interest Rate", f"{interest_rate:.1f}%")
    st.metric("💳 Estimated Monthly Payment", f"${monthly_payment:.2f}")

# Loan Approval Logic
if st.button("Check Eligibility"):
    if income > 2000 and credit_score >= 650 and loan_amount <= income * 5:
        st.success("✅ You are eligible for the loan.")
    else:
        st.error("❌ You do not meet the eligibility criteria.")

# Loan Chatbot
initialize_session()
st.subheader("🤖 Loan Assistance Chatbot")
user_query = st.text_input("Ask me anything about loans!")
if st.button("Ask Chatbot"):
    if user_query:
        response = chatbot_response(user_query)
        st.session_state.messages.append(("You", user_query))
        st.session_state.messages.append(("Chatbot", response))

# Display chat history
for sender, message in st.session_state.messages:
    st.write(f"**{sender}:** {message}")
