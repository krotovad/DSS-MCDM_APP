"""
Data Handlers module
Contains classes and functions for managing data sources and validation
"""

import csv
import json
import xml.etree.ElementTree as ET
import sqlite3
import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any


class DataManager:
    """
    Centralized class for managing data sources and validation
    """
    
    def __init__(self):
        self.data = None
        self.original_data = None
        self.metadata = {}
        
    def load_from_file(self, file_path: str) -> bool:
        """
        Load data from various file formats
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            if file_path.endswith('.csv'):
                self.data = self._load_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                self.data = self._load_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = self._load_json(file_path)
            elif file_path.endswith('.xml'):
                self.data = self._load_xml(file_path)
            elif file_path.endswith('.db') or file_path.endswith('.sqlite'):
                self.data = self._load_sqlite(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
            self.original_data = self.data.copy()
            return True
        except Exception as e:
            print(f"Error loading file {file_path}: {str(e)}")
            return False
    
    def _load_csv(self, file_path: str) -> List[List[float]]:
        """Load data from CSV file"""
        data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                float_row = []
                for cell in row:
                    try:
                        float_row.append(float(cell))
                    except ValueError:
                        # Skip non-numeric cells
                        float_row.append(0.0)
                data.append(float_row)
        return data
    
    def _load_excel(self, file_path: str) -> List[List[float]]:
        """Load data from Excel file"""
        df = pd.read_excel(file_path, header=None)
        # Convert to numeric, replacing non-numeric values with NaN, then fill with 0
        df = pd.to_numeric(df.stack(), errors='coerce').unstack().fillna(0.0)
        return df.values.tolist()
    
    def _load_json(self, file_path: str) -> List[List[float]]:
        """Load data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        # Handle different JSON structures
        if isinstance(raw_data, list):
            if len(raw_data) > 0 and isinstance(raw_data[0], list):
                # Already in matrix format
                data = raw_data
            else:
                # Single array - convert to matrix
                data = [raw_data]
        else:
            # Object format - extract values
            data = [list(raw_data.values())] if isinstance(raw_data, dict) else []
            
        # Convert to float matrix
        result = []
        for row in data:
            float_row = []
            for cell in row:
                try:
                    float_row.append(float(cell))
                except (ValueError, TypeError):
                    float_row.append(0.0)
            result.append(float_row)
        return result
    
    def _load_xml(self, file_path: str) -> List[List[float]]:
        """Load data from XML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        data = []
        # Look for various possible structures
        for element in root:
            if element.tag.lower() in ['row', 'alternative', 'record']:
                row = []
                for subelement in element:
                    try:
                        row.append(float(subelement.text or '0'))
                    except ValueError:
                        row.append(0.0)
                if row:
                    data.append(row)
            elif element.tag.lower() in ['value', 'cell', 'criterion']:
                # Flat structure - treat as single row
                row = []
                for subelement in element:
                    try:
                        row.append(float(subelement.text or '0'))
                    except ValueError:
                        row.append(0.0)
                if row:
                    data.append(row)
                    
        return data
    
    def _load_sqlite(self, file_path: str) -> List[List[float]]:
        """Load data from SQLite database"""
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return []
            
        # Use first table
        table_name = tables[0][0]
        
        # Get all data from the table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert to float matrix
        data = []
        for row in rows:
            float_row = []
            for cell in row:
                try:
                    float_row.append(float(cell))
                except (ValueError, TypeError):
                    float_row.append(0.0)
            data.append(float_row)
            
        return data
    
    def validate_data(self) -> Dict[str, Any]:
        """
        Validate the loaded data
        
        Returns:
            Dictionary with validation results
        """
        if self.data is None:
            return {'valid': False, 'errors': ['No data loaded']}
        
        errors = []
        warnings = []
        
        # Check if data is a non-empty matrix
        if not self.data or not isinstance(self.data, list):
            errors.append('Data is empty or not a list')
        else:
            # Check if all rows have the same length
            if len(set(len(row) for row in self.data)) > 1:
                warnings.append('Rows have different lengths')
                
            # Check for non-numeric values
            for i, row in enumerate(self.data):
                if not isinstance(row, list):
                    errors.append(f'Row {i} is not a list')
                    continue
                    
                for j, val in enumerate(row):
                    if not isinstance(val, (int, float)):
                        errors.append(f'Non-numeric value at [{i}][{j}]: {val}')
        
        # Additional checks
        if not errors:
            # Check if we have at least 2 alternatives and 1 criterion
            if len(self.data) < 2:
                warnings.append('At least 2 alternatives are recommended')
                
            if len(self.data[0]) if self.data else 0 < 1:
                warnings.append('At least 1 criterion is needed')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'shape': (len(self.data), len(self.data[0])) if self.data else (0, 0),
            'has_missing_values': any(any(pd.isna(val) for val in row) for row in self.data) if self.data else False
        }
    
    def clean_data(self, strategy='fill_zero') -> bool:
        """
        Clean the data according to specified strategy
        
        Args:
            strategy: How to handle missing/corrupted values ('fill_zero', 'fill_mean', 'remove_rows')
            
        Returns:
            True if cleaning was successful, False otherwise
        """
        if self.data is None:
            return False
            
        try:
            # Convert to numpy array for easier manipulation
            arr = np.array(self.data, dtype=float)
            
            # Identify problematic values
            mask = np.isnan(arr) | np.isinf(arr)
            
            if not np.any(mask):
                # No cleaning needed
                return True
                
            if strategy == 'fill_zero':
                arr[mask] = 0.0
            elif strategy == 'fill_mean':
                # Fill each column separately
                for j in range(arr.shape[1]):
                    col = arr[:, j]
                    col_mask = np.isnan(col) | np.isinf(col)
                    if np.any(col_mask):
                        # Calculate mean of valid values in the column
                        valid_vals = col[~col_mask]
                        if len(valid_vals) > 0:
                            fill_val = np.mean(valid_vals)
                            arr[col_mask, j] = fill_val
                        else:
                            arr[col_mask, j] = 0.0
            elif strategy == 'remove_rows':
                # Remove any rows that contain invalid values
                valid_rows = ~np.any(mask, axis=1)
                arr = arr[valid_rows]
            else:
                raise ValueError(f"Unknown cleaning strategy: {strategy}")
                
            # Update data
            self.data = arr.tolist()
            return True
        except Exception as e:
            print(f"Error during data cleaning: {str(e)}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save data to various file formats
        
        Args:
            file_path: Path to save the file
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            if file_path.endswith('.csv'):
                self._save_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self._save_excel(file_path)
            elif file_path.endswith('.json'):
                self._save_json(file_path)
            elif file_path.endswith('.xml'):
                self._save_xml(file_path)
            elif file_path.endswith('.db') or file_path.endswith('.sqlite'):
                self._save_sqlite(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
            return True
        except Exception as e:
            print(f"Error saving file {file_path}: {str(e)}")
            return False
    
    def _save_csv(self, file_path: str):
        """Save data to CSV file"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in self.data:
                writer.writerow(row)
    
    def _save_excel(self, file_path: str):
        """Save data to Excel file"""
        df = pd.DataFrame(self.data)
        df.to_excel(file_path, index=False, header=False)
    
    def _save_json(self, file_path: str):
        """Save data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _save_xml(self, file_path: str):
        """Save data to XML file"""
        root = ET.Element("data")
        
        for i, row in enumerate(self.data):
            row_elem = ET.SubElement(root, "row", id=str(i))
            for j, val in enumerate(row):
                val_elem = ET.SubElement(row_elem, "value", col=str(j))
                val_elem.text = str(val)
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def _save_sqlite(self, file_path: str):
        """Save data to SQLite database"""
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Create table
        n_cols = len(self.data[0]) if self.data else 0
        columns_def = ', '.join([f'col_{i} REAL' for i in range(n_cols)])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS data_matrix ({columns_def})")
        
        # Insert data
        for row in self.data:
            placeholders = ', '.join(['?' for _ in row])
            cursor.execute(f"INSERT INTO data_matrix VALUES ({placeholders})", row)
        
        conn.commit()
        conn.close()


def load_data_from_file(file_path: str) -> Union[List[List[float]], None]:
    """
    Convenience function to load data from a file
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        Loaded data or None if loading failed
    """
    dm = DataManager()
    if dm.load_from_file(file_path):
        return dm.data
    return None


def validate_data_matrix(data: List[List[float]]) -> Dict[str, Any]:
    """
    Validate a data matrix
    
    Args:
        data: Data matrix to validate
        
    Returns:
        Dictionary with validation results
    """
    dm = DataManager()
    dm.data = data
    return dm.validate_data()


def clean_data_matrix(data: List[List[float]], strategy: str = 'fill_zero') -> List[List[float]]:
    """
    Clean a data matrix
    
    Args:
        data: Data matrix to clean
        strategy: Cleaning strategy
        
    Returns:
        Cleaned data matrix
    """
    dm = DataManager()
    dm.data = data
    dm.clean_data(strategy)
    return dm.data