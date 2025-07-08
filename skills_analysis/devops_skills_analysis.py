"""
This script processes a CSV file containing current skills data, extracts relevant information,
and saves the results to a new CSV file.
The CSV file will have the following information:
  - Name
  - Classification
  - Team
  - Category
  - SubCategory
  - Skill Level Value
  - Skill Level Desc
  - Team Need Value
  - Team Need Desc
"""
import re

# Set the number of characters for column names
CUR_COL_MAPPING = {}
FUT_COL_MAPPING = {}
COMMON_COL_MAPPING = {}
FUT_COLS = {}

OTHER_COL = ["Name", "Classification Level", "What team are you on?"]
# Used to map reported skill levels to numeric values
SKILL_LEVEL_MAP = {
    "None": 0,
    "Novice": 1,
    "Intermediate": 2,
    "Advanced": 3,
    "Expert": 4,
    "N/A": "N/A"
    }

def clean_subcategory(subcategory):
    """
    Remove the examples from the subcategory, extracting just the subcategory.

    Parameter:
      subcategory (str): raw string from header

    Returns:
      subcategory (str): stripped header with just subcategory remaining
    """
    start = "("
    if start in subcategory:
        # split string on "(", and extract everything to the left
        subcategory = subcategory.split(start)[0]
    # remove leading or trailing white space
    subcategory = subcategory.strip()
    return subcategory

def set_common_headers(key, index):
    """
    When a header is hit that may be used by both the future and current skills processes add
    the indexing information to the COMMON_COL_MAPPING global structure.

    Parameters:
      key (str): Found header to be indexed for both processes
      index (int): Position of key in row list
    """
    global COMMON_COL_MAPPING

    if key not in COMMON_COL_MAPPING.keys() and index:
        # if the given key has not already been set add it
        COMMON_COL_MAPPING[key] = index


def set_fut_headers(row, mapping):
    """
    Given the header row of information collect and set the column number that matches the format
    we are looking for. The two strings we are interested in collecting are:
    - Which <CATEGORY> skills would you like to use in your day-to-day work, or feel are underused?
    - Are there <CATEGORY> skills you are interested in learning or continuing to develop?

    Parameters:
      row (list): list of headers to be parsed for indexing
      mapping (dict): Category and subcategory information from mapping_file for team_name
    """
    global FUT_COL_MAPPING
    global FUT_COLS

    use = r"^Which.(.*).skills would you like to use in your day-to-day work,"\
       r" or feel are underused\?$"
    learn = r"^Are there.(.*).skills you are interested in learning or continuing to develop\?$"

    for category in mapping.keys():
        FUT_COL_MAPPING[category] = {
            "USE": None,
            "LEARN": None
        }
        FUT_COLS[category] = {}
        for subcategory in mapping[category]:
            FUT_COLS[category][subcategory] = {
                "USE": 0,
                "LEARN": 0
            }

    for index, col in enumerate(row):
        if col in OTHER_COL:
            set_common_headers(OTHER_COL[OTHER_COL.index(col)], index)
            continue
        use_match = re.search(use, col)
        learn_match = re.search(learn, col)
        # If we get a match for a use column
        if use_match:
            match_category = use_match.groups()[0]
            match_category = match_category.strip()
            FUT_COL_MAPPING[match_category]["USE"] = index
        # If we get a match for a learn column
        if learn_match:
            match_category = learn_match.groups()[0]
            match_category = match_category.strip()
            FUT_COL_MAPPING[match_category]["LEARN"] = index

def str_to_subcategory_list(in_str):
    """
    Take a string of listed subcategories and transform it into a list of cleaned subcategories

    Parameters:
      in_str (str): list of subcategories in string format

    Returns:
      ret_li (list): List version of in_str holding subcategories
    """
    ret_li = []
    if in_str != "":
        in_list = in_str.split(";")
        for ele in in_list:
            if ele == "":
                continue
            ret_li.append(clean_subcategory(ele))

    return ret_li

def create_new_rows(use_li, learn_li, temp_row):
    """
    There is the possibility that additional subcategories were inputted as free form text input.
    In these cases we need to add rows for that subcategory based on the section it was inputted to.
    Additionally, check if the exact subcategory was added to the other list.

    Parameters:
      use_li (list): list of subcategories that were listed as want to use for the current row
      learn_li (list): list of subcategories that were listed as want to learn for the current row
      temp_row (list): templated row with common information prefilled

    Returns:
      rows (list): list of dictionaries of temp_row format. Each unique element from use_li and
        learn_li will create a new dictionary within this list.
    """
    rows = []
    added = []
    for new_subcategory in use_li:
        # If we havent seen this subcategory yet add it
        if new_subcategory in added:
            continue
        cur_row = dict(temp_row)
        cur_row["SubCategory"] = new_subcategory
        cur_row["Use"] = 1

        # check if the subcategory is in the learn list
        if new_subcategory in learn_li:
            cur_row["Learn"] = 1
        else:
            cur_row["Learn"] = 0

        added.append(new_subcategory)
        rows.append(cur_row)

    for sub_category in learn_li:
        # If we havent seen this subcategory yet add it
        if sub_category in added:
            continue
        cur_row = dict(temp_row)
        cur_row["SubCategory"] = sub_category
        cur_row["Learn"] = 1

        # check if the subcategory is in the use list
        if sub_category in use_li:
            cur_row["Use"] = 1
        else:
            cur_row["Use"] = 0

        added.append(sub_category)
        rows.append(cur_row)

    return rows

def row_to_future_skills(row):
    """
    Given a row of data use the FUT_COL_MAPPING glogbal variable to collect the data for all
    category and subcategory data.
    This function will only work if the FUT_COL_MAPPING has already been set. This can be done by
    using the set_fut_headers function.
    This function will set up the output such that the learn and use data is divided by individuals.
    To have the output counts are collated please use row_to_fut_skills_count.

    Parameters:
      row (list): current row to process detailing future skill information

    Returns:
      future_skills (list): created rows from row expanding informaiton on future skills
    """

    future_skills = []
    # common structure to every row. Prefill the common fields.
    skill_dict = {
        "Name": row[COMMON_COL_MAPPING['Name']],
        "Classification": row[COMMON_COL_MAPPING['Classification Level']],
        "Team": row[COMMON_COL_MAPPING['What team are you on?']],
        "Category": None,
        "SubCategory": None,
        "Use": None,
        "Learn": None,
    }

    for ele in FUT_COLS.items():
        category = ele[0]

        # Get the use and learn lists from the row
        use_list = row[FUT_COL_MAPPING[category]["USE"]]
        use_list = str_to_subcategory_list(use_list)
        learn_list = row[FUT_COL_MAPPING[category]["LEARN"]]
        learn_list = str_to_subcategory_list(learn_list)

        # Create template row with category
        cur_row = dict(skill_dict)
        cur_row["Category"] = category

        # Get all rows from use and learn lists
        sub_category_rows = create_new_rows(use_list, learn_list, cur_row)
        future_skills.extend(sub_category_rows)

    return future_skills

def set_cur_headers(row, mapping):
    """
    Given the first row of data collect all the columns that match the format we are looking for.
    The two columns related to current skills match the following structure:
    - How would you describe your current experience or comfort level with <CATEGORY> <SUBCATEGORY>
    - Based on what you know today, what level of <CATEGORY> do you think your
        team will need over the next 12 months? <SUBCATEGORY>
    """
    global CUR_COL_MAPPING
    global COMMON_COL_MAPPING

    # common structure to skill questions for self and team
    self = r"^How would you describe your current experience or comfort level with.(.*)\?\.(.*)$"
    team = r"^Based on what you know today, what level of.(.*).skills do you think your team will"\
       r" need over the next 12 months\?\.(.*)$"

    # create a new structure for holding column numbers for each of the CATEGORY and SUBCATEGORY
    for category in mapping.keys():
        CUR_COL_MAPPING[category] = {}
        for subcategory in mapping[category]:
            CUR_COL_MAPPING[category][subcategory] = {
                "SELF": None,
                "TEAM": None
            }

    for index, col in enumerate(row):
        if col in OTHER_COL:
            set_common_headers(OTHER_COL[OTHER_COL.index(col)], index)
            continue
        self_match = re.search(self, col)
        team_match = re.search(team, col)
        # If we get a match for the self column
        if self_match:
            match_category, match_subcategory = self_match.groups()
            match_category = match_category.strip()
            match_subcategory = clean_subcategory(match_subcategory)
            CUR_COL_MAPPING[match_category][match_subcategory]["SELF"] = index
        if team_match:
            match_category, match_subcategory = team_match.groups()
            match_category = match_category.strip()
            match_subcategory = clean_subcategory(match_subcategory)
            CUR_COL_MAPPING[match_category][match_subcategory]["TEAM"] = index

def row_to_cur_skills(row):
    """
    Convert a row of data into a dictionary containing current skills information.
    Return as a list of dictionaries with the information for each item.

    Parameters:
      row (list): current row to process

    Returns:
      cur_skills (list): list of dictionaries of skills_dict format. Used to capture information
        to rows for output.
    """
    cur_skills = []
    # each output row will have the following structure, fill in the common fields
    skill_dict = {
        "Name": row[COMMON_COL_MAPPING['Name']],
        "Classification": row[COMMON_COL_MAPPING['Classification Level']],
        "Team": row[COMMON_COL_MAPPING['What team are you on?']],
        "Category": None,
        "SubCategory": None,
        "Skill Level Value": None,
        "Skill Level Desc": None,
        "Team Need Value": None,
        "Team Need Desc": None
    }

    for category, value in CUR_COL_MAPPING.items():
        if category in OTHER_COL:
            continue
        for subcategory in value:
            # create a new dict from the template above
            cur_dict = dict(skill_dict)

            # get the values and descriptions for the category and sub category
            self_desc = row[CUR_COL_MAPPING[category][subcategory]["SELF"]]
            if self_desc == "":
                self_desc = "N/A"
            self_value = SKILL_LEVEL_MAP[self_desc]
            team_desc = row[CUR_COL_MAPPING[category][subcategory]["TEAM"]]
            if team_desc == "":
                team_desc = "N/A"
            team_value = SKILL_LEVEL_MAP[team_desc]

            # Set the remaining values in the dictionary
            cur_dict["Category"] = category
            cur_dict["SubCategory"] = subcategory
            cur_dict["Skill Level Value"] = self_value
            cur_dict["Skill Level Desc"] = self_desc
            cur_dict["Team Need Value"] = team_value
            cur_dict["Team Need Desc"] = team_desc

            # add the new dict to the list of dicts
            cur_skills.append(cur_dict)

    return cur_skills
