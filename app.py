import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="AI Revenue Risk Agent", layout="wide")

st.title("AI Revenue Leakage Detection Agent")
st.markdown("Upload AR Aging, Billing, and Contract files to run automated risk analysis.")

# File Upload Section
col1, col2, col3 = st.columns(3)

with col1:
    ar_file = st.file_uploader("Upload AR Aging File", type=["xlsx"])

with col2:
    billing_file = st.file_uploader("Upload Billing File", type=["xlsx"])

with col3:
    contract_file = st.file_uploader("Upload Contract File", type=["xlsx"])


def calculate_risk(df):

    risk_levels = []
    reasons_list = []

    for _, row in df.iterrows():

        risk_score = 0
        reasons = []

        if row["Days_Overdue"] > 90:
            risk_score += 3
            reasons.append("Invoice overdue > 90 days")

        if row["Budgeted_Cost"] > row["Contract_Value"]:
            risk_score += 2
            reasons.append("Cost overrun risk")

        if row["Outstanding_Amount"] > 0.8 * row["Invoice_Amount"]:
            risk_score += 2
            reasons.append("High outstanding exposure")

        if row["Complexity_Score"] == "High":
            risk_score += 1
            reasons.append("High project complexity")

        if risk_score >= 5:
            risk_level = "High"
        elif risk_score >= 3:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        risk_levels.append(risk_level)
        reasons_list.append(", ".join(reasons))

    df["Risk_Level"] = risk_levels
    df["Risk_Reasons"] = reasons_list

    return df


if st.button("Run Analysis"):

    if ar_file and billing_file and contract_file:

        try:
            ar_data = pd.read_excel(ar_file)
            billing_data = pd.read_excel(billing_file)
            contract_data = pd.read_excel(contract_file)

            df = ar_data.merge(billing_data, on="Invoice_No")
            df = df.merge(contract_data, on="Project_ID")

            df = calculate_risk(df)

            st.success("Risk Analysis Completed Successfully")

            # KPI Metrics
            total_invoices = len(df)
            high_risk = len(df[df["Risk_Level"] == "High"])
            medium_risk = len(df[df["Risk_Level"] == "Medium"])
            low_risk = len(df[df["Risk_Level"] == "Low"])

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Invoices", total_invoices)
            k2.metric("High Risk", high_risk)
            k3.metric("Medium Risk", medium_risk)
            k4.metric("Low Risk", low_risk)

            st.dataframe(df, use_container_width=True)

            # Download Button
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="Download Results",
                data=output,
                file_name="Revenue_Risk_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error processing files: {e}")

    else:
        st.warning("Please upload all three required files before running analysis.")
