"""
This module contains utility functions for data processing, validation and analysis.
It will primarily be used to host common functions that are used across the sill analysis scripts.
"""
import os
import sys
import csv
import json
import logging

# Use this to change the logging level.
# DEBUG (10) will show all messages, INFO (20) will show all info messages and higher,
# WARNING (30) will show warnings and higher, ERROR (40) will show errors and higher.
# CRITICAL (50) will only show critical errors.
LOG_LEVEL = "INFO"

# Getting terminal size for progress printing
TERMINAL_WIDTH = None

def exit_with_code_message(logger, code=50, message="Exiting the program."):
    """
    Exit the program with a specific exit code and print a message to the console.

    Parameters:
        logger (Logger): Logger instance to log the message.
        code (int): The exit code to use when exiting the program.
            default is 50 such that a critical error is logged.
        message (str): The message to print to the console before exiting.
            If no massage is passed in the default is "Exiting the program."
    """
    # Log the message based on the exit code level
    if code <= 10:
        logger.debug(message)
    elif code <= 20:
        logger.info(message)
    elif code <= 30:
        logger.warning(message)
    elif code <= 40:
        logger.error(message)
    else:
        logger.critical(message)

    sys.exit(code)

def setup_logger():
    """
    Set up logging for the skills analysis script. Uses global LOG_LEVEL to determine
    the logging level. Sets logger format to "<log_level>:<message>"
    Using this function ensures that every log created will use the same formatting.

    Returns:
        logger (Logger): Configured logger instance.
    """
    # Set up the logger
    logger = logging.getLogger(__name__)
    # print anything info level or higher to console
    logging.basicConfig(format='%(levelname)s: %(message)s', level=LOG_LEVEL)
    logger.info("Starting skills analysis...")

    return logger

def check_file_exists(file_path):
    """
    Check if a file exists at the given path.

    Parameters:
        file_path (str): Path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)

def set_terminal_width():
    """
    Set the terminal width for progress printing.
    This function is used to adjust the terminal width based on the current terminal size.
    """
    global TERMINAL_WIDTH
    buffer = 7
    try:
        TERMINAL_WIDTH = (os.get_terminal_size().columns // 2) - buffer
    except OSError:
        # If we can't get the terminal size, default to a reasonable width
        TERMINAL_WIDTH = 80

def print_percentage(num, total):
    """
    Print a percentage progress indicator to the console.
    This function will only work if the loop it is called in has no other print statements.

    Parameters:
        num (int): The current count.
        total (int): The total count to reach.

    Returns:
        int: The terminal width used for the progress bar.
    """
    if TERMINAL_WIDTH is None:
        set_terminal_width()
    percentage = (num / total) * 100
    term_complete = round((num / total) * TERMINAL_WIDTH)
    term_uncomplete = TERMINAL_WIDTH - term_complete
    percentage_str = f"{percentage:.2f}%"
    term_str = f"[{'#' * term_complete}{'.' * term_uncomplete}]"

    # print percentage bar. Use carriage return to start the next print statement on the same line
    print(f"{term_str} {percentage_str}", end='\r', flush=True)

    return TERMINAL_WIDTH

def read_input_file(input_file, logger):
    """
    Read the input CSV file and return its content. If an error occurs the program will exit.
    The Excel file created by the Form seems to consist of various encodings. The majority of
    characters are correctly decoded using utf-8-sig, the only character that is uncaught is
    '\xa0' a Unicode non breaking space. The replace method is used on lines as they are read in
    from the input file to ensure they are replaced correctly.
    The contents of this function are wrapped in a try except block - this will allow the function
    to exit gracefully if any other character is read that cant be parsed.

    Parameters:
        input_file (str): Path to the input CSV file.
        logger (Logger): Logger instance for logging messages.

    Returns:
        data (list): Rows from the input CSV file.
    """
    logger.info("Reading input file...")
    try:
        with open(input_file, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            data = []
            for row in reader:
                decoded_row = []
                for cell in row:
                    new_cell = cell.replace('\xa0', ' ').strip()
                    decoded_row.append(new_cell)
                data.append(decoded_row)
            logger.info("Input file read successfully.")

    except Exception as e:
        message = f"Error reading input file '{input_file}': {e}"
        exit_with_code_message(logger, message=message)

    return data

def read_map_file(logger, map_file_path):
    """
    Read the mapping file and return the mapping data.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        map_file_path (str): Path to the mapping JSON file.

    Returns:
        map_data (dict): Parsed mapping data.
    """
    logger.info("Loading mapping file...")
    if not check_file_exists(map_file_path):
        message = f"Error: Mapping file '{map_file_path}' not found. Please check the file path."
        exit_with_code_message(logger, message=message)

    with open(map_file_path, 'r', encoding='utf8') as f:
        map_data = json.load(f)
        logger.info("Mapping file loaded successfully.")

    return map_data

def output_failed(log, process):
    """
    Report a warning if the file was unable to be created.

    Parameters:
      log (logger): used to print information to console
      process (str): information on which file was unable to be created
    """
    log.warn("Unable to create output file for %s", process)
    log.warn("Please ensure there are less than 100 versions for this file.")

def create_output(data, filename):
    """
    Given a list of dicts and a fileneme attempt to create and save a CSV file with that name
    If the file already exists try appending a number to the end of the filename until an
    available filename is found. Print the name of the file to the console.

    Parameters:
        data (list): The data to be saved.
        filename (str): Base name for the output CSV file.

    Returns:
        filename (str): The name of the saved CSV file,
                        or 0 if the file could not be saved.
    """
    # Attempt to get a filename that currently does not exist
    version = 1
    while check_file_exists(filename) and version < 100:
        # If the file already exists, append a version number to the filename
        filename = f"{filename.split('.')[0]}_{version}.csv"
        version += 1
    if version >= 100:
        return 0

    with open(filename, 'w', encoding='utf-8', newline='') as out:
        headers = data[0].keys()
        # Save the data to a CSV file
        writer = csv.DictWriter(out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    return filename
