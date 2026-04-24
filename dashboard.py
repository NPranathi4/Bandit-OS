import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

st.title("BanditOS Dashboard")

# Create Experiment
st.header("Create Experiment")
exp_id = st.text_input("Experiment ID")
variants = st.text_input("Variants (comma separated, e.g. A,B)")

if st.button("Create"):
    response = requests.post(
        f"{BASE_URL}/create_experiment",
        json={
            "experiment_id": exp_id,
            "variants": [v.strip() for v in variants.split(",")]
        }
    )
    st.write(response.json())

# Assign Variant
st.header("Assign Variant")

assign_exp = st.text_input("Experiment ID for assignment")

if st.button("Assign"):
    response = requests.get(
        f"{BASE_URL}/assign_variant",
        params={"experiment_id": assign_exp}
    )
    st.write(response.json())

# Record Click
st.header("Record Click")

click_exp = st.text_input("Experiment ID for click")
variant = st.text_input("Variant (A/B)")
reward = st.selectbox("Reward", [0, 1])

if st.button("Submit Click"):
    response = requests.post(
        f"{BASE_URL}/record_click",
        json={
            "experiment_id": click_exp,
            "variant": variant,
            "reward": reward
        }
    )
    st.write(response.json())

# Experiment Status
st.header("Check Status")

status_exp = st.text_input("Experiment ID for status")

if st.button("Check"):
    response = requests.get(
        f"{BASE_URL}/experiment_status",
        params={"experiment_id": status_exp}
    )
    st.write(response.json())

import pandas as pd

st.header("📊 Analytics")

# Input FIRST (outside button)
analytics_exp = st.text_input("Experiment ID for analytics", key="analytics_input")

if st.button("Load Analytics"):
    if analytics_exp:
        status_res = requests.get(
            f"{BASE_URL}/experiment_status",
            params={"experiment_id": analytics_exp}
        )

        data = status_res.json()

        if "traffic_split" in data:
            traffic = data["traffic_split"]

            df = pd.DataFrame({
                "Variant": list(traffic.keys()),
                "Traffic %": list(traffic.values())
            })

            st.subheader("Traffic Split")
            st.bar_chart(df.set_index("Variant"))
        else:
            st.error("No data found")


# ---------- CLICK DATA ----------
click_exp = st.text_input("Experiment ID for clicks", key="clicks_input")

if st.button("Load Click Data"):
    if click_exp:
        res = requests.get(
            f"{BASE_URL}/analytics",
            params={"experiment_id": click_exp}
        )

        response = res.json()
        data = response["clicks"]

        if len(data) > 0:
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

            st.subheader("Click Data Table")
            st.write(df)

            summary = df.groupby("variant")["reward"].sum()

            st.subheader("Total Clicks per Variant")
            st.bar_chart(summary)
            st.subheader("📈 Click Trend Over Time")
            trend = df.groupby(["timestamp", "variant"])["reward"].sum().unstack().fillna(0)
            st.line_chart(trend)   
            # 🚨 ADD THIS PART HERE
            if response.get("anomaly"):
                st.error("🚨 Anomaly Detected in Click Behavior!")
            else:
                st.success("✅ No Anomaly Detected")
        else:
            st.warning("No click data yet")
