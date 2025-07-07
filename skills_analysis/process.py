"""
This script is part of the skills analysis library. It serves as the main entry point for
running the skills analysis. The script is designed to be modular, allowing for different
components of the analysis to be executed based on the configuration specified in a JSON file.

Required Files:
- `config.json`: (Required) A JSON file that specifies which components of the analysis to run.
    broken into two parts:
        "input: { "csv_file": file with data to be analyzed,
                  "mapping_file": json file with mapping of categories,
                  "team_name": name of team in mapping file to use }
        "processes": ["process1", "process2", ...] - list of processes to run
            - select from: "mad_libs", "current_skills", "future_skills"
              Each process included will provide an output file with the desired results.
              The output files will be named based on the process name and the input file name.
"""
import json
import utilities
import generate_madlibs_bios as mad_lib
import devops_skills_analysis as skills

CONFIG_PATH = "./config.json"
# defining the possible process that can be run
PROCESSES = ["mad_libs", "current_skills", "future_skills"]
# Making indexing into the process list clearer
MAD_LIB = 0
CUR_SKILLS = 1
FUT_SKILLS = 2

def check_requirements(logger, conf):
    """
    Check if the config file has the required elements.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        conf (dict): Configuration data.

    Returns:
        int: 1 if all required elements are present, 0 otherwise.
    """
    required_keys = ["input", "processes"]
    required_inputs = ["csv_file", "mapping_file", "team_name"]
    missing_elements = []

    for key in required_keys:
        if key not in conf:
            missing_elements.append(key)
    for key in required_inputs:
        if key not in conf["input"]:
            missing_elements.append(f'input: {key}')

    if missing_elements:
        err_str = "Missing required elements in the configuration file:"
        logger.error(f"{err_str} {', '.join(missing_elements)}")
        return 0
    return 1

def parse_config(config_file, logger):
    """
    Parse the configuration file to get the input file and processes to run.

    Parameters:
        config_file (str): Path to the configuration JSON file.
        logger (Logger): Logger instance for logging messages.

    Returns:
        config (dict): Parsed configuration data.
    """
    logger.info("Parsing configuration file...")
    # Default value for config
    config = {}

    # Check if the config file exists
    if not utilities.check_file_exists(config_file):
        message =f"Error: File not found at '{config_file}'. Please check the file path."
        utilities.exit_with_code_message(logger, message=message)

    # open the file and read it into a json object
    with open(config_file, 'r', encoding='utf8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            message = f"Error: Could not decode JSON from '{config_file}'. {e}"
            utilities.exit_with_code_message(logger, message=message)

    # Validate the config file
    config_check = check_requirements(logger, config)
    if config == {} or not config or not config_check:
        message = "Configuration file is empty or missing required elements."
        utilities.exit_with_code_message(logger, message=message)

    # if no issues were hit return the config file as a json object
    logger.info("Configuration file loaded successfully.")
    logger.debug(f"Configuration: {config}")
    return config

def get_team_mapping(logger, config_data):
    """
    Get the team mapping from the configuration data.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        config_data (dict): Parsed configuration data.

    Returns:
        team_mapping (dict): Team mapping information.
    """
    logger.info("Getting team mapping...")
    team_name = config_data["input"]["team_name"]
    mapping_file = config_data["input"]["mapping_file"]

    try:
        map_info = utilities.read_map_file(logger, mapping_file)
    except Exception as e:
        message = f"Error: Could not read mapping file '{mapping_file}'. {e}"
        utilities.exit_with_code_message(logger, message=message)

    team_mapping = map_info.get(team_name, {})
    if not team_mapping:
        message = f"Error: Team '{team_name}' not found in mapping file '{mapping_file}'."
        utilities.exit_with_code_message(logger, message=message)

    logger.debug(f"Team mapping for '{team_name}': {team_mapping}")
    return team_mapping

def load_config_values(logger, config_data):
    """
    Load the configuration values from the parsed config data. Because we have already verified
    that the config file has the required elements we are able to read and store the necessary
    data.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        config_data (dict): Configuration data.

    Returns:
        input_file (string): Path to input file
        team_mapping (string): Only created if current or future skills will be run.
            Path to team category mapping file.
        processes (string): String list of processes to run.
    """
    logger.info("Loading configuration values...")

    # Get the list of processes to run. If none are given default to all processes.
    logger.info("  - Loading processes to run...")
    processes = config_data.get("processes", PROCESSES)
    logger.debug(f"Processes to run: {processes}")
    logger.info("  - Processes loaded")

    # Get the input file path from the config
    logger.info("  - Loading input file...")
    input_file = config_data["input"]["csv_file"]
    if not utilities.check_file_exists(input_file):
        message = f"Error: Input file '{input_file}' not found. Please check the file path."
        utilities.exit_with_code_message(logger, message=message)
    logger.debug(f"  - Input file: {input_file}")
    logger.info("  - Input file verified")

    # Get the team name. If not provided, default to "team_name".
    logger.info("  - Loading team name...")
    team_name = config_data["input"]["team_name"]
    logger.debug(f"Team name: {team_name}")
    logger.info("  - Team name loaded")

    # If we are running current or future skills
    # Get the mapping file path from the config
    team_mapping = None
    if PROCESSES[CUR_SKILLS] in processes or PROCESSES[FUT_SKILLS] in processes:
        logger.info("  - Loading team mapping...")
        team_mapping = get_team_mapping(logger, config_data)
        logger.debug("Team mapping: ", team_mapping)
        logger.info("  - Team mapping loaded")

    return input_file, team_mapping, processes

def process(logger, processes, in_rows, mapping):
    """
    Process the input data based on the specified processes.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        processes (list): List of processes to run.
        in (str): Data read from the input file.
        mapping (dict): Team mapping information.

    Returns:
        Tuple (mad_libs, cur_skills, fut_skills):
          lists of dictionaries to be used as rows for output.
    """
    mad_libs = []
    cur_skills = []
    fut_skills = []

    # Fun status print
    total_rows = len()

    logger.info("Starting processing...")

    for index, row in enumerate(in_rows):
        if row == "":
            continue
        # Update percentage and progress bar
        term_len = utilities.print_percentage(index, total_rows)

        if PROCESSES[MAD_LIB] in processes:
            logger.debug("Running Mad Libs process...")
            if index == 0:
                mad_lib.map_cols(row)
            else:
                new_mad_lib = mad_lib.row_to_madlib(row)
                mad_libs.append(new_mad_lib)

        if PROCESSES[CUR_SKILLS] in processes:
            logger.debug("Running Current Skills process...")
            if index == 0:
                skills.set_cur_headers(row, mapping)
            else:
                new_cur_skills = skills.row_to_cur_skills(row)
                cur_skills.extend(new_cur_skills)

        if PROCESSES[FUT_SKILLS] in processes:
            logger.debug("Running Future Skills process...")
            if index == 0:
                skills.set_fut_headers(row, mapping)
            else:
                future_skills = skills.row_to_future_skills(row)
                fut_skills.extend(future_skills)

    print(f"[{'#'*term_len}] 100%", flush=True)
    logger.info("Processing completed.")

    return (mad_libs, cur_skills, fut_skills)

def write_files(log, files, team_name):
    """
    Given the three lists of dictionaries (mad libs, current skills, and future skills) write to
    each specified file.

    Parameters:
      log (logger): Used to pring information to console
      files (tuple): Containing lists of mad libs, current skills, and future skills output
      team_name (str): Use the team name to create a base file name.
    """
    if files[MAD_LIB]:
        log.info("Writing Mad Libs...")
        madlib_file_name = PROCESSES[MAD_LIB] + "_" + team_name + ".csv"
        file_name = utilities.create_output(files[MAD_LIB], madlib_file_name)
        if file_name == 0:
            utilities.output_failed(log, PROCESSES[MAD_LIB])
        else:
            log.info("Mad Libs file: %s finished.", file_name)

    if files[CUR_SKILLS]:
        log.info("Writing Current Skills...")
        cur_file_name = PROCESSES[CUR_SKILLS] + "_" + team_name + ".csv"
        file_name = utilities.create_output(files[CUR_SKILLS], cur_file_name)
        if file_name == 0:
            utilities.output_failed(log, PROCESSES[CUR_SKILLS])
        else:
            log.info("Current Skills file: %s finished.", file_name)

    if files[FUT_SKILLS]:
        log.info("Writing Future Skills...")
        fut_file_name = PROCESSES[FUT_SKILLS] + "_" + team_name + ".csv"
        file_name = utilities.create_output(files[FUT_SKILLS], fut_file_name)
        if file_name == 0:
            utilities.output_failed(log, PROCESSES[FUT_SKILLS])
        else:
            log.info("Future Skills file: %s finished.", file_name)

def main():
    """
    Main function to run the skills analysis. Based on the `config.json` file different portions
    of the library of scripts will be run.
    """
    # Set up and configure logger
    logger = utilities.setup_logger()

    # Check for config file and parse it
    config_data = parse_config(CONFIG_PATH, logger)

    # Load configuration values
    input_file, team_map, processes = load_config_values(logger, config_data)

    # Read the input file
    input_rows = utilities.read_input_file(input_file, logger)

    output = process(logger, processes, input_rows, team_map)

    # Write the files
    write_files(logger, output, config_data["input"]["team_name"])

if __name__ == '__main__':
    main()
