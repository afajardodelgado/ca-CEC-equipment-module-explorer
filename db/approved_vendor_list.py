import os
import sqlite3
import pandas as pd

def get_db_path():
    """Get the path to the database file"""
    db_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(db_dir, 'approved_vendor_list.db')

def create_approved_vendor_list_table():
    """Create the approved_vendor_list table if it doesn't exist"""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        
        # Create approved_vendor_list table with standardized columns
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS approved_vendor_list (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_category TEXT,
            manufacturer TEXT,
            technology_type TEXT,
            model_sku TEXT,
            product_model_description TEXT,
            racking_system_name TEXT,
            power_rating_specification TEXT,
            module_level_power_electronics TEXT,
            system_configuration TEXT,
            racking_style TEXT,
            internal_notes TEXT,
            additional_notes TEXT,
            date_added TEXT
        )
        ''')
        conn.commit()

def save_approved_vendor_list_data(df):
    """Save approved vendor list data from DataFrame to database"""
    create_approved_vendor_list_table()
    
    with sqlite3.connect(get_db_path()) as conn:
        # Map DataFrame columns to database columns
        item_data = []
        
        # Handle column name case sensitivity and normalize column names
        column_mapping = {}
        for col in df.columns:
            # Create a case-insensitive mapping
            normalized_col = col.lower().strip()
            if normalized_col == 'equipment category':
                column_mapping[col] = 'Equipment Category'
            elif normalized_col == 'manufacturer':
                column_mapping[col] = 'Manufacturer'
            elif normalized_col == 'technology type':
                column_mapping[col] = 'Technology Type'
            elif normalized_col == 'model sku':
                column_mapping[col] = 'Model SKU'
            elif normalized_col == 'product model description':
                column_mapping[col] = 'Product Model Description'
            elif normalized_col == 'racking system name':
                column_mapping[col] = 'Racking System Name'
            elif normalized_col == 'power rating specification':
                column_mapping[col] = 'Power Rating Specification'
            elif normalized_col == 'module level power electronics':
                column_mapping[col] = 'Module Level Power Electronics'
            elif normalized_col == 'system configuration':
                column_mapping[col] = 'System Configuration'
            elif normalized_col == 'racking style':
                column_mapping[col] = 'Racking Style'
            elif normalized_col == 'internal notes / memo' or normalized_col == 'internal notes':
                column_mapping[col] = 'Internal Notes / Memo'
            elif normalized_col == 'additional notes':
                column_mapping[col] = 'Additional Notes'
            else:
                column_mapping[col] = col
        
        # Create a new DataFrame with normalized column names
        normalized_df = df.rename(columns=column_mapping)
        
        for _, row in normalized_df.iterrows():
            # Clean and sanitize string values
            def clean_value(val):
                if pd.isna(val):
                    return None
                if isinstance(val, str):
                    # Replace problematic characters
                    return val.strip().replace('\x00', '').replace('\xa0', ' ')
                return val
            
            item = {
                'equipment_category': clean_value(row.get('Equipment Category', None)),
                'manufacturer': clean_value(row.get('Manufacturer', None)),
                'technology_type': clean_value(row.get('Technology Type', None)),
                'model_sku': clean_value(row.get('Model SKU', None)),
                'product_model_description': clean_value(row.get('Product Model Description', None)),
                'racking_system_name': clean_value(row.get('Racking System Name', None)),
                'power_rating_specification': clean_value(row.get('Power Rating Specification', None)),
                'module_level_power_electronics': clean_value(row.get('Module Level Power Electronics', None)),
                'system_configuration': clean_value(row.get('System Configuration', None)),
                'racking_style': clean_value(row.get('Racking Style', None)),
                'internal_notes': clean_value(row.get('Internal Notes / Memo', None)),
                'additional_notes': clean_value(row.get('Additional Notes', None)),
                'date_added': pd.Timestamp.now().strftime('%Y-%m-%d')
            }
            item_data.append(item)
        
        # Insert data into database
        cursor = conn.cursor()
        for item in item_data:
            cursor.execute('''
            INSERT INTO approved_vendor_list (
                equipment_category, manufacturer, technology_type, model_sku,
                product_model_description, racking_system_name, power_rating_specification,
                module_level_power_electronics, system_configuration, racking_style,
                internal_notes, additional_notes, date_added
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['equipment_category'], item['manufacturer'], item['technology_type'],
                item['model_sku'], item['product_model_description'], item['racking_system_name'],
                item['power_rating_specification'], item['module_level_power_electronics'],
                item['system_configuration'], item['racking_style'], item['internal_notes'],
                item['additional_notes'], item['date_added']
            ))
        
        conn.commit()
        return len(item_data)

def load_approved_vendor_list_data():
    """Load approved vendor list data from database into a DataFrame"""
    create_approved_vendor_list_table()
    
    with sqlite3.connect(get_db_path()) as conn:
        query = "SELECT * FROM approved_vendor_list"
        df = pd.read_sql_query(query, conn)
        
        # Remove item_id column from display if it exists
        if 'item_id' in df.columns:
            df = df.drop('item_id', axis=1)
            
        # Ensure column names match the standardized format
        standard_columns = [
            'equipment_category', 'manufacturer', 'technology_type', 'model_sku',
            'product_model_description', 'racking_system_name', 'power_rating_specification',
            'module_level_power_electronics', 'system_configuration', 'racking_style',
            'internal_notes', 'additional_notes', 'date_added'
        ]
        
        # Rename columns to title case for display
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
        
        # Rename columns for display
        df = df.rename(columns=column_display_names)
            
        return df

def delete_approved_vendor_list_item(item_id):
    """Delete an approved vendor list item by ID"""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM approved_vendor_list WHERE item_id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0

def drop_approved_vendor_list_data():
    """Drop all data from the approved_vendor_list table"""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM approved_vendor_list")
        conn.commit()
        # Reset the auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='approved_vendor_list'")
        conn.commit()
        return cursor.rowcount
