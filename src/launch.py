"""
This program is designed as an extension of Transmission options.

Requirements:
    - sudo apt install transmission-remote

Setup Options: 
    - https://manpages.debian.org/testing/transmission-remote/transmission-remote.1.en.html
"""
# Built-in/Generic Imports
from dataclasses import asdict
import os
import pathlib
import logging
from typing import Union
from time import sleep

# Local Functions
from remove.remove import start_remove

# Local Dataclasses
from common.common import StartupSettings, EmailSettings

# Local Exceptions
from common.common import GeneralTransmissionExtError, TransmissionExtError

# Libraries
from ictoolkit import setup_logger_yaml, get_function_name, read_yaml_config, send_email
from fchecker.type import type_check

# Exceptions
from fexception import FCustomException


__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2021, launch"
__credits__ = ["IncognitoCoding"]
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "IncognitoCoding"
__status__ = "Development"


def get_startup_settings() -> StartupSettings:
    """
    This function populates all hard-coded and yaml-configuration variables into a dataclass that is pulled into the main function.
    YAML entry validation checks are performed within this function. No manual configurations are setup within the program. All user
    settings are completed in the "settings.yaml" configuration file.

    Raises:
        FTypeError (fexception):
        \t\\- The object value '{remove_sleep}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{email_alerts}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{alert_program_errors}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{server}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{email_settings}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{smtp}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{authentication_required}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{use_tls}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{username}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{password}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{from_email}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{to_email}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{send_email_template}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{limit_message_detail}' is not an instance of the required class(es) or subclass(es).
        TransmissionExtError:
        \t\\- The 'general' key is missing from the YAML file.
        TransmissionExtError:
        \t\\- The 'connection' key is missing from the YAML file.
        TransmissionExtError:
        \t\\- The 'removal' key is missing from the YAML file.
        TransmissionExtError:
        \t\\- The 'email' key is missing from the YAML file.

    Returns:
        StartupSettings:
        \t\\- The statup settings.
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"=" * 20 + get_function_name() + "=" * 20)
    # Custom flowchart tracking. This is ideal for large projects that move a lot.
    # For any third-party modules, set the flow before making the function call.
    logger_flowchart = logging.getLogger("flowchart")
    logger_flowchart.debug(f"Flowchart --> Function: {get_function_name()}")

    # Initialized an empty dictionary for running variables.
    startup_variables: StartupSettings

    # This is required to start the program. The YAML file is read to set the required variables.
    # No file output or formatted console logging is completed in these variable population sections. Basic print statements will prompt an error.
    # Each configuration section is unique. To make the read easier, each sections will be comment blocked using ############.
    # Gets the config from the YAML file.
    # Gets the main program root directory.
    main_script_path = pathlib.Path.cwd()
    # Sets the reports directory save path.
    settings_path_name = os.path.abspath(f"{main_script_path}/settings.yaml")
    returned_yaml_read_config = read_yaml_config(settings_path_name, "FullLoader")

    # Validates required root keys exist in the YAML configuration.
    missing_key_msg: Union[str, None] = None
    if "general" not in returned_yaml_read_config:
        missing_key_msg = "The 'general' key is missing from the YAML file."
    if "connection" not in returned_yaml_read_config:
        missing_key_msg = "The 'connection' key is missing from the YAML file."
    if "removal" not in returned_yaml_read_config:
        missing_key_msg = "The 'removal' key is missing from the YAML file."
    if "email" not in returned_yaml_read_config:
        missing_key_msg = "The 'email' key is missing from the YAML file."

    if missing_key_msg:
        exc_args = {
            "main_message": missing_key_msg,
            "custom_type": TransmissionExtError,
            "suggested_resolution": "Please verify you have set all required keys and try again.",
        }
        raise TransmissionExtError(FCustomException(message_args=exc_args))
    ##############################################################################
    # Gets the remove sleep settings.
    #
    # Time is in seconds.
    remove_sleep: int = returned_yaml_read_config.get("general", {}).get("remove_sleep")  # type: ignore
    type_check(value=remove_sleep, required_type=int)
    ##############################################################################
    # Gets the option to enable or not enable email alerts.
    email_alerts: bool = returned_yaml_read_config.get("general", {}).get("email_alerts")  # type: ignore
    type_check(value=email_alerts, required_type=bool)
    ##############################################################################
    # Gets the option to enable or not enable program error email alerts.
    #
    alert_program_errors: bool = returned_yaml_read_config.get("general", {}).get("alert_program_errors")  # type: ignore
    type_check(value=alert_program_errors, required_type=bool)
    ##############################################################################
    ##############################################################################
    # Gets the transmission connection values.
    server: str = returned_yaml_read_config.get("connection", {}).get("server")  # type: ignore
    type_check(value=server, required_type=str)
    ##############################################################################
    ##############################################################################
    # Gets the transmission removal values.
    removal_ratio: float = returned_yaml_read_config.get("removal", {}).get("removal_ratio")  # type: ignore
    type_check(value=removal_ratio, required_type=float)
    root_download_path: str = returned_yaml_read_config.get("removal", {}).get("root_download_path")  # type: ignore
    type_check(value=root_download_path, required_type=str)
    ##############################################################################
    # Sets email values.
    smtp: str = returned_yaml_read_config.get("email", {}).get("smtp")  # type: ignore
    authentication_required: bool = returned_yaml_read_config.get("email", {}).get("authentication_required")  # type: ignore
    use_tls: bool = returned_yaml_read_config.get("email", {}).get("use_tls")  # type: ignore
    username: str = returned_yaml_read_config.get("email", {}).get("username")  # type: ignore
    password: str = returned_yaml_read_config.get("email", {}).get("password")  # type: ignore
    from_email: str = returned_yaml_read_config.get("email", {}).get("from_email")  # type: ignore
    to_email: str = returned_yaml_read_config.get("email", {}).get("to_email")  # type: ignore

    type_check(value=smtp, required_type=str)
    type_check(value=authentication_required, required_type=bool)
    type_check(value=use_tls, required_type=bool)
    type_check(value=username, required_type=str)
    type_check(value=password, required_type=str)
    type_check(value=from_email, required_type=str)
    type_check(value=to_email, required_type=str)
    ##############################################################################

    startup_variables = StartupSettings(
        remove_sleep=remove_sleep,
        email_alerts=email_alerts,
        alert_program_errors=alert_program_errors,
        server=server,
        removal_ratio=removal_ratio,
        root_download_path=root_download_path,
        email_settings=EmailSettings(
            smtp=smtp,
            authentication_required=authentication_required,
            use_tls=use_tls,
            username=username,
            password=password,
            from_email=from_email,
            to_email=to_email,
        ),
    )

    logger.debug(f"Returning value(s):\n  - {startup_variables}")

    # Returns the startup settings.
    return startup_variables


def main():
    # ############################################################################################
    # ######################Gets the programs main root directory/YAML File Path##################
    # ############################################################################################
    # Gets the main program root directory.
    main_script_path = pathlib.Path.cwd()

    # Checks that the main root program directory has the correct save folders created.
    # Sets the log directory save path.
    save_log_path = os.path.abspath(f"{main_script_path}/logs")

    # Checks if the save_log_path exists and if not it will be created.
    if not os.path.exists(save_log_path):
        os.makedirs(save_log_path)

    # Sets the log removal to False. Enable True for any debug testing.
    remove_log: bool = False
    if remove_log:
        # Removes existing log files if they exist.
        for file in os.listdir(save_log_path):
            filename = os.fsdecode(file)
            # Gets all log files.
            if filename.endswith(".log") or list(filename)[-1].isdigit():
                log_file_path = os.path.join(save_log_path, filename)
                os.remove(log_file_path)

    # Sets the YAML file configuration location.
    yaml_file_path = os.path.abspath(f"{main_script_path}/settings.yaml")

    try:
        # Calls function to setup the logging configuration with the YAML file.
        setup_logger_yaml(yaml_file_path)
    except FileNotFoundError:
        exc_args = {
            "main_message": "The settings.yaml file was not found.",
            "custom_type": TransmissionExtError,
            "suggested_resolution": "Please verify you renamed the sample_settings.yaml file to settings.yaml and applied updates to the settings.",
        }
        raise TransmissionExtError(FCustomException(message_args=exc_args))

    logger = logging.getLogger(__name__)
    # Custom flowchart tracking. This is ideal for large projects that move a lot.
    # For any third-party modules, set the flow before making the function call.
    logger_flowchart = logging.getLogger("flowchart")
    logger_flowchart.info(f"Flowchart --> Function: {get_function_name()}")

    logger.debug("#" * 80)
    logger.debug(" " * 31 + "Transmission Remove" + " " * 30)
    logger.debug("#" * 80)

    # Calls function to pull in the startup variables.
    startup_variables = get_startup_settings()

    try:
        # Starts the remove.
        start_remove(startup_settings=startup_variables)

        logger.debug(f"{startup_variables.remove_sleep} seconds until next torrent remove check")
        # Sleeps for the amount of seconds set in the YAML file.
        sleep(startup_variables.remove_sleep)
    except Exception as exc:
        # ################################################
        # ############Cataches For Email Alerts###########
        # ################################################
        exc_args: Union[dict, None] = None
        # Raises handled fexception's or creates a general exception depending on what is trigged.
        if "Exception Trace Details:" not in str(exc):
            exc_args = {
                "main_message": f"A general exception trigged while running a remove job. See below for more details.",
                "original_exception": exc,
                "custom_type": GeneralTransmissionExtError,
            }
            exc = GeneralTransmissionExtError(FCustomException(message_args=exc_args))

        # Catches exceptions to email notifications.
        # Checks if program errors get emailed.
        if startup_variables.alert_program_errors:
            # Converts the dataclass to a dictionary.
            email_settings_asdict: dict = asdict(startup_variables.email_settings)

            send_email(
                email_settings=email_settings_asdict,
                subject="Transmission Remove - Exiting Program Error Occurred",
                body=str(exc),
            )

        # Raises the exception based on the thrown a handled fexception or unhandled exception.
        if exc_args:
            logger.error(GeneralTransmissionExtError(exc))
            raise GeneralTransmissionExtError(exc)
        else:
            logger.error(exc)
            raise


# Checks that this is the main program that initiates the classes to start the functions.
if __name__ == "__main__":

    # Prints out at the start of the program.
    print("# " + "=" * 85)
    print("Author: " + __author__)
    print("Copyright: " + __copyright__)
    print("Credits: " + ", ".join(__credits__))
    print("License: " + __license__)
    print("Version: " + __version__)
    print("Maintainer: " + __maintainer__)
    print("Status: " + __status__)
    print("# " + "=" * 85)

    try:
        # Loops to keep the main program active.
        # The YAML configuration file will contain a sleep setting within the main function.
        while True:
            main()
            # 5-second delay sleep to prevent system resource issues if the function fails and the loop runs without any pause.
            sleep(5)
    # Catches ctrl + c
    except KeyboardInterrupt:
        print("\nKeyboard interruption. Exiting...")
        exit()
    # Catches ctrl + z
    # Input box failure (ex: ctrl + z) will throw this exception.
    except EOFError:
        print("Keyboard interruption. Exiting...")
        exit()
