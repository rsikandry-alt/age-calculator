
import os
import calendar
from datetime import datetime, date
from groq import Groq
import streamlit as st


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Age Calculator",
    page_icon="🎂",
    layout="centered",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777;
        margin-bottom: 30px;
    }

    .age-card {
        padding: 22px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }

    .age-number {
        font-size: 28px;
        font-weight: 700;
    }

    .age-label {
        font-size: 14px;
        color: #777;
    }

    .footer {
        text-align: center;
        color: #888;
        font-size: 13px;
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="title">🎂 Age Calculator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Calculate your age in years, months, days, hours, "
    "minutes and seconds."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helper: Add calendar months to a datetime
# ---------------------------------------------------------
def add_months(dt, months):
    month_index = dt.month - 1 + months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1

    # Clamp the day for shorter months and leap years
    day = min(
        dt.day,
        calendar.monthrange(year, month)[1],
    )

    return dt.replace(year=year, month=month, day=day)


# ---------------------------------------------------------
# Age Calculation
# ---------------------------------------------------------
def calculate_age(birth_datetime, current_datetime):
    if birth_datetime > current_datetime:
        return None

    # Calculate completed calendar years
    years = current_datetime.year - birth_datetime.year

    anniversary = add_months(birth_datetime, years * 12)

    if anniversary > current_datetime:
        years -= 1

    anniversary = add_months(birth_datetime, years * 12)

    # Calculate completed calendar months
    months = (
        (current_datetime.year - anniversary.year) * 12
        + current_datetime.month
        - anniversary.month
    )

    month_date = add_months(anniversary, months)

    if month_date > current_datetime:
        months -= 1

    month_date = add_months(anniversary, months)

    # Remaining days, hours, minutes and seconds
    remaining = current_datetime - month_date
    days = remaining.days

    # Total elapsed time
    total_seconds = int(
        (current_datetime - birth_datetime).total_seconds()
    )

    total_minutes = total_seconds // 60
    total_hours = total_seconds // 3600
    total_days = total_seconds // 86400

    return {
        "years": years,
        "months": months,
        "days": days,
        "total_days": total_days,
        "total_hours": total_hours,
        "total_minutes": total_minutes,
        "total_seconds": total_seconds,
    }


# ---------------------------------------------------------
# Date and Time Inputs
# ---------------------------------------------------------
st.subheader("📅 Enter Your Date of Birth")

dob = st.date_input(
    "Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today(),
    value=date(2000, 1, 1),
)

st.subheader("⏰ Time of Birth")

birth_time = st.time_input(
    "Time of Birth",
    value=datetime.strptime("00:00:00", "%H:%M:%S").time(),
)


# ---------------------------------------------------------
# Calculate Button
# ---------------------------------------------------------
if st.button("🔢 Calculate My Age", use_container_width=True):
    birth_datetime = datetime.combine(dob, birth_time)
    current_datetime = datetime.now()

    age = calculate_age(birth_datetime, current_datetime)

    if age is None:
        st.error("Date and time of birth cannot be in the future.")
        st.session_state.pop("age_result", None)

    else:
        st.session_state["age_result"] = {
            "birth_datetime": birth_datetime,
            "current_datetime": current_datetime,
            "age": age,
        }


# ---------------------------------------------------------
# Display Results
# ---------------------------------------------------------
if "age_result" in st.session_state:
    result = st.session_state["age_result"]
    age = result["age"]
    birth_datetime = result["birth_datetime"]
    current_datetime = result["current_datetime"]

    st.success("Your exact age has been calculated!")

    st.markdown("### 🎯 Your Exact Age")

    st.markdown(
        f"""
        <div class="age-card">
            <div class="age-number">
                {age['years']} Years, {age['months']} Months,
                {age['days']} Days
            </div>
            <div class="age-label">Your calendar age</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Years", f"{age['years']:,}")
    col2.metric("Months", f"{age['months']:,}")
    col3.metric("Days", f"{age['days']:,}")

    st.markdown("### ⏱️ Total Time Lived")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Days", f"{age['total_days']:,}")
    col2.metric("Total Hours", f"{age['total_hours']:,}")
    col3.metric("Total Minutes", f"{age['total_minutes']:,}")

    st.metric("Total Seconds", f"{age['total_seconds']:,}")

    st.caption(
        "Results are calculated as of "
        + current_datetime.strftime("%d %B %Y, %H:%M:%S")
        + ". Recalculate to refresh the time."
    )

    # -----------------------------------------------------
    # Groq AI Assistant
    # -----------------------------------------------------
    st.divider()
    st.subheader("🤖 Ask AI About Your Age")

    question = st.text_input(
        "Ask a question about your age",
        placeholder="e.g. How many days old am I?",
        key="ai_question",
    )

    if st.button("💬 Ask AI", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question first.")

        else:
            # Read key from Streamlit Secrets or environment
            groq_api_key = None

            try:
                groq_api_key = st.secrets.get("GROQ_API_KEY")
            except Exception:
                pass

            if not groq_api_key:
                groq_api_key = os.getenv("GROQ_API_KEY")

            if not groq_api_key:
                st.warning(
                    "Groq API key is not configured. "
                    "Add GROQ_API_KEY to Streamlit Secrets."
                )

            else:
                prompt = f"""
You are a helpful age and date assistant.

The user's date of birth is:
{birth_datetime.strftime("%d %B %Y %H:%M:%S")}

The calculation time is:
{current_datetime.strftime("%d %B %Y %H:%M:%S")}

Calculated calendar age:
{age['years']} years, {age['months']} months,
{age['days']} days.

Total days lived: {age['total_days']}
Total hours lived: {age['total_hours']}
Total minutes lived: {age['total_minutes']}
Total seconds lived: {age['total_seconds']}

User's question:
{question}

Answer clearly and briefly. Use the provided calculation
for the user's current age. Do not invent personal details.
"""

                try:
                    with st.spinner("AI is preparing your answer..."):
                        client = Groq(api_key=groq_api_key)

                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt,
                                }
                            ],
                            temperature=0.3,
                            max_tokens=500,
                        )

                        answer = response.choices[0].message.content

                    st.markdown("### 🤖 AI Answer")
                    st.write(answer)

                except Exception:
                    st.error(
                        "Unable to get a response from Groq. "
                        "Check your API key, model availability, "
                        "internet connection, or API usage limits."
                    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        🎂 Age Calculator • Built with Streamlit & Groq
    </div>
    """,
    unsafe_allow_html=True,
)
