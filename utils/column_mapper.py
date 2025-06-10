"""
Column Mapping Utility for CSV files

This module provides functionality to map columns from source CSV files to standardized destination columns
for the Solar Equipment Explorer application.
"""

import pandas as pd
import streamlit as st

# Define the standardized destination columns
STANDARD_COLUMNS = [
    "Equipment Category",
    "Manufacturer",
    "Technology Type",
    "Model SKU",
    "Product Model Description",
    "Racking System Name",
    "Power Rating Specification",
    "Module Level Power Electronics",
    "System Configuration",
    "Racking Style",
    "Internal Notes / Memo",
    "Additional Notes"
]

def initialize_column_mapping_state():
    """Initialize session state variables for column mapping"""
    if 'source_df' not in st.session_state:
        st.session_state.source_df = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'mapping_complete' not in st.session_state:
        st.session_state.mapping_complete = False
    if 'mapping_validated' not in st.session_state:
        st.session_state.mapping_validated = False

def reset_column_mapping():
    """Reset column mapping session state"""
    st.session_state.column_mapping = {}
    st.session_state.mapping_complete = False
    st.session_state.mapping_validated = False

def get_sample_data(df, column_name, num_samples=3):
    """Get sample data values from a column"""
    if column_name not in df.columns:
        return []
    
    # Get non-null values if possible
    sample_values = df[column_name].dropna().head(num_samples).tolist()
    
    # If we don't have enough non-null values, just get the first few values
    if len(sample_values) < num_samples:
        sample_values = df[column_name].head(num_samples).tolist()
    
    # Format values for display
    formatted_samples = []
    for val in sample_values:
        if isinstance(val, str):
            # Truncate long strings
            val = val if len(val) < 30 else val[:27] + "..."
        formatted_samples.append(str(val))
    
    return formatted_samples

def validate_mapping(mapping, required_columns=None):
    """
    Validate the column mapping
    
    Args:
        mapping: Dictionary of source to destination column mappings
        required_columns: List of destination columns that must be mapped
        
    Returns:
        tuple: (is_valid, unmapped_required_columns)
    """
    if required_columns is None:
        required_columns = STANDARD_COLUMNS
    
    # Check if all required columns are mapped
    mapped_destinations = set(mapping.values())
    unmapped_required = [col for col in required_columns if col not in mapped_destinations]
    
    is_valid = len(unmapped_required) == 0
    
    return is_valid, unmapped_required

def apply_column_mapping(source_df, mapping):
    """
    Apply column mapping to create a new DataFrame with standardized columns
    
    Args:
        source_df: Source DataFrame
        mapping: Dictionary of source to destination column mappings
        
    Returns:
        DataFrame: New DataFrame with mapped columns
    """
    # Create a new DataFrame with only the mapped columns
    mapped_df = pd.DataFrame()
    
    # Add each mapped column to the new DataFrame
    for source_col, dest_col in mapping.items():
        if source_col in source_df.columns:
            mapped_df[dest_col] = source_df[source_col]
    
    # Add empty columns for any unmapped destination columns
    for col in STANDARD_COLUMNS:
        if col not in mapped_df.columns:
            mapped_df[col] = None
    
    # Ensure columns are in the standard order
    return mapped_df[STANDARD_COLUMNS]

def render_column_mapping_interface(source_df):
    """
    Render the column mapping interface
    
    Args:
        source_df: Source DataFrame with columns to map
        
    Returns:
        bool: True if mapping is complete and applied, False otherwise
    """
    if source_df is None or source_df.empty:
        st.warning("Please upload a CSV file first")
        return False
    
    st.subheader("CSV Column Mapping")
    st.info("Map your CSV columns to the standardized format")
    
    # Initialize session state for column mapping if needed
    initialize_column_mapping_state()
    
    # Store the source DataFrame in session state
    st.session_state.source_df = source_df
    
    # Create two columns for the mapping interface
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("### Source CSV Columns")
        st.markdown("Select which destination column each source column should map to:")
        
        # Display source columns with sample data
        for col in source_df.columns:
            st.markdown(f"**{col}**")
            samples = get_sample_data(source_df, col)
            if samples:
                st.markdown(f"*Sample values: {', '.join(samples)}*")
            
            # Dropdown to select destination column
            dest_options = [""] + STANDARD_COLUMNS
            current_selection = st.session_state.column_mapping.get(col, "")
            
            # If this source column is already mapped to a destination, remove that destination
            # from options for other source columns to enforce one-to-one mapping
            if col not in st.session_state.column_mapping and current_selection == "":
                # Remove destinations that are already mapped by other source columns
                for src, dst in st.session_state.column_mapping.items():
                    if src != col and dst in dest_options:
                        dest_options = [opt for opt in dest_options if opt != dst]
            
            selected_dest = st.selectbox(
                f"Map '{col}' to:",
                dest_options,
                index=dest_options.index(current_selection) if current_selection in dest_options else 0,
                key=f"map_{col}"
            )
            
            # Update the mapping in session state
            if selected_dest:
                st.session_state.column_mapping[col] = selected_dest
            elif col in st.session_state.column_mapping and not selected_dest:
                del st.session_state.column_mapping[col]
            
            st.markdown("---")
    
    with right_col:
        st.markdown("### Destination Columns")
        st.markdown("These are the standardized columns for the approved vendor list:")
        
        # Get current mapping for validation
        current_mapping = st.session_state.column_mapping
        is_valid, unmapped_required = validate_mapping(current_mapping)
        
        # Display destination columns with mapping status
        for dest_col in STANDARD_COLUMNS:
            # Check if this destination is mapped
            mapped_sources = [src for src, dst in current_mapping.items() if dst == dest_col]
            is_mapped = len(mapped_sources) > 0
            
            if is_mapped:
                st.success(f"**{dest_col}**: Mapped from '{mapped_sources[0]}'")
            else:
                st.warning(f"**{dest_col}**: Not mapped yet")
        
        # Display overall mapping status
        st.markdown("---")
        st.markdown("### Mapping Status")
        
        mapped_count = len(set(current_mapping.values()))
        total_count = len(STANDARD_COLUMNS)
        
        st.progress(mapped_count / total_count)
        st.markdown(f"**{mapped_count}** of **{total_count}** destination columns mapped")
        
        if not is_valid:
            st.warning(f"Required columns not yet mapped: {', '.join(unmapped_required)}")
        else:
            st.success("All required columns are mapped!")
            st.session_state.mapping_validated = True
    
    # Add buttons for actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Reset Mapping"):
            reset_column_mapping()
            st.experimental_rerun()
    
    with col2:
        if st.button("Auto-Map Columns"):
            # Try to automatically map columns based on name similarity
            auto_mapping = {}
            for src_col in source_df.columns:
                src_lower = src_col.lower().replace("_", " ")
                for dst_col in STANDARD_COLUMNS:
                    dst_lower = dst_col.lower()
                    # Check if source column name contains destination column name
                    if dst_lower in src_lower or src_lower in dst_lower:
                        # Check if this destination isn't already mapped
                        if dst_col not in auto_mapping.values():
                            auto_mapping[src_col] = dst_col
                            break
            
            # Update session state with auto-mapping
            st.session_state.column_mapping.update(auto_mapping)
            st.experimental_rerun()
    
    with col3:
        # Apply mapping button
        if st.button("Apply Mapping", disabled=not is_valid):
            # Apply the mapping to create a new DataFrame
            mapped_df = apply_column_mapping(source_df, current_mapping)
            
            # Store the mapped DataFrame in session state
            st.session_state.mapped_df = mapped_df
            st.session_state.mapping_complete = True
            
            # Return True to indicate mapping is complete
            return True
    
    # If we get here, mapping is not complete yet
    return st.session_state.mapping_complete
