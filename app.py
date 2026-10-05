```python
import os
from datetime import datetime, date
import calendar

import streamlit as st
from groq import Groq


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Age Calculator",
    page_icon="🎂",
    layout="centered"
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown("""
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
        border: 1px solid rgba(128,128,128,0.2);
    }

    .age-number {
        font-size: 32px;
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
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="title">🎂 Age Calculator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Calculate your exact age in years, months, days, hours, minutes and seconds.</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Date & Time Input
# ---------------------------------------------------------
st.subheader("📅 Enter Your Date of Birth")

dob = st.date_input(
    "Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today(),
    value=date(2000, 1, 1)
)

st.subheader("⏰ Time of Birth")

birth_time = st.time_input(
    "Time of Birth",
    value=datetime.strptime("00:00:00", "%H:%M:%S").time()
)


# ---------------------------------------------------------
# Calculate Age
# ---------------------------------------------------------
def calculate_age(birth_datetime, current_datetime):

    if birth_datetime > current_datetime:
        return None

    birth_year = birth_datetime.year
    birth_month = birth_datetime.month
    birth_day = birth_datetime.day

    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day

    years = current_year - birth_year
    months = current_month - birth_month
    days = current_day - birth_day

    # Borrow days from previous month
    if days < 0:
        months -= 1

        previous_month = current_month - 1
        previous_year = current_year

        if previous_month == 0:
            previous_month = 12
            previous_year -= 1

        days += calendar.monthrange(previous_year, previous_month)[1]

    # Borrow months from previous year
    if months < 0:
        years -= 1
        months += 12

    # Calculate total time difference
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
        "total_seconds": total_seconds
    }


# ---------------------------------------------------------
# Calculate Button
# ---------------------------------------------------------
if st.button("🔢 Calculate My Age", use_container_width=True):

    birth_datetime = datetime.combine(dob, birth_time)
    current_datetime = datetime.now()

    age = calculate_age(birth_datetime, current_datetime)

    if age is None:
        st.error("Date of birth cannot be in the future.")

    else:

        st.success("Your exact age has been calculated!")

        st.markdown("### 🎯 Your Exact Age")

        # Main age
        st.markdown(
            f"""
            <div class="age-card">
                <div class="age-number">
                    {age['years']} Years, {age['months']} Months, {age['days']} Days
                </div>
                <div class="age-label">
                    Your calendar age
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Years", f"{age['years']:,}")

        with col2:
            st.metric("Months", f"{age['months']:,}")

        with col3:
            st.metric("Days", f"{age['days']:,}")

        st.markdown("### ⏱️ Total Time Lived")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Days", f"{age['total_days']:,}")

        with col2:
            st.metric("Total Hours", f"{age['total_hours']:,}")

        with col3:
            st.metric("Total Minutes", f"{age['total_minutes']:,}")

        st.metric(
            "Total Seconds",
            f"{age['total_seconds']:,}"
        )

        # -------------------------------------------------
        # Groq AI Section
        # -------------------------------------------------
        st.markdown("---")
        st.subheader("🤖 Ask AI About Your Age")

        question = st.text_input(
            "Ask something about your age",
            placeholder="e.g. How many days old am I?"
        )

        if question:

            # First check Streamlit Secrets
            groq_api_key = None

            try:
                groq_api_key = st.secrets.get("GROQ_API_KEY")
            except Exception:
                pass

            # Then check environment variable
            if not groq_api_key:
                groq_api_key = os.getenv("GROQ_API_KEY")

            if not groq_api_key:

                st.warning(
                    "Groq API key is not configured. "
                    "Add GROQ_API_KEY to Streamlit Secrets."
                )

            else:

                try:

                    client = Groq(api_key=groq_api_key)

                    prompt = f"""
You are an age calculation assistant.

The user's date of birth is:
{birth_datetime.strftime("%d %B %Y %H:%M:%S")}

The current date and time is:
{current_datetime.strftime("%d %B %Y %H:%M:%S")}

Calculated age:
{age['years']} years,
{age['months']} months,
{age['days']} days.

Total days lived:
{age['total_days']}

Total hours lived:
{age['total_hours']}

Total minutes lived:
{age['total_minutes']}

Total seconds lived:
{age['total_seconds']}

User's question:
{question}

Answer clearly and briefly.
"""

                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.3,
                        max_tokens=500
                    )

                    answer = response.choices[0].message.content

                    st.markdown("### 🤖 AI Answer")
                    st.write(answer)

                except Exception as e:

                    st.error(
                        f"Unable to connect to Groq: {str(e)}"
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
    unsafe_allow_html=True
)
```
