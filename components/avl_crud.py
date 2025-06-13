import streamlit as st
import pandas as pd
from db.approved_vendor_list import (
    save_approved_vendor_list_data, 
    load_approved_vendor_list_data, 
    delete_approved_vendor_list_item,
    create_approved_vendor_list_table
)
import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get the path to the database file"""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
    return os.path.join(db_dir, 'approved_vendor_list.db')

def update_avl_record(item_id, updated_data):
    """Update an existing AVL record"""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        
        # Build the UPDATE query dynamically
        update_fields = []
        values = []
        
        field_mapping = {
            'Equipment Category': 'equipment_category',
            'Manufacturer': 'manufacturer',
            'Technology Type': 'technology_type',
            'Model SKU': 'model_sku',
            'Product Model Description': 'product_model_description',
            'Racking System Name': 'racking_system_name',
            'Power Rating Specification': 'power_rating_specification',
            'Module Level Power Electronics': 'module_level_power_electronics',
            'System Configuration': 'system_configuration',
            'Racking Style': 'racking_style',
            'Internal Notes / Memo': 'internal_notes',
            'Additional Notes': 'additional_notes'
        }
        
        for display_name, db_field in field_mapping.items():
            if display_name in updated_data:
                update_fields.append(f"{db_field} = ?")
                values.append(updated_data[display_name])
        
        if update_fields:
            query = f"UPDATE approved_vendor_list SET {', '.join(update_fields)} WHERE item_id = ?"
            values.append(item_id)
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        
        return False

def get_avl_record_by_id(item_id):
    """Get a single AVL record by ID"""
    with sqlite3.connect(get_db_path()) as conn:
        query = "SELECT * FROM approved_vendor_list WHERE item_id = ?"
        df = pd.read_sql_query(query, conn, params=(item_id,))
        
        if not df.empty:
            # Rename columns for display
            column_display_names = {
                'equipment_category': 'Equipment Category',
                'manufacturer': 'Manufacturer',
                'technology_type': 'Technology Type',
                'model_sku': 'Model SKU',
                'product_model_description': 'Product Model Description',
                'racking_system_name': 'Racking System Name',
                'power_rating_specification': 'Power Rating Specification',
                'module_level_power_electronics': 'Module Level Power Electronics',
                'system_configuration': 'System Configuration',
                'racking_style': 'Racking Style',
                'internal_notes': 'Internal Notes / Memo',
                'additional_notes': 'Additional Notes',
                'date_added': 'Date Added'
            }
            df = df.rename(columns=column_display_names)
            return df.iloc[0].to_dict()
        
        return None

def bulk_delete_avl_records(item_ids):
    """Delete multiple AVL records"""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        placeholders = ','.join(['?' for _ in item_ids])
        query = f"DELETE FROM approved_vendor_list WHERE item_id IN ({placeholders})"
        cursor.execute(query, item_ids)
        conn.commit()
        return cursor.rowcount

def bulk_update_avl_records(item_ids, field_name, new_value):
    """Update a specific field for multiple records"""
    field_mapping = {
        'Equipment Category': 'equipment_category',
        'Manufacturer': 'manufacturer',
        'Technology Type': 'technology_type',
        'Model SKU': 'model_sku',
        'Product Model Description': 'product_model_description',
        'Racking System Name': 'racking_system_name',
        'Power Rating Specification': 'power_rating_specification',
        'Module Level Power Electronics': 'module_level_power_electronics',
        'System Configuration': 'system_configuration',
        'Racking Style': 'racking_style',
        'Internal Notes / Memo': 'internal_notes',
        'Additional Notes': 'additional_notes'
    }
    
    if field_name in field_mapping:
        db_field = field_mapping[field_name]
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?' for _ in item_ids])
            query = f"UPDATE approved_vendor_list SET {db_field} = ? WHERE item_id IN ({placeholders})"
            cursor.execute(query, [new_value] + item_ids)
            conn.commit()
            return cursor.rowcount
    
    return 0

def render_avl_crud_interface(category_filter=None):
    """Render the CRUD interface for AVL management"""
    
    # Create a safe key suffix from category filter
    key_suffix = (category_filter or "all").replace(" ", "_").lower()
    
    # Initialize session state
    if f'edit_mode_{key_suffix}' not in st.session_state:
        st.session_state[f'edit_mode_{key_suffix}'] = False
    if f'selected_records_{key_suffix}' not in st.session_state:
        st.session_state[f'selected_records_{key_suffix}'] = []
    if f'bulk_operation_{key_suffix}' not in st.session_state:
        st.session_state[f'bulk_operation_{key_suffix}'] = None
    
    # Load data with ID column
    with sqlite3.connect(get_db_path()) as conn:
        query = "SELECT * FROM approved_vendor_list"
        if category_filter:
            query += f" WHERE equipment_category LIKE '%{category_filter}%'"
        df = pd.read_sql_query(query, conn)
    
    if df.empty:
        st.info("No records found. Upload data to get started.")
        return
    
    # Rename columns for display
    column_display_names = {
        'item_id': 'ID',
        'equipment_category': 'Equipment Category',
        'manufacturer': 'Manufacturer',
        'technology_type': 'Technology Type',
        'model_sku': 'Model SKU',
        'product_model_description': 'Product Model Description',
        'racking_system_name': 'Racking System Name',
        'power_rating_specification': 'Power Rating Specification',
        'module_level_power_electronics': 'Module Level Power Electronics',
        'system_configuration': 'System Configuration',
        'racking_style': 'Racking Style',
        'internal_notes': 'Internal Notes / Memo',
        'additional_notes': 'Additional Notes',
        'date_added': 'Date Added'
    }
    
    df = df.rename(columns=column_display_names)
    
    # CRUD Operations Section
    
    # Operation tabs
    crud_tabs = st.tabs(["View & Edit", "Add New", "Bulk Operations"])
    
    # View & Edit Tab
    with crud_tabs[0]:
        # Search and filter
        search_term = st.text_input("Search records", placeholder="Search by manufacturer, model, etc.", key=f"search_{key_suffix}")
        
        if search_term:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # Replace blue info box with subtle text
        st.markdown(f"<span style='color: var(--secondary-gray); font-size: 0.8rem;'>{len(filtered_df)} of {len(df)} records</span>", unsafe_allow_html=True)
        
        # Display records with selection
        if st.checkbox("Enable selection for bulk operations", key=f"enable_selection_{key_suffix}"):
            # Add checkboxes for selection
            selected_indices = st.multiselect(
                "Select records by ID:",
                options=filtered_df['ID'].tolist(),
                default=st.session_state[f'selected_records_{key_suffix}'],
                key=f"select_records_{key_suffix}"
            )
            st.session_state[f'selected_records_{key_suffix}'] = selected_indices
            
            if selected_indices:
                st.success(f"Selected {len(selected_indices)} records")
        
        # Display the dataframe
        st.dataframe(filtered_df, use_container_width=True)
        
        # Edit individual record
        st.markdown("### Edit Record")
        edit_id = st.number_input("Enter Record ID to edit", min_value=1, step=1, key=f"edit_id_{key_suffix}")
        
        if st.button("Load Record", key=f"load_record_{key_suffix}"):
            record = get_avl_record_by_id(edit_id)
            if record:
                st.session_state[f'edit_record_{key_suffix}'] = record
                st.session_state[f'edit_mode_{key_suffix}'] = True
            else:
                st.error("Record not found")
        
        if st.session_state[f'edit_mode_{key_suffix}'] and f'edit_record_{key_suffix}' in st.session_state:
            record = st.session_state[f'edit_record_{key_suffix}']
            st.markdown(f"**Editing Record ID: {record.get('ID', edit_id)}**")
            
            # Create form for editing
            with st.form(f"edit_form_{key_suffix}"):
                updated_data = {}
                
                # Editable fields
                editable_fields = [
                    'Equipment Category', 'Manufacturer', 'Technology Type',
                    'Model SKU', 'Product Model Description', 'Racking System Name',
                    'Power Rating Specification', 'Module Level Power Electronics',
                    'System Configuration', 'Racking Style', 'Internal Notes / Memo',
                    'Additional Notes'
                ]
                
                for field in editable_fields:
                    current_value = record.get(field, '')
                    updated_data[field] = st.text_input(field, value=current_value or '', key=f"edit_{field.replace(' ', '_').lower()}_{key_suffix}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("Save Changes", type="primary"):
                        if update_avl_record(record.get('ID', edit_id), updated_data):
                            st.success("Record updated successfully!")
                            st.session_state[f'edit_mode_{key_suffix}'] = False
                            st.rerun()
                        else:
                            st.error("Failed to update record")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f'edit_mode_{key_suffix}'] = False
                        st.rerun()
                
                with col3:
                    if st.form_submit_button("Delete Record", type="secondary"):
                        if delete_approved_vendor_list_item(record.get('ID', edit_id)):
                            st.success("Record deleted successfully!")
                            st.session_state[f'edit_mode_{key_suffix}'] = False
                            st.rerun()
                        else:
                            st.error("Failed to delete record")
    
    # Add New Tab
    with crud_tabs[1]:
        st.markdown("### Add New Equipment")
        
        with st.form(f"add_new_form_{key_suffix}"):
            new_data = {}
            
            # Equipment category selection
            equipment_categories = [
                "PV Module", "PV Module + Inverter", "Inverter", 
                "Optimizer", "Battery", "Battery Expansion", 
                "Non-Steel Roof Racking"
            ]
            
            # Pre-select the current category if filtering
            default_category = category_filter if category_filter in equipment_categories else equipment_categories[0]
            new_data['Equipment Category'] = st.selectbox("Equipment Category", equipment_categories, 
                                                         index=equipment_categories.index(default_category))
            new_data['Manufacturer'] = st.text_input("Manufacturer", placeholder="Enter manufacturer name", key=f"new_manufacturer_{key_suffix}")
            new_data['Technology Type'] = st.text_input("Technology Type", placeholder="e.g., Monocrystalline, String Inverter", key=f"new_tech_type_{key_suffix}")
            new_data['Model SKU'] = st.text_input("Model SKU", placeholder="Enter model/SKU", key=f"new_model_sku_{key_suffix}")
            new_data['Product Model Description'] = st.text_area("Product Model Description", placeholder="Detailed description", key=f"new_prod_desc_{key_suffix}")
            new_data['Racking System Name'] = st.text_input("Racking System Name", key=f"new_racking_name_{key_suffix}")
            new_data['Power Rating Specification'] = st.text_input("Power Rating Specification", key=f"new_power_rating_{key_suffix}")
            new_data['Module Level Power Electronics'] = st.text_input("Module Level Power Electronics", key=f"new_module_elec_{key_suffix}")
            new_data['System Configuration'] = st.text_input("System Configuration", key=f"new_sys_config_{key_suffix}")
            new_data['Racking Style'] = st.text_input("Racking Style", key=f"new_racking_style_{key_suffix}")
            new_data['Internal Notes / Memo'] = st.text_area("Internal Notes / Memo", key=f"new_internal_notes_{key_suffix}")
            new_data['Additional Notes'] = st.text_area("Additional Notes", key=f"new_additional_notes_{key_suffix}")
            
            if st.form_submit_button("Add Equipment", type="primary"):
                # Create a DataFrame with the new record
                new_df = pd.DataFrame([new_data])
                
                try:
                    records_added = save_approved_vendor_list_data(new_df)
                    st.success(f"Successfully added {records_added} new equipment!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding equipment: {str(e)}")
    
    # Bulk Operations Tab
    with crud_tabs[2]:
        st.markdown("### Bulk Operations")
        
        if st.session_state[f'selected_records_{key_suffix}']:
            st.markdown(f"<span style='color: var(--secondary-gray); font-size: 0.8rem;'>{len(st.session_state[f'selected_records_{key_suffix}'])} records selected</span>", unsafe_allow_html=True)
            
            operation = st.selectbox(
                "Select bulk operation",
                ["", "Bulk Update Field", "Bulk Delete"],
                key=f"bulk_operation_{key_suffix}"
            )
            
            if operation == "Bulk Update Field":
                field_to_update = st.selectbox(
                    "Select field to update",
                    ['Equipment Category', 'Manufacturer', 'Technology Type',
                     'Power Rating Specification', 'Internal Notes / Memo'],
                    key=f"field_to_update_{key_suffix}"
                )
                
                new_value = st.text_input(f"New value for {field_to_update}", key=f"new_value_{key_suffix}")
                
                if st.button("Apply Bulk Update", type="primary", key=f"apply_bulk_update_{key_suffix}"):
                    if new_value:
                        updated_count = bulk_update_avl_records(
                            st.session_state[f'selected_records_{key_suffix}'],
                            field_to_update,
                            new_value
                        )
                        st.success(f"Updated {updated_count} records!")
                        st.session_state[f'selected_records_{key_suffix}'] = []
                        st.rerun()
                    else:
                        st.error("Please enter a new value")
            
            elif operation == "Bulk Delete":
                st.warning(f"⚠️ This will permanently delete {len(st.session_state[f'selected_records_{key_suffix}'])} records!")
                
                if st.button("Confirm Bulk Delete", type="secondary", key=f"confirm_bulk_delete_{key_suffix}"):
                    deleted_count = bulk_delete_avl_records(st.session_state[f'selected_records_{key_suffix}'])
                    st.success(f"Deleted {deleted_count} records!")
                    st.session_state[f'selected_records_{key_suffix}'] = []
                    st.rerun()
        else:
            st.markdown("<span style='color: var(--secondary-gray); font-size: 0.8rem;'>Select records from the 'View & Edit' tab to perform bulk operations</span>", unsafe_allow_html=True)
    
    # Save/Export Section
    st.markdown("---")
    st.subheader("Save & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export current view
        if st.button("Export Current View to CSV", key=f"export_view_{key_suffix}"):
            csv_data = filtered_df.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"avl_export_{category_filter or 'all'}_{timestamp}.csv",
                mime="text/csv",
                key=f"download_csv_{key_suffix}"
            )
    
    with col2:
        # Backup database
        if st.button("Backup Database", key=f"backup_db_{key_suffix}"):
            # Create a full export of the database
            full_df = load_approved_vendor_list_data()
            backup_data = full_df.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download Backup",
                data=backup_data,
                file_name=f"avl_backup_{timestamp}.csv",
                mime="text/csv",
                key=f"download_backup_{key_suffix}"
            )
