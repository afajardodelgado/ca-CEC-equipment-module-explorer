import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from db.approved_vendor_list import save_approved_vendor_list_data, load_approved_vendor_list_data, delete_approved_vendor_list_item

# Set page configuration
st.set_page_config(
    page_title="Solar Equipment Explorer",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a minimalist aesthetic
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton button {
        background-color: #343a40;
        color: white;
    }
    .stDataFrame {
        padding: 10px;
    }
    h1, h2, h3 {
        color: #343a40;
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        justify-content: flex-start;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        padding: 15px 30px;
        min-width: 250px;
        font-size: 20px;
        font-weight: 400;
        color: #666;
        border: 1px solid #eee;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
        border-bottom: 3px solid #4e8df5;
        font-weight: 700;
        color: #333;
    }
    .stat-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .stat-box {
        background-color: white;
        border-radius: 5px;
        padding: 15px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: 30%;
        text-align: center;
    }
    .stat-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Add custom CSS to make the search bar narrower and style the refresh button
st.markdown("""
<style>
    /* Make the search input narrower */
    [data-testid="stTextInput"] {
        max-width: 250px;
    }
    
    /* Style the refresh button to look like the screenshot */
    [data-testid="stButton"] button {
        background-color: #f8f9fa;
        color: #6c757d;
        border: 1px solid #e0e0e0;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        padding: 0;
        font-size: 14px;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 0;
        box-shadow: none;
    }
    
    /* Hover effect for refresh button */
    [data-testid="stButton"] button:hover {
        background-color: #f0f0f0;
        border-color: #d0d0d0;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("☀️ Solar Equipment Explorer")

# Define base directory for database files
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Function to get database path
def get_db_path(db_name):
    return str(BASE_DIR / 'db' / db_name)


# Function to load PV module data
@st.cache_data
def load_pv_data():
    with sqlite3.connect(get_db_path('pv_modules.db')) as conn:
        query = "SELECT * FROM pv_modules"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['CEC Listing Date', 'Last Update', 'Date Added to Tool']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load inverter data
@st.cache_data
def load_inverter_data():
    with sqlite3.connect(get_db_path('inverters.db')) as conn:
        query = "SELECT * FROM inverters"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Grid Support Listing Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load energy storage data
@st.cache_data
def load_energy_storage_data():
    with sqlite3.connect(get_db_path('energy_storage.db')) as conn:
        query = "SELECT * FROM energy_storage"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Energy Storage Listing Date', 'Certificate Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load battery data
@st.cache_data
def load_battery_data():
    with sqlite3.connect(get_db_path('batteries.db')) as conn:
        query = "SELECT * FROM batteries"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Battery Listing Date', 'Certificate Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load meter data
@st.cache_data
def load_meter_data():
    with sqlite3.connect(get_db_path('meters.db')) as conn:
        query = "SELECT * FROM meters"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Meter Listing Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Create main tabs for California CEC and Approved Vendor List
main_tab1, main_tab2 = st.tabs(["California CEC", "Approved Vendor List"])

# California CEC Tab with subtabs for equipment types
with main_tab1:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["PV Modules", "Grid Support Inverter List", "Energy Storage Systems", "Batteries", "Meters"])

# Function to run the appropriate downloader script based on equipment type
def run_downloader(equipment_type):
    try:
        # Determine which script to run based on equipment type
        if equipment_type == "PV Modules":
            script_path = str(BASE_DIR / "modules" / "pv_module_downloader.py")
        elif equipment_type == "Grid Support Inverter List":
            script_path = str(BASE_DIR / "inverters" / "inverter_downloader.py")
        elif equipment_type == "Energy Storage Systems":
            script_path = str(BASE_DIR / "storage" / "energy_storage_downloader.py")
        elif equipment_type == "Batteries":
            script_path = str(BASE_DIR / "batteries" / "battery_downloader.py")
        elif equipment_type == "Meters":
            script_path = str(BASE_DIR / "meters" / "meter_downloader.py")
        else:
            st.error(f"Unknown equipment type: {equipment_type}")
            return False
        
        # Check if the script exists
        if not os.path.exists(script_path):
            st.error(f"Downloader script not found: {script_path}")
            return False
        
        # Run the script using subprocess with the correct Python executable
        python_executable = sys.executable
        result = subprocess.run([python_executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              check=False)
        
        if result.returncode == 0:
            st.success(f"Successfully updated {equipment_type} database.")
            # Clear cache to force reload of data
            st.cache_data.clear()
            return True
        else:
            st.error(f"Error updating {equipment_type} database: {result.stderr}")
            with st.expander("View Error Details"):
                st.code(result.stderr)
            return False
    except Exception as e:
        st.error(f"Error running downloader: {str(e)}")
        return False

# Function to display equipment data with consistent formatting
def display_equipment_data(equipment_type, df, id_column, manufacturer_column, model_column, efficiency_column, power_column):
    
    # Display statistics in a consistent format
    # Determine which date column to use based on equipment type
    date_column = None
    if equipment_type == "PV Modules":
        date_column = 'CEC Listing Date'
    elif equipment_type == "Grid Support Inverter List":
        date_column = 'Grid Support Listing Date'
    elif equipment_type == "Energy Storage Systems":
        date_column = 'Energy Storage Listing Date'
    elif equipment_type == "Batteries":
        date_column = 'Battery Listing Date'
    elif equipment_type == "Meters":
        date_column = 'Meter Listing Date'
    
    # Handle the date formatting safely
    latest_listing_date = "N/A"
    if date_column and date_column in df.columns and not df.empty:
        try:
            # Filter out None, 'None', and empty values before finding max date
            valid_dates = df[df[date_column].notna() & 
                             (df[date_column].astype(str) != 'None') & 
                             (df[date_column].astype(str) != '')][date_column]
            
            if not valid_dates.empty:
                max_date = valid_dates.max()
                if isinstance(max_date, str) and len(max_date) > 0:
                    # If it contains time, just take the date part
                    if ' ' in max_date:
                        latest_listing_date = max_date.split(' ')[0]
                    else:
                        latest_listing_date = max_date
                else:
                    latest_listing_date = str(max_date) if max_date else "N/A"
            else:
                latest_listing_date = "N/A"
        except Exception as e:
            print(f"Error processing dates: {e}")
            latest_listing_date = "N/A"
    
    # Format the label based on equipment type
    date_label = "Latest Listing Date"
    if equipment_type == "PV Modules":
        date_label = "Latest CEC Listing Date"
    elif equipment_type == "Grid Support Inverter List":
        date_label = "Latest Grid Support Listing Date"
    elif equipment_type == "Energy Storage Systems":
        date_label = "Latest Energy Storage Listing Date"
    elif equipment_type == "Batteries":
        date_label = "Latest Battery Listing Date"
    elif equipment_type == "Meters":
        date_label = "Latest Meter Listing Date"
    
    st.markdown("""
    <div class="stat-container">
        <div class="stat-box">
            <div class="stat-label">Total Items</div>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Manufacturers</div>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">{}</div>
            <div class="stat-value">{}</div>
        </div>
    </div>
    """.format(
        len(df), 
        df[manufacturer_column].nunique(),
        date_label,
        latest_listing_date
    ), unsafe_allow_html=True)
    
    # Display filtered data
    st.subheader(f"{equipment_type}")
    
    # Create a row with two columns - one for filters on the left and search on the right
    filter_col, search_col = st.columns([1, 1])
    
    # Add a filters button in the left column
    with filter_col:
        with st.expander("Add Filters Here"):
            # Filter by manufacturer
            manufacturers = ["All"] + sorted(df[manufacturer_column].unique().tolist())
            selected_manufacturer = st.selectbox(
                "Manufacturer", 
                manufacturers,
                key=f"manufacturer_select_{equipment_type}"
            )
            
            # Filter by efficiency if available
            if efficiency_column in df.columns:
                try:
                    min_efficiency = float(df[efficiency_column].min())
                    max_efficiency = float(df[efficiency_column].max())
                    efficiency_range = st.slider(
                        f"Efficiency (%)",
                        min_efficiency,
                        max_efficiency,
                        (min_efficiency, max_efficiency),
                        key=f"efficiency_slider_{equipment_type}"
                    )
                except (ValueError, TypeError):
                    st.warning(f"Cannot filter by {efficiency_column} due to data type issues.")
                    efficiency_column = None
    
    # Add a search bar in the right column
    with search_col:
        with st.expander("Add Search Here"):
            tab_search_query = st.text_input(
                f"Search {equipment_type} by {manufacturer_column} or {model_column}", 
                "", 
                placeholder="Enter search term...",
                key=f"search_{equipment_type}"
            )
            
            # Apply search if provided
            if tab_search_query:
                try:
                    # Handle potential errors in string operations
                    search_results = df[df[manufacturer_column].astype(str).str.contains(tab_search_query, case=False, na=False) | 
                                      df[model_column].astype(str).str.contains(tab_search_query, case=False, na=False)]
                    
                    # Only update df if we found results
                    if not search_results.empty:
                        df = search_results
                        st.success(f"Found {len(df)} items matching '{tab_search_query}'")
                    else:
                        st.warning(f"No items found matching '{tab_search_query}'. Showing all items instead.")
                except Exception as e:
                    st.error(f"Search error: {e}. Showing all items instead.")
                    # Keep df as is if there's an error
        
    # Add a simple refresh button aligned far left
    if st.button("⟳", key=f"refresh_button_{equipment_type}", help="Download latest data and refresh"):
        # Set downloading state
        st.session_state[f"downloading_{equipment_type}"] = True
        st.rerun()
    
    # Show downloading spinner below refresh button if downloading
    if st.session_state.get(f"downloading_{equipment_type}", False):
        with st.spinner(f"Downloading latest {equipment_type} data..."):
            # Run the appropriate downloader script
            success = run_downloader(equipment_type)
            # Clear downloading state
            st.session_state[f"downloading_{equipment_type}"] = False
            if success:
                # Clear cache and reload the app
                st.cache_data.clear()
                st.rerun()
    
    st.write(f"Showing {len(df)} items")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_manufacturer != "All":
        filtered_df = filtered_df[filtered_df[manufacturer_column] == selected_manufacturer]
    
    if efficiency_column and efficiency_column in df.columns:
        try:
            filtered_df = filtered_df[
                (filtered_df[efficiency_column].astype(float) >= efficiency_range[0]) &
                (filtered_df[efficiency_column].astype(float) <= efficiency_range[1])
            ]
        except (ValueError, TypeError):
            st.warning(f"Could not apply {efficiency_column} filter due to data type issues.")
    
    # Select columns to display
    all_columns = df.columns.tolist()
    default_columns = [id_column, manufacturer_column, model_column]
    
    # Add equipment-specific columns to defaults
    if equipment_type == "PV Modules":
        # Set specific default columns for PV Modules
        default_columns = ['module_id', 'Manufacturer', 'Model Number', 'CEC Listing Date', 'Technology', 'Nameplate Pmax (W)']
    elif equipment_type == "Grid Support Inverter List":
        # Set specific default columns for Grid Support Inverter List
        default_columns = ['inverter_id', 'Manufacturer Name', 'Model Number1', 'Grid Support Listing Date', 'Description']
    elif equipment_type == "Energy Storage Systems":
        # Set specific default columns for Energy Storage Systems
        default_columns = ['storage_id', 'Manufacturer', 'Model Number', 'Energy Storage Listing Date', 'Chemistry', 'Description', 'PV DC Input Capability', 'Capacity (kWh)', 'Continuous Power Rating (kW)', 'Maximum Discharge Rate (kW)', 'Voltage (Vac)', 'Certifying Entity', 'Certificate Date']
    elif equipment_type == "Batteries":
        # Set specific default columns for Batteries
        default_columns = ['battery_id', 'Manufacturer', 'Model Number', 'Battery Listing Date', 'Chemistry', 'Description', 'Capacity (kWh)', 'Discharge Rate (kW)', 'Round Trip Efficiency (%)', 'Certifying Entity', 'Certificate Date']
    elif equipment_type == "Meters":
        # Set specific default columns for Meters
        default_columns = ['meter_id', 'Manufacturer', 'Model Number', 'Meter Listing Date', 'Display Type', 'PBI Meter', 'Note']
    
    # Keep only columns that exist in the dataframe
    default_columns = [col for col in default_columns if col in all_columns]
    
    selected_columns = st.multiselect(
        "Select columns to display",
        all_columns,
        default=default_columns,
        key=f"columns_{equipment_type}"
    )
    
    if selected_columns:
        st.dataframe(filtered_df[selected_columns], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)
    
    return filtered_df

# PV Modules Tab
with tab1:
    # Load PV module data
    with st.spinner("Loading PV Modules data..."):
        df_pv = load_pv_data()
        filtered_df_pv = display_equipment_data(
            "PV Modules",
            df_pv,
            'module_id',
            'Manufacturer',
            'Model Number',
            'PTC Efficiency (%)',
            'Power Rating (W)'
        )

# Grid Support Inverter List Tab
with tab2:
    # Load Grid Support Inverter data
    with st.spinner("Loading Grid Support Inverter List data..."):
        try:
            df_inv = load_inverter_data()
            filtered_df_inv = display_equipment_data(
                "Grid Support Inverter List",
                df_inv,
                'inverter_id',
                'Manufacturer Name',
                'Model Number1',
                'CEC Weighted Efficiency (%)',
                'Rated Output Power (kW)'
            )
        except Exception as e:
            st.error(f"Error loading inverter data: {e}")

# Energy Storage Systems Tab
with tab3:
    # Load Energy Storage Systems data
    with st.spinner("Loading Energy Storage Systems data..."):
        try:
            df_storage = load_energy_storage_data()
            filtered_df_storage = display_equipment_data(
                "Energy Storage Systems",
                df_storage,
                'storage_id',
                'Manufacturer',
                'Model Number',
                'Round Trip Efficiency (%)',
                'Maximum Discharge Rate (kW)'
            )
        except Exception as e:
            st.error(f"Error loading energy storage data: {e}")
            st.info("To download Energy Storage Systems data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Energy Storage Data"):
                success = run_downloader("Energy Storage Systems")
                if success:
                    st.experimental_rerun()

# Batteries Tab
with tab4:
    # Load Batteries data
    with st.spinner("Loading Batteries data..."):
        try:
            df_battery = load_battery_data()
            filtered_df_battery = display_equipment_data(
                "Batteries",
                df_battery,
                'battery_id',
                'Manufacturer',
                'Model Number',
                'Round Trip Efficiency (%)',
                'Discharge Rate (kW)'
            )
        except Exception as e:
            st.error(f"Error loading battery data: {e}")
            st.info("To download Batteries data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Batteries Data"):
                success = run_downloader("Batteries")
                if success:
                    st.experimental_rerun()

# Meters Tab
with tab5:
    # Load Meters data
    with st.spinner("Loading Meters data..."):
        try:
            df_meter = load_meter_data()
            filtered_df_meter = display_equipment_data(
                "Meters",
                df_meter,
                'meter_id',
                'Manufacturer',
                'Model Number',
                'Display Type',
                'PBI Meter'
            )
        except Exception as e:
            st.error(f"Error loading meter data: {e}")
            st.info("To download Meters data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Meters Data"):
                success = run_downloader("Meters")
                if success:
                    st.experimental_rerun()

# Add visualization section to each tab
def display_visualizations(filtered_df, equipment_type, manufacturer_column, efficiency_column, power_column):
    st.subheader("Data Visualization")
    # Add a unique key for each selectbox based on equipment_type
    chart_type = st.selectbox(
        "Select chart type",
        ["Manufacturer Distribution", "Efficiency Comparison", "Power Comparison"],
        key=f"chart_type_{equipment_type}"
    )
    
    if chart_type == "Manufacturer Distribution":
        # Group manufacturers by count
        manufacturer_counts = filtered_df[manufacturer_column].value_counts().reset_index()
        manufacturer_counts.columns = ['Manufacturer', 'Count']
        
        # Calculate percentage
        total = manufacturer_counts['Count'].sum()
        manufacturer_counts['Percentage'] = (manufacturer_counts['Count'] / total * 100).round(1)
        
        # Keep only top 10 manufacturers, group others
        top_n = 10
        if len(manufacturer_counts) > top_n:
            top_manufacturers = manufacturer_counts.head(top_n).copy()
            other_count = manufacturer_counts.iloc[top_n:]['Count'].sum()
            other_percentage = manufacturer_counts.iloc[top_n:]['Percentage'].sum()
            
            # Add "Other" category
            other_row = pd.DataFrame({
                'Manufacturer': ['Other'],
                'Count': [other_count],
                'Percentage': [other_percentage.round(1)]
            })
            
            manufacturer_counts = pd.concat([top_manufacturers, other_row])
        
        # Sort by percentage descending
        manufacturer_counts = manufacturer_counts.sort_values('Percentage', ascending=True)
        
        # Create a custom color palette - distinct colors for top categories, gray for "Other"
        colors = px.colors.qualitative.Bold[:top_n]
        if len(manufacturer_counts) > top_n:
            colors.append('#CCCCCC')  # Gray for "Other"
        
        # Create horizontal bar chart
        fig = px.bar(
            manufacturer_counts,
            y='Manufacturer',
            x='Percentage',
            title=f'Share of {equipment_type} by Manufacturer (%)',
            color='Manufacturer',
            color_discrete_sequence=colors,
            text='Percentage',
            orientation='h',
            height=500
        )
        
        # Improve layout
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            xaxis_title='Market Share (%)',
            yaxis_title='Manufacturer',
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(range=[0, max(manufacturer_counts['Percentage']) * 1.15])  # Add space for labels
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Efficiency Comparison" and efficiency_column in filtered_df.columns:
        try:
            fig = px.box(
                filtered_df,
                x=manufacturer_column,
                y=efficiency_column,
                title=f'Efficiency Comparison by Manufacturer',
                color=manufacturer_column,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=500
            )
            fig.update_layout(
                xaxis_title='Manufacturer',
                yaxis_title='Efficiency (%)',
                showlegend=False,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create efficiency comparison chart: {e}")
    
    elif chart_type == "Power Comparison" and power_column in filtered_df.columns:
        try:
            fig = px.box(
                filtered_df,
                x=manufacturer_column,
                y=power_column,
                title=f'Power Rating Comparison by Manufacturer',
                color=manufacturer_column,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=500
            )
            fig.update_layout(
                xaxis_title='Manufacturer',
                yaxis_title='Power Rating',
                showlegend=False,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create power comparison chart: {e}")
    
    # Correlation plots are now a separate visualization type

# Function to display correlation plots as a separate visualization type
def display_correlation_plots(filtered_df, equipment_type, manufacturer_column):
    st.subheader("Correlation Analysis")
    
    # Select only numeric columns for correlation
    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        # Add unique keys for each axis selectbox based on equipment_type
        x_axis = st.selectbox("X-axis", numeric_cols, index=0, key=f"corr_x_axis_{equipment_type}")
        y_axis = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1), key=f"corr_y_axis_{equipment_type}")
        
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color=manufacturer_column,
            title=f'{y_axis} vs {x_axis}',
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=500
        )
        
        # Add trendline option
        add_trendline = st.checkbox("Add trendline", key=f"trendline_{equipment_type}")
        if add_trendline:
            fig.update_traces(mode='markers')
            fig.update_layout(
                shapes=[
                    dict(
                        type='line',
                        yref='y', xref='x',
                        x0=filtered_df[x_axis].min(),
                        y0=filtered_df[y_axis].min(),
                        x1=filtered_df[x_axis].max(),
                        y1=filtered_df[y_axis].max(),
                        line=dict(color='rgba(0,0,0,0.5)', width=2, dash='dash')
                    )
                ]
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add correlation coefficient
        if add_trendline:
            corr = filtered_df[[x_axis, y_axis]].corr().iloc[0,1]
            st.info(f"Correlation coefficient between {x_axis} and {y_axis}: {corr:.3f}")
    else:
        st.warning("Not enough numeric columns available for correlation plot.")

# Update the tab content to include visualizations
with tab1:
    # Add visualization section for PV Modules
    display_visualizations(
        filtered_df_pv,
        "PV Modules",
        'Manufacturer',
        'PTC Efficiency (%)',
        'Power Rating (W)'
    )
    
    # Add correlation plots section
    display_correlation_plots(
        filtered_df_pv,
        "PV Modules",
        'Manufacturer'
    )

with tab2:
    # Add visualization section for Grid Support Inverter List
    display_visualizations(
        filtered_df_inv,
        "Grid Support Inverter List",
        'Manufacturer Name',
        'Weighted Efficiency (%)',
        'Maximum Continuous Output Power at Unity Power Factor ((kW))'
    )
    
    # Add correlation plots section
    display_correlation_plots(
        filtered_df_inv,
        "Grid Support Inverter List",
        'Manufacturer Name'
    )

with tab3:
    # Add visualization section for Energy Storage Systems
    display_visualizations(
        filtered_df_storage,
        "Energy Storage Systems",
        'Manufacturer',
        'Chemistry',
        'Maximum Discharge Rate (kW)'
    )
    
    # Add correlation plots section
    display_correlation_plots(
        filtered_df_storage,
        "Energy Storage Systems",
        'Manufacturer'
    )

with tab4:
    # Add visualization section for Batteries
    display_visualizations(
        filtered_df_battery,
        "Batteries",
        'Manufacturer',
        'Round Trip Efficiency (%)',
        'Discharge Rate (kW)'
    )
    
    # Add correlation plots section
    display_correlation_plots(
        filtered_df_battery,
        "Batteries",
        'Manufacturer'
    )

with tab5:
    # Add visualization section for Meters
    display_visualizations(
        filtered_df_meter,
        "Meters",
        'Manufacturer',
        'Display Type',
        'PBI Meter'
    )
    
    # Add correlation plots section
    display_correlation_plots(
        filtered_df_meter,
        "Meters",
        'Manufacturer'
    )

# Add equipment comparison functionality to each tab
def display_comparison(filtered_df, equipment_type, id_column):
    st.subheader(f"{equipment_type} Comparison")
    st.markdown(f"Select {equipment_type.lower()} to compare their specifications side by side.")
    
    # Get list of equipment
    equipment_list = filtered_df[id_column].tolist()
    if len(equipment_list) > 1:
        selected_equipment = st.multiselect(
            f"Select {equipment_type.lower()} to compare",
            equipment_list,
            max_selections=3,
            key=f"compare_{equipment_type}"
        )
        
        if selected_equipment:
            comparison_df = filtered_df[filtered_df[id_column].isin(selected_equipment)]
            
            # Transpose the dataframe for side-by-side comparison
            comparison_df = comparison_df.set_index(id_column).T
            
            st.dataframe(comparison_df, use_container_width=True)
    else:
        st.info(f"Apply filters to see more {equipment_type.lower()} for comparison.")

# Update the tab content to include comparisons
with tab1:
    # Add comparison section for PV Modules
    display_comparison(filtered_df_pv, "PV Modules", 'module_id')

with tab2:
    # Add comparison section for Grid Support Inverter List
    display_comparison(filtered_df_inv, "Grid Support Inverter List", 'inverter_id')

with tab3:
    # Add comparison section for Energy Storage Systems
    display_comparison(filtered_df_storage, "Energy Storage Systems", 'storage_id')

with tab4:
    # Add comparison section for Batteries
    display_comparison(filtered_df_battery, "Batteries", 'battery_id')

with tab5:
    # Add comparison section for Meters
    display_comparison(filtered_df_meter, "Meters", 'meter_id')

# Function to load vendor data
@st.cache_data
def load_approved_vendor_list_data_cached():
    try:
        df = load_approved_vendor_list_data()
        return df
    except Exception as e:
        st.error(f"Error loading approved vendor list data: {str(e)}")
        return pd.DataFrame()

# Approved Vendor List Tab
with main_tab2:
    st.header("Approved Vendor List")
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Approved Vendor List Data")
        
        # Load existing approved vendor list data
        df_existing_avl = load_approved_vendor_list_data_cached()
        
        # File uploader for CSV
        uploaded_file = st.file_uploader("Upload a CSV file with approved vendor list data", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Read the CSV file with error handling for different encodings
                try:
                    # First try UTF-8 encoding
                    df_avl = pd.read_csv(uploaded_file)
                except UnicodeDecodeError:
                    # If UTF-8 fails, try with Latin-1 encoding
                    uploaded_file.seek(0)  # Reset file pointer
                    df_avl = pd.read_csv(uploaded_file, encoding='latin1')
                
                # Display success message
                st.success(f"Successfully uploaded {uploaded_file.name} with {len(df_avl)} records")
                
                # Basic validation of required columns
                required_columns = [
                    "Equipment Category", "Manufacturer", "Technology Type", "Model SKU", 
                    "Product Model Description", "Racking System Name", "Power Rating Specification", 
                    "Module Level Power Electronics", "System Configuration", "Racking Style", 
                    "Internal Notes / Memo", "Additional Notes"
                ]
                missing_columns = [col for col in required_columns if col not in df_avl.columns]
                
                if missing_columns:
                    st.warning(f"The following standardized columns are missing: {', '.join(missing_columns)}")
                    st.info("Your CSV should contain all 12 standardized columns for the approved vendor list")
                
                # Display the dataframe
                st.subheader("Uploaded Approved Vendor List Data")
                st.dataframe(df_avl, use_container_width=True)
                
                # Save button for database
                if st.button("Save to Database"):
                    try:
                        records_added = save_approved_vendor_list_data(df_avl)
                        st.success(f"Successfully saved {records_added} approved vendor list records to the database")
                        st.session_state['avl_data_saved'] = True
                        # Clear the cache to reload data
                        st.cache_data.clear()
                        # Rerun to refresh the page with new data
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error saving to database: {str(e)}")
                
                # Option to download processed data
                csv_data = df_avl.to_csv(index=False)
                st.download_button(
                    label="Download Processed Data",
                    data=csv_data,
                    file_name="processed_approved_vendor_list.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error processing the CSV file: {str(e)}")
                st.info("Please ensure your CSV file is properly formatted")
        else:
            # Show existing data from database
            if not df_existing_avl.empty:
                st.subheader("Existing Approved Vendor List Data")
                st.dataframe(df_existing_avl, use_container_width=True)
                
                # Option to download existing data
                csv_data = df_existing_avl.to_csv(index=False)
                st.download_button(
                    label="Download Existing Data",
                    data=csv_data,
                    file_name="approved_vendor_list_database.csv",
                    mime="text/csv"
                )
            else:
                st.info("Upload a CSV file to see approved vendor list data here.")
                st.markdown("""
                ### Standardized CSV Format
                Your CSV must include the following 12 standardized columns:
                - Equipment Category
                - Manufacturer
                - Technology Type
                - Model SKU
                - Product Model Description
                - Racking System Name
                - Power Rating Specification
                - Module Level Power Electronics
                - System Configuration
                - Racking Style
                - Internal Notes / Memo
                - Additional Notes
                """)
                
                # Add a button to download the sample CSV template
                try:
                    with open('sample_approved_vendor_list.csv', 'r', encoding='utf-8') as f:
                        sample_csv = f.read()
                        
                    st.download_button(
                        label="Download Sample CSV Template",
                        data=sample_csv,
                        file_name="sample_approved_vendor_list.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error loading sample template: {str(e)}")
                    st.info("You can still upload your own CSV file with approved vendor list data.")
    
    with col2:
        st.subheader("Approved Vendor List Information")
        st.info("This section contains approved vendor statistics.")
        
        # Approved vendor list statistics from database
        if not df_existing_avl.empty:
            # Count of items in approved vendor list
            st.metric("Total Items", len(df_existing_avl))
            
            # Count unique equipment categories
            if "Equipment Category" in df_existing_avl.columns:
                unique_categories = df_existing_avl["Equipment Category"].nunique()
                st.metric("Equipment Categories", unique_categories)
            
            # Most common manufacturer if the column exists
            if "Manufacturer" in df_existing_avl.columns and len(df_existing_avl) > 0:
                # Handle potential NaN values
                valid_manufacturers = df_existing_avl["Manufacturer"].dropna()
                if not valid_manufacturers.empty:
                    most_common = valid_manufacturers.value_counts().idxmax()
                    st.metric("Top Manufacturer", most_common)
            
            # Most common technology type
            if "Technology Type" in df_existing_avl.columns and len(df_existing_avl) > 0:
                valid_types = df_existing_avl["Technology Type"].dropna()
                if not valid_types.empty:
                    most_common_tech = valid_types.value_counts().idxmax()
                    st.metric("Top Technology", most_common_tech)
        else:
            st.markdown("""
            ### Approved Vendor List Statistics
            Upload and save approved vendor list data to see statistics here.
            
            You'll be able to:
            - Track total approved vendors
            - View certification statistics
            - Analyze vendor distribution
            """)
            
        # Future features section
        st.markdown("---")
        st.markdown("### Coming Soon")
        st.markdown("""
        - Vendor certification verification
        - Automatic data validation
        - Vendor performance metrics
        - Integration with certification authorities
        """)

# Footer
st.markdown("---")
st.markdown("Data source: California Energy Commission")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")
