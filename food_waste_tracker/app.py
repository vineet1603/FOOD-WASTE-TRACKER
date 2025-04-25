import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from food_waste_data import (
    initialize_data,
    add_waste_entry,
    get_stats,
    get_all_data,
    delete_data_by_id
)
from visualization import (
    create_daily_chart,
    create_category_chart,
    create_monthly_trend
)
from chatbot import get_chatbot_response

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Food Waste Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data from MongoDB
waste_data = initialize_data()

# Session state for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# App title
st.title("🥕 Food Waste Tracker with AI Assistant")

# --- Sidebar Form: Add New Entry ---
st.sidebar.subheader("➕ Add Food Waste Entry")
with st.sidebar.form("waste_form"):
    food_item = st.text_input("Food Item")
    category = st.selectbox("Category", ["Vegetables", "Fruits", "Dairy", "Grains", "Meat", "Others"])
    quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
    unit = st.selectbox("Unit", ["kg", "lbs", "servings", "items"])
    reason = st.selectbox("Reason", ["Expired", "Spoiled", "Leftover", "Overcooked", "Others"])
    date = st.date_input("Date", datetime.today())
    notes = st.text_area("Notes (optional)")
    submit = st.form_submit_button("Submit")

if submit:
    add_waste_entry(None, food_item, category, quantity, unit, date, reason, notes)
    st.success(f"✅ {quantity} {unit} of '{food_item}' added!")

    # Trigger chatbot after entry
    prompt = (
        f"I just logged {quantity} {unit} of {food_item} in the category '{category}', "
        f"wasted because it was '{reason}'. Suggest a tip or advice."
    )
    bot_reply = get_chatbot_response(prompt, waste_data)
    st.session_state.chat_history.append(("Assistant", bot_reply))


# --- Dashboard Section ---
st.subheader("📊 Waste Overview")

total, avg_daily, top_cat = get_stats(waste_data)
col1, col2, col3 = st.columns(3)
col1.metric("Total Waste (kg)", f"{total:.2f}")
col2.metric("Avg Daily Waste", f"{avg_daily:.2f} kg")
col3.metric("Top Wasted Category", top_cat)

# Charts
st.plotly_chart(create_daily_chart(waste_data), use_container_width=True)
st.plotly_chart(create_category_chart(waste_data), use_container_width=True)
st.plotly_chart(create_monthly_trend(waste_data), use_container_width=True)

# --- Chat Assistant ---
st.subheader("💬 Ask Your AI Assistant")

user_msg = st.text_input("Talk to the assistant:", key="chat_input")

if user_msg:
    st.session_state.chat_history.append(("You", user_msg))
    response = get_chatbot_response(user_msg, waste_data)
    st.session_state.chat_history.append(("Assistant", response))

# Display chat history
for speaker, message in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {message}")

# --- Data Table + Delete ---
st.subheader("📋 Waste Log")
raw_data = get_all_data()
if raw_data:
    df = initialize_data()
    st.dataframe(df.drop(columns=["_id"]), use_container_width=True)

    delete_id = st.text_input("Enter MongoDB ID to Delete Entry:")
    if st.button("Delete Entry"):
        try:
            delete_data_by_id(delete_id)
            st.success("🗑️ Entry deleted successfully.")
        except:
            st.error("❌ Invalid ID or deletion failed.")
else:
    st.info("No entries yet. Add your first one from the sidebar.")
