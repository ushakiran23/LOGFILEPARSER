"""
Streamlit Dashboard for Log Parser Visualizations
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import pandas as pd
import json
import os
from src.parser import NginxLogParser
from src.stats import LogStatsCollector

# Configure Streamlit page
st.set_page_config(page_title="Log Parser Visualizer", layout="wide")

# Directory where log files are stored
LOG_DIR = os.path.join(os.path.dirname(__file__), 'tests', 'sample_logs')

def load_log_data(filename):
    """Load and parse log file data"""
    filepath = os.path.join(LOG_DIR, filename)
    log_parser = NginxLogParser()
    stream = log_parser.parse_file(filepath)
    
    # Convert to list for multiple processing
    logs = list(stream)
    return logs

def get_dataframe(logs):
    """Convert parsed logs to DataFrame"""
    if not logs:
        return pd.DataFrame()
    
    df = pd.DataFrame(logs)
    return df

def get_numeric_columns(df):
    """Get columns that can be used for numeric aggregation"""
    numeric_cols = []
    for col in df.columns:
        # Check if column has numeric values
        if df[col].dtype in ['int64', 'float64']:
            numeric_cols.append(col)
        # Also check if it's a column that could be converted
        elif col in ['status', 'bytes']:
            numeric_cols.append(col)
    return numeric_cols

def get_categorical_columns(df):
    """Get columns suitable for grouping/categorical axes"""
    cat_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            cat_cols.append(col)
    return cat_cols

# Main App
st.title("📊 Log Parser Visualizer")
st.markdown("Select your visualization options below")

# Sidebar for file selection
st.sidebar.header("Data Selection")

# Get available log files
log_files = []
if os.path.exists(LOG_DIR):
    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]

if not log_files:
    st.error("No log files found in tests/sample_logs/")
    st.stop()

selected_file = st.sidebar.selectbox("Select Log File", log_files)

# Load data button
if st.sidebar.button("Load Data"):
    st.session_state['data_loaded'] = True
    st.session_state['logs'] = load_log_data(selected_file)
    st.session_state['df'] = get_dataframe(st.session_state['logs'])

# Check if data is loaded
if 'data_loaded' not in st.session_state or not st.session_state.get('data_loaded', False):
    st.info("👈 Select a log file and click 'Load Data' to begin")
    st.stop()

df = st.session_state['df']

if df.empty:
    st.warning("No data to display")
    st.stop()

# Show raw data preview
with st.expander("📋 View Raw Data"):
    st.dataframe(df.head(20))

# Visualization Options
st.header("🎨 Visualization Builder")

col1, col2, col3 = st.columns(3)

with col1:
    chart_types = [
        "Bar Chart", 
        "Line Chart", 
        "Pie Chart", 
        "Area Chart",
        "Scatter Plot",
        "Horizontal Bar Chart"
    ]
    chart_type = st.selectbox("Select Chart Type", chart_types)

with col2:
    x_axis_cols = ["None"] + list(df.columns)
    x_axis = st.selectbox("Select X-Axis", x_axis_cols)

with col3:
    y_axis_cols = ["None"] + get_numeric_columns(df) + get_categorical_columns(df)
    y_axis = st.selectbox("Select Y-Axis (Value)", y_axis_cols)

# Aggregation option
if y_axis and y_axis != "None":
    st.subheader("Aggregation Method")
    agg_method = st.selectbox(
        "How to aggregate the data:",
        ["Count", "Sum", "Mean", "Min", "Max", "Unique"]
    )
    
    # Group by option
    if x_axis and x_axis != "None":
        st.checkbox("Group by X-Axis", value=True, key="group_by")
    else:
        st.session_state['group_by'] = False

# Generate Chart Button
if st.button("Generate Visualization", type="primary"):
    if x_axis == "None" and y_axis == "None":
        st.warning("Please select at least one axis")
    else:
        try:
            # Prepare data for visualization
            if x_axis != "None" and y_axis != "None":
                # Group and aggregate
                if agg_method == "Count":
                    grouped = df.groupby(x_axis).size().reset_index(name='value')
                elif agg_method == "Sum":
                    grouped = df.groupby(x_axis)[y_axis].sum().reset_index(name='value')
                elif agg_method == "Mean":
                    grouped = df.groupby(x_axis)[y_axis].mean().reset_index(name='value')
                elif agg_method == "Min":
                    grouped = df.groupby(x_axis)[y_axis].min().reset_index(name='value')
                elif agg_method == "Max":
                    grouped = df.groupby(x_axis)[y_axis].max().reset_index(name='value')
                elif agg_method == "Unique":
                    grouped = df.groupby(x_axis)[y_axis].nunique().reset_index(name='value')
                
                x_data = grouped[x_axis].astype(str)
                y_data = grouped['value']
                
            elif y_axis != "None":
                # Only Y-axis selected - show distribution
                y_data = df[y_axis]
                x_data = range(len(y_data))
            else:
                # Only X-axis selected - count occurrences
                grouped = df[x_axis].value_counts().reset_index()
                grouped.columns = [x_axis, 'count']
                x_data = grouped[x_axis].astype(str)
                y_data = grouped['count']
            
            # Create chart based on selection
            if chart_type == "Bar Chart":
                st.bar_chart(pd.DataFrame({'Value': y_data.values}, index=x_data.values))
            elif chart_type == "Horizontal Bar Chart":
                chart_data = pd.DataFrame({'Value': y_data.values}, index=x_data.values)
                st.bar_chart(chart_data)
            elif chart_type == "Line Chart":
                st.line_chart(pd.DataFrame({'Value': y_data.values}, index=x_data.values))
            elif chart_type == "Area Chart":
                st.area_chart(pd.DataFrame({'Value': y_data.values}, index=x_data.values))
            elif chart_type == "Pie Chart":
                # Use Altair for pie chart
                import altair as alt
                pie_data = pd.DataFrame({x_axis if x_axis != 'None' else 'Index': x_data, 'Value': y_data})
                st.altair_chart(
                    alt.Chart(pie_data).mark_arc().encode(
                        theta=alt.Theta(field="Value", type="quantitative"),
                        color=alt.Color(field=x_axis if x_axis != 'None' else "Index", type="nominal"),
                        tooltip=[x_axis if x_axis != 'None' else "Index", "Value"]
                    ),
                    use_container_width=True
                )
            elif chart_type == "Scatter Plot":
                import altair as alt
                scatter_data = df[[x_axis, y_axis]].dropna()
                st.altair_chart(
                    alt.Chart(scatter_data).mark_circle(size=60).encode(
                        x=x_axis,
                        y=y_axis,
                        tooltip=[x_axis, y_axis]
                    ).interactive(),
                    use_container_width=True
                )
                
        except Exception as e:
            st.error(f"Error generating chart: {str(e)}")

# Statistics Summary
st.header("📈 Quick Statistics")
if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        if 'ip' in df.columns:
            st.metric("Unique IPs", df['ip'].nunique())
    with col3:
        if 'status' in df.columns:
            st.metric("Unique Status Codes", df['status'].nunique())
