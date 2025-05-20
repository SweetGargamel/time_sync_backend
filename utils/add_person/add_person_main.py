import json
import json_repair
import time
import pandas as pd
import os
from .Identify_columns import identify_columns_self
from .Identify_nonrepeat_group import identified_nonrepeat_groups

def main(file_path, existing_groups_with_ids: list[dict]):
    """Reads an Excel or CSV file, extracts data, identifies columns, 
    and differentiates new groups from existing ones using their IDs.
    """
    try:
        _, file_extension = os.path.splitext(file_path)
        df = None

        if file_extension.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_extension.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Please upload an Excel (.xlsx, .xls) or CSV (.csv) file.")

        print(df)

        # Extract the first 15 rows (all columns)
        first_15_rows_df = df.iloc[:15, :]  # :15 表示前15行，冒号表示所有列

        if not first_15_rows_df.empty:
            # Convert dataframe to list of lists for the LLM
            header = first_15_rows_df.columns.tolist() # Get all column headers
            data_rows = first_15_rows_df.values.tolist() # Get data from the first 15 rows
            data_as_list_of_lists = [header] + data_rows

            print("--- Extracted Data (first 15 rows, all columns, as list of lists) ---")
            # print(data_as_list_of_lists) # Avoid printing large lists to console by default
            for row in data_as_list_of_lists:
                print(row)
            
            id_column_idx,name_column_idx,college_column_idx = identify_columns_self(data_as_list_of_lists)

            print("--- Identified Columns ---")
            print(f"ID Column Index: {id_column_idx}, Name Column Index: {name_column_idx}, College Column Index: {college_column_idx}")

        new_group_names_to_create = []
        groups_from_file_with_db_ids = []
        selected_columns_df = pd.DataFrame()

        # Check if critical columns were identified
        if id_column_idx is None or id_column_idx < 0 or name_column_idx is None or name_column_idx < 0:
            # This case should be caught by the ValueError in identify_columns_self, 
            # but as a safeguard or if identify_columns_self changes:
            raise ValueError("Critical columns (ID or Name) could not be identified.")

        if college_column_idx is not None and college_column_idx != -1:
            if college_column_idx < len(df.columns):
                potential_new_groups = list(set(df.iloc[:, college_column_idx].astype(str).tolist()))
                print("--- Potential New Groups from File ---")
                print(potential_new_groups)

                new_group_names_to_create, groups_from_file_with_db_ids = identified_nonrepeat_groups(
                    new_potential_groups=potential_new_groups,
                    existing_groups_with_ids=existing_groups_with_ids
                )
                print("--- New Group Names to Create (Not in DB) ---")
                print(new_group_names_to_create)
                print("--- Identified Existing Groups from File (with DB IDs) ---")
                print(groups_from_file_with_db_ids)
                print("--- Selected Columns ---")
                print(college_column_idx, name_column_idx, id_column_idx)
                # print(selected_columns_df)
                # Select and rename columns
                selected_columns_df = df.iloc[:, [id_column_idx, name_column_idx, college_column_idx]].copy()
                selected_columns_df.columns = ['person_id', 'person_name', 'group_name']
            else:
                print(f"Warning: college_column index {college_column_idx} is out of bounds.")
                # Proceed as if college_column_idx was -1 if it's out of bounds but not None/-1
                selected_columns_df = df.iloc[:, [id_column_idx, name_column_idx]].copy()
                selected_columns_df.columns = ['person_id', 'person_name']
                selected_columns_df['group_name'] = None # Add placeholder group column
        else: # college_column_idx is -1 or None (though None should be caught by identify_columns_self for college)
            print("--- No College/Group Column Identified or Specified as -1 ---")
            selected_columns_df = df.iloc[:, [id_column_idx, name_column_idx]].copy()
            selected_columns_df.columns = ['person_id', 'person_name']
            selected_columns_df['group_name'] = None # Add placeholder group column

        # Return the new group names, identified existing groups, selected data, and identified columns
        return new_group_names_to_create, groups_from_file_with_db_ids, selected_columns_df, id_column_idx, name_column_idx, college_column_idx

    except FileNotFoundError as e:
        print(f"Error: File not found at {file_path}: {e}")
        raise
    except ValueError as e:
        print(f"A ValueError occurred in add_person_main: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred in add_person_main: {e}")
        raise

import sys # Add missing import

if __name__ == "__main__":
    # Example usage: Replace with an actual file path
    # main("e:\\path\\to\\your\\file.xlsx") 
    # For testing, you might want to pass a file path via command line arguments or hardcode one.
    if len(sys.argv) > 1:
        # This example usage needs to be adapted if you run this script directly,
        # as it now requires existing_groups_with_ids.
        # For testing, you might mock this list.
        mock_existing_groups_with_ids = [{"id": 1, "name": "Existing Group 1"}, {"id": 2, "name": "Existing Group 2"}] # Example
        main(sys.argv[1], mock_existing_groups_with_ids)
    else:
        print("Please provide a file path as a command line argument.")
        # Example: python add_person_main.py your_excel_file.xlsx
        # You can also hardcode a test file path here if needed for development
        # main(r"E:\CodePlace\timesync_backend\data\test_students.xlsx", [{"id": 99, "name": "TestGroup1"}]) # Replace with your test file and mock groups