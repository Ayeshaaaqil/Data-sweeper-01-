import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import io
from io import BytesIO

# Streamlit Page Configurations
st.set_page_config(page_title="📀 Data Sweeper", layout='wide')

# Title and Description
st.title("📀 Data Sweeper")
st.write("✨ Transform, clean, and visualize your data with ease! 🚀")

# File Upload
uploaded_files = st.file_uploader(
    "📂 Upload CSV or Excel Files:",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read the uploaded file
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue

        # Display File Details
        st.write(f"📁 **File Name:** {file.name}")
        st.write(f"📏 **File Size:** {file.size / 1024:.2f} KB")

        # Data Preview
        st.subheader("🔍 Data Preview")
        st.dataframe(df.head())

        # Data Summary
        st.subheader("📊 Data Summary")
        st.write(df.describe())

        # Data Cleaning Options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"🧹 Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑 Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"⚙ Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

        # Column Selection
        st.subheader("📌 Select Columns to Work With")
        columns = st.multiselect(f"🎯 Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Column Renaming
        st.subheader("✏️ Rename Columns")
        new_column_names = {}
        for col in columns:
            new_name = st.text_input(f"Rename {col} to:", col)
            new_column_names[col] = new_name

        df.rename(columns=new_column_names, inplace=True)

        # Correlation Heatmap
        st.subheader("🔥 Correlation Heatmap")
        numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns

        if not numeric_df.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("⚠ No numeric columns found for correlation heatmap.")

        # Data Visualization (Basic Bar Chart)
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"📈 Show Bar Chart for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 1:
                st.bar_chart(df[numeric_cols])
            else:
                st.warning("⚠ Not enough numeric columns for visualization.")

        # Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"🔄 Convert {file.name}"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"⬇️ Download {file_name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("🎉 All files processed successfully!")
