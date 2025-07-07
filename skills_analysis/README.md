# Skills Analysis

## Overview

Used to capture work done within and across the DSS DevOps chapter. View the README files within each sub folder for more information on the work held within.

## Directory

| Item                        | Description                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------ |
| `category_mapping.json`     | Categories and subcategories sorted by team name. Used by current and future skills. |
| `devops_skills_analysis.py` | Python functions used to handle processing of current and future skills.             |
| `generate_madlibs_bios.py`  | Python functions used to handle processing of mad libs.                              |
| `process.py`                | Main python script. Handles configuration and flow for all processes.                |
| `README.md`                 | This document                                                                        |
| `template-config.json`      | Use this as a base for each run filling sections with information on current run.    |
| `utilities.py`              | Python functions that can be used in various processes.                              |

## To Run

1. Pull data from skills Form and save as a `.csv` file within this directory
2. Verify that the current team's categories and sub categories have been added to `category_mapping.json`
3. Create a copy of `template-config.json`, save as `config.json`. Replace fields with information as needed.
   1. `input`
      1. `csv_file`: name of extracted skills Form `.csv` file
      2. `mapping_file`: `category_mapping.json`, or if another file was created enter that file name here.
      3. `team_name`: Group name of categories from `mapping_file`. eg. Use `DevOps` to process DevOps categories
   2. `processes`: Enter each process that is desired to run from "mad_libs", "current_skills", "future_skills".
      1. If all processes are wanted leave this empty
4. Navigate to this folder and use command `<python_command> process.py` to run
   1. Replace <python_command> with whatever command you have set to run python scripts. eg. `python3 process.py`
   2. To check a python command try `<python_command> -V`. If the version number is displayed that is a Python command that can be used.

The script will output to console as it is processing.
