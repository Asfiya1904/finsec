import streamlit as st
import pandas as pd
import numpy as np
import requests
import os

st.set_page_config(page_title="FinSec Threat Detection", layout="wide")

if "use_api" not in st.session_state:
    st.session_state.use_api = True

st.title("🛡️ FinSec: AI-Powered Fraud & Threat Detection")

st.sidebar.header("⚙️ Settings")
st.session_state.use_api = st.sidebar.checkbox("Use FinSec API (Live Detection)", value=True)

api_url = os.getenv("FINSEC_API_URL", "https://finsec1.onrender.com/detect")
api_key = os.getenv("FINSEC_API_KEY", "supersecret")

uploaded_file = st.file_uploader("📥 Upload Transaction File (.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data", df.head())

    if st.button("🚨 Analyze Now"):
        results = []
        progress = st.progress(0)
        for i, row in df.iterrows():
            row_data = row.to_dict()
            if st.session_state.use_api:
                try:
                    res = requests.post(
                        api_url,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json=row_data,
                        timeout=10
                    )
                    if res.status_code == 200:
                        result = res.json()
                        row_data.update(result)
                    else:
                        row_data.update({
                            "status": "API Error",
                            "risk_score": None,
                            "severity": "Unknown",
                            "recommendation": "Check API"
                        })
                except Exception as e:
                    row_data.update({
                        "status": "Connection Failed",
                        "risk_score": None,
                        "severity": "Unknown",
                        "recommendation": str(e)
                    })
            else:
                score = np.abs(row.select_dtypes(include=np.number)).sum()
                severity = "Low" if score < 100 else "Medium" if score < 200 else "High"
                row_data.update({
                    "risk_score": round(score, 2),
                    "status": "🟢 Normal" if severity == "Low" else "🔴 Suspicious",
                    "severity": severity,
                    "recommendation": "Monitor" if severity != "High" else "Review"
                })

            results.append(row_data)
            progress.progress((i + 1) / len(df))

        result_df = pd.DataFrame(results)
        st.success("✅ Analysis complete.")
        st.dataframe(result_df)

        st.download_button("📁 Download Results", data=result_df.to_csv(index=False), file_name="finsec_results.csv", mime="text/csv")
