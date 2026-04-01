import streamlit as st
from pyspark.sql import SparkSession

from common.config import AppConfig


class Dashboard:
    """
    Simple Streamlit dashboard for visualizing Gold layer metrics.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.spark = self._create_spark_session()

    def _create_spark_session(self):
        return SparkSession.builder.appName("Dashboard").getOrCreate()

    def load_data(self):
        """Loads Gold layer data."""
        df = self.spark.read.parquet(self.config.paths.gold)
        return df.toPandas()

    def run(self):
        st.set_page_config(page_title="AdTech Metrics", layout="wide")

        st.title("📊 AdTech Real-Time Metrics Dashboard")

        st.sidebar.header("Controls")

        if st.sidebar.button("🔄 Refresh Data"):
            st.experimental_rerun()

        try:
            df = self.load_data()

            if df.empty:
                st.warning("No data available yet.")
                return

            # --------------------------
            # KPIs
            # --------------------------
            total_revenue = df["total_revenue"].sum()
            total_events = df["total_events"].sum()

            col1, col2 = st.columns(2)

            col1.metric("Total Revenue", f"${total_revenue:.2f}")
            col2.metric("Total Events", int(total_events))

            st.divider()

            # --------------------------
            # Table
            # --------------------------
            st.subheader("Campaign Metrics")
            st.dataframe(df)

            # --------------------------
            # Ranking
            # --------------------------
            st.subheader("Top Campaigns by Revenue")

            df_sorted = df.sort_values("total_revenue", ascending=False)

            st.bar_chart(df_sorted.set_index("campaign_id")["total_revenue"])

        except Exception as e:
            st.error(f"Error loading data: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)

    args = parser.parse_args()

    config = AppConfig.from_yaml(args.config)

    dashboard = Dashboard(config)
    dashboard.run()
