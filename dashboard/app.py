import streamlit as st
from pyspark.sql import SparkSession

from core.config import settings


class Dashboard:

    def __init__(self):
        self.spark = SparkSession.builder \
            .appName(f"{settings.spark.app_name}-dashboard") \
            .getOrCreate()

    def load_data(self):
        df = self.spark.read.parquet(settings.paths.gold)
        return df.toPandas()

    def run(self):
        st.set_page_config(page_title="AdTech Metrics", layout="wide")
        st.title("AdTech Real-Time Metrics Dashboard")

        st.sidebar.header("Controls")
        if st.sidebar.button("Refresh Data"):
            st.rerun()

        try:
            df = self.load_data()

            if df.empty:
                st.warning("No data available yet.")
                return

            total_revenue = df["total_revenue"].sum()
            total_events = df["total_events"].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total Revenue", f"${total_revenue:.2f}")
            col2.metric("Total Events", int(total_events))

            st.divider()

            st.subheader("Campaign Metrics")
            st.dataframe(df)

            st.subheader("Top Users by Revenue")
            df_sorted = df.sort_values("total_revenue", ascending=False)
            st.bar_chart(df_sorted.set_index("user_id")["total_revenue"])

        except Exception as e:
            st.error(f"Error loading data: {e}")


if __name__ == "__main__":
    Dashboard().run()

    config = AppConfig.from_yaml(args.config)

    dashboard = Dashboard(config)
    dashboard.run()
