"""
Script used to generate Mad Libs-style bios from a CSV file.
The CSV file is created from exporting data collected by a Microsoft Teams Form.
The Mad Libs output is a new CSV file.
"""
import pandas as pd

# Column names to use for the Mad Libs
COLUMNS = [
    "Name",
    "Your Name",
    "What team are you on?",
    "Adjective (how would you describe yourself?)",
    "Role/Title (Your role or what best describes your work)",
    "Tool/System/Approach (What do you love working with?)",
    "Skill or Strength (What’s something you're great at?)",
    "Biggest Challenge or Growth Area (What do you find tricky?)",
    "Notable Experience or Achievement (Something cool you’ve done)",
    "Favorite Part of Work (What makes your job fun, meaningful, or energizing)"
]
COL_MAPPING = {}

# Mad Libs template
TEMPLATE = "Hi, my name is {Your Name}, and I am on the {What team are you on?} Team. and I am a" \
" {Adjective (how would you describe yourself?)} " \
"{Role/Title (Your role or what best describes your work)} who loves working with " \
"{Tool/System/Approach (What do you love working with?)}. My superpower is" \
" {Skill or Strength (What’s something you're great at?)}, and my biggest challenge is" \
" {Biggest Challenge or Growth Area (What do you find tricky?)}. In the past, I have" \
" {Notable Experience or Achievement (Something cool you’ve done)}, and my favorite part of my" \
" work is {Favorite Part of Work (What makes your job fun, meaningful, or energizing)}!"


def map_cols(header_row):
    """
    Loop through the COLUMNS list getting the index of each.
    Use this to set COL_MAPPING as a dictionary with indexes as keys

    Parameters:
        header_row (List): Header row to be parsed, and indexes stored for later use.
    """
    global COL_MAPPING
    for col in COLUMNS:
        found_col = False
        for header in header_row:
            # loop through header row , if the curent header is in COLUMNS capture its index
            if col in [header]:
                index = header_row.index(header)
                COL_MAPPING[index] = col
                found_col = True
                break
        if not found_col:
            print("MISSING - ", col)

def row_to_madlib(row):
    """
    Convert a row of data into a Mad Libs-style string.
    Return as a dictionary with the name provided from the row.

    Parameters:
        row (Series): The row to analyze from the input object.

    Returns:
        mad_libs_name_data (dict): The full name and the Mad Libs string for the provided row.
    """
    mad_libs_data = {}
    full_name = ""
    for col_num, header in COL_MAPPING.items():
        data = row[col_num]
        mad_libs_data[header] = data

        if header == "Name":
            # Hold the full name
            full_name = str(data)
            continue
    filled_mad_libs = TEMPLATE.format(**mad_libs_data)

    # row structure
    mad_libs_name_data = {"FullName": full_name, "Mad Libs": filled_mad_libs}

    return mad_libs_name_data

def create(df, output_csv_file):
    """
    Main function to create Mad Libs CSV from a dataframe.
    Please use row_to_madlib for processing a single row.

    Parameters:
        input_dataframe (DataFrame): Data read from input file.
        output_csv_file (str): Path to the output CSV file.

    Outputs:
        CSV file with Mad Libs responses.
    """

    mad_libs_list = []

    for row in df.iterrows():
        value = row[1]
        mad_libs_data = {}
        for col in COLUMNS:
            mad_libs_data[col] = value.get(col, "N/A")

        filled_mad_libs = TEMPLATE.format(**mad_libs_data)
        full_name = value.get("Name", "N/A")  # Assuming "Name" is the full name column
        mad_libs_list.append({"FullName": full_name, "Mad Libs": filled_mad_libs})

    output_df = pd.DataFrame(mad_libs_list)
    output_df.to_csv(output_csv_file, index=False, encoding="utf-8")
