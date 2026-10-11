import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from io import BytesIO

st.set_page_config(page_title="TerraMind | Land Acquisition Risk", page_icon="🌍", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.main {background-color:#f7f9fc;}
.block-container {padding-top:1.5rem;}
.tm-card {
    padding:18px 20px; border-radius:14px; background:white;
    border:1px solid #e5e7eb; box-shadow:0 2px 10px rgba(0,0,0,.04);
    margin-bottom:12px;
}
.metric-box {
    padding:16px;
    border-radius:12px;
    background:white;
    border:1px solid #e5e7eb;
    text-align:center;
    color:#111827 !important;
}

.metric-box h2 {
    color:#111827 !important;
}

.metric-box .small {
    color:#6b7280 !important;
}
.small {color:#6b7280; font-size:0.88rem;}
.risk-high {color:#b91c1c; font-weight:700;}
.risk-medium {color:#b45309; font-weight:700;}
.risk-low {color:#15803d; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session data
# -----------------------------
if "cases" not in st.session_state:
    st.session_state.cases = pd.DataFrame([
        {"Case ID":"TM-1001","Project":"Rural Road Package A","District":"Kamrup","State":"Assam",
         "Approval":"Pending","Documentation":"Incomplete","Legal Dispute":"Yes",
         "Compensation":"Pending","Landowner Cooperation":"Low","Affected Parcels":42,
         "Risk":82,"Level":"High","Reasons":"Legal dispute; pending compensation; incomplete documentation"},
        {"Case ID":"TM-1002","Project":"Irrigation Canal Phase II","District":"Barpeta","State":"Assam",
         "Approval":"Approved","Documentation":"Complete","Legal Dispute":"No",
         "Compensation":"In Progress","Landowner Cooperation":"Medium","Affected Parcels":27,
         "Risk":43,"Level":"Medium","Reasons":"Compensation still in progress; moderate cooperation"},
        {"Case ID":"TM-1003","Project":"Village Connectivity Project","District":"Nalbari","State":"Assam",
         "Approval":"Approved","Documentation":"Complete","Legal Dispute":"No",
         "Compensation":"Completed","Landowner Cooperation":"High","Affected Parcels":15,
         "Risk":12,"Level":"Low","Reasons":"No major risk factor identified"},
    ])

# -----------------------------
# Explainable scoring engine
# -----------------------------
def predict_risk(approval, documentation, dispute, compensation, cooperation, parcels, days_pending):
    score = 0
    reasons = []

    approval_points = {"Approved":0, "In Review":12, "Pending":22}
    doc_points = {"Complete":0, "Partially Complete":12, "Incomplete":20}
    comp_points = {"Completed":0, "In Progress":12, "Pending":20}
    coop_points = {"High":0, "Medium":7, "Low":15}

    score += approval_points[approval]
    if approval != "Approved":
        reasons.append("Administrative approval is not completed")
    score += doc_points[documentation]
    if documentation != "Complete":
        reasons.append("Documentation is incomplete or partially complete")
    if dispute == "Yes":
        score += 25
        reasons.append("Legal dispute is present")
    score += comp_points[compensation]
    if compensation != "Completed":
        reasons.append("Compensation process is not completed")
    score += coop_points[cooperation]
    if cooperation != "High":
        reasons.append("Landowner cooperation needs attention")

    if days_pending > 180:
        score += 10
        reasons.append("Case has remained pending for more than 180 days")
    elif days_pending > 90:
        score += 5
        reasons.append("Case has remained pending for more than 90 days")

    if parcels >= 100:
        score += 5
        reasons.append("Large number of affected parcels increases coordination complexity")
    elif parcels >= 50:
        score += 3
        reasons.append("Moderate-to-large number of affected parcels")

    score = min(100, score)
    if score >= 65:
        level = "High"
    elif score >= 35:
        level = "Medium"
    else:
        level = "Low"
    return score, level, reasons

def recommendations(reasons):
    rec = []
    for r in reasons:
        if "approval" in r.lower():
            rec.append("Follow up with the concerned approving authority and track the pending approval.")
        elif "documentation" in r.lower():
            rec.append("Create a document checklist and complete missing/incorrect records.")
        elif "legal" in r.lower():
            rec.append("Escalate the dispute for legal review and maintain a clear resolution timeline.")
        elif "compensation" in r.lower():
            rec.append("Verify compensation eligibility, payment status and pending beneficiary records.")
        elif "cooperation" in r.lower():
            rec.append("Increase stakeholder communication and schedule a local grievance/support meeting.")
        elif "180" in r:
            rec.append("Escalate the long-pending case for a time-bound review.")
        elif "90" in r:
            rec.append("Review the case with the responsible officer and set a follow-up deadline.")
        elif "parcels" in r:
            rec.append("Consider parcel-wise tracking to reduce coordination bottlenecks.")
    # preserve order, remove duplicates
    return list(dict.fromkeys(rec))

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown("## 🌍 TerraMind")
st.sidebar.caption("Predictive Land Acquisition Risk Monitor")
page = st.sidebar.radio("Navigate", ["Dashboard", "New Case Prediction", "Case Monitoring", "About"])
st.sidebar.divider()
st.sidebar.info("Prototype for SIH • SIH26017\n\nPython + Streamlit\n\nThe prototype uses an explainable rule-based risk model. It can later be replaced/trained with verified government historical data.")

# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    st.title("🌍 TerraMind")
    st.subheader("Predictive Analytics for Early Detection of Land Acquisition Delays")
    st.markdown("**Predict before the delay becomes critical.**")

    df = st.session_state.cases
    total = len(df)
    high = int((df["Level"]=="High").sum())
    medium = int((df["Level"]=="Medium").sum())
    low = int((df["Level"]=="Low").sum())

    c1,c2,c3,c4 = st.columns(4)
    for c, title, value in [(c1,"Total Cases",total),(c2,"High Risk",high),(c3,"Medium Risk",medium),(c4,"Low Risk",low)]:
        c.markdown(f'<div class="metric-box"><div class="small">{title}</div><h2>{value}</h2></div>', unsafe_allow_html=True)

    st.write("")
    left,right = st.columns([1.2,1])
    with left:
        st.markdown("### 📊 Current Risk Overview")
        chart = df["Level"].value_counts().reindex(["High","Medium","Low"]).fillna(0)
        st.bar_chart(chart)
    with right:
        st.markdown("### 🚨 Cases Requiring Attention")
        if high:
            st.dataframe(df[df["Level"]=="High"][["Case ID","Project","District","Risk","Reasons"]], hide_index=True, use_container_width=True)
        else:
            st.success("No high-risk cases currently.")

    st.markdown("### 🔄 How TerraMind Works")
    st.markdown("""
    **Case Data → Risk Analysis → Delay Probability → Reasons → Preventive Action**

    TerraMind combines important acquisition factors into an explainable risk score.
    Instead of only showing the current status, it helps answer **which cases may be delayed and why**.
    """)

# -----------------------------
# New prediction
# -----------------------------
elif page == "New Case Prediction":
    st.title("📋 New Land Acquisition Case")
    st.caption("Enter the current status of a case to generate an early-warning risk assessment.")

    with st.form("prediction_form"):
        a,b,c = st.columns(3)
        with a:
            case_id = st.text_input("Case ID", value=f"TM-{1000+len(st.session_state.cases)+1}")
            project = st.text_input("Project / Scheme Name", "New Development Project")
            state = st.text_input("State", "Assam")
            district = st.text_input("District", "Kamrup")
        with b:
            approval = st.selectbox("Administrative Approval", ["Approved","In Review","Pending"])
            documentation = st.selectbox("Documentation Status", ["Complete","Partially Complete","Incomplete"])
            dispute = st.selectbox("Legal Dispute", ["No","Yes"])
            compensation = st.selectbox("Compensation Status", ["Completed","In Progress","Pending"])
        with c:
            cooperation = st.selectbox("Landowner Cooperation", ["High","Medium","Low"])
            parcels = st.number_input("Affected Parcels", min_value=1, value=25, step=1)
            days_pending = st.number_input("Days Pending", min_value=0, value=60, step=1)

        submitted = st.form_submit_button("🔍 Analyze Case", use_container_width=True)

    if submitted:
        score, level, reasons = predict_risk(approval, documentation, dispute, compensation, cooperation, parcels, days_pending)
        recs = recommendations(reasons)

        st.divider()
        st.markdown("## Risk Assessment")
        x,y,z = st.columns(3)
        x.metric("Estimated Delay Risk", f"{score}%")
        y.metric("Risk Level", level)
        z.metric("Affected Parcels", parcels)

        if level == "High":
            st.error("🔴 HIGH RISK — Early intervention is recommended.")
        elif level == "Medium":
            st.warning("🟠 MEDIUM RISK — Monitor the case closely.")
        else:
            st.success("🟢 LOW RISK — No major warning signs identified.")

        l,r = st.columns(2)
        with l:
            st.markdown("### 🔎 Main Risk Factors")
            if reasons:
                for reason in reasons:
                    st.write("•", reason)
            else:
                st.success("No major risk factor identified.")
        with r:
            st.markdown("### 💡 Suggested Actions")
            for rec in recs:
                st.write("•", rec)

        row = {
            "Case ID":case_id,"Project":project,"District":district,"State":state,
            "Approval":approval,"Documentation":documentation,"Legal Dispute":dispute,
            "Compensation":compensation,"Landowner Cooperation":cooperation,
            "Affected Parcels":parcels,"Risk":score,"Level":level,
            "Reasons":"; ".join(reasons) if reasons else "No major risk factor identified"
        }
        st.session_state.last_prediction = (row, recs)

        csv = pd.DataFrame([row]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Case Assessment (CSV)", csv, "terramind_case_assessment.csv", "text/csv")

        if st.button("➕ Add Case to Monitoring Dashboard"):
            st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([row])], ignore_index=True)
            st.success(f"{case_id} added to TerraMind monitoring.")

# -----------------------------
# Monitoring
# -----------------------------
elif page == "Case Monitoring":
    st.title("📊 Case Monitoring")
    df = st.session_state.cases.copy()

    f1,f2,f3 = st.columns(3)
    risk_filter = f1.selectbox("Risk Level", ["All","High","Medium","Low"])
    district_filter = f2.selectbox("District", ["All"] + sorted(df["District"].unique().tolist()))
    search = f3.text_input("Search Project / Case ID")

    filtered = df.copy()
    if risk_filter != "All":
        filtered = filtered[filtered["Level"] == risk_filter]
    if district_filter != "All":
        filtered = filtered[filtered["District"] == district_filter]
    if search:
        mask = filtered["Project"].str.contains(search, case=False, na=False) | filtered["Case ID"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    st.dataframe(filtered, hide_index=True, use_container_width=True)

    st.markdown("### 📌 Priority Cases")
    priority = df.sort_values("Risk", ascending=False).head(5)
    for _, row in priority.iterrows():
        if row["Level"] == "High":
            st.error(f"**{row['Case ID']} — {row['Project']}** | {row['District']} | Risk: {row['Risk']}%")
        elif row["Level"] == "Medium":
            st.warning(f"**{row['Case ID']} — {row['Project']}** | {row['District']} | Risk: {row['Risk']}%")
        else:
            st.success(f"**{row['Case ID']} — {row['Project']}** | {row['District']} | Risk: {row['Risk']}%")

    st.download_button("⬇️ Export All Cases", df.to_csv(index=False).encode("utf-8"), "terramind_cases.csv", "text/csv")

# -----------------------------
# About
# -----------------------------
else:
    st.title("ℹ️ About TerraMind")
    st.markdown("""
    ### The Problem
    Land acquisition may be delayed by approvals, documentation gaps, legal disputes,
    compensation issues and stakeholder coordination problems.

    ### Our Solution
    TerraMind provides an early-warning layer that estimates delay risk from case-level
    information and explains the main factors contributing to that risk.

    ### Prototype Technology
    - **Frontend / App:** Streamlit
    - **Language:** Python
    - **Data:** Prototype dataset based on open-source information
    - **Approach:** Explainable risk scoring, designed to be upgraded to a trained ML model
    - **Output:** Risk level, contributing factors and preventive actions

    ### Future Development
    With access to verified historical government data, the scoring engine can be replaced
    or enhanced with a trained machine-learning model. The platform can also integrate GIS,
    real-time case data, automated alerts, role-based access and department-level dashboards.

    **Vision:** Move land acquisition monitoring from reactive tracking to proactive intervention.
    """)

st.sidebar.caption("TerraMind • SIH26017 • Prototype")
