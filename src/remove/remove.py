"""This module is designed to remove torrents from Transmission after a specified ratio."""
# Built-in/Generic Imports
from dataclasses import asdict
import os
import logging
from typing import Union
from time import sleep
import shutil
import re

# Local Dataclasses
from common.common import StartupSettings

# Local Exceptions
from common.common import TransmissionExtError

# Libraries
from ictoolkit import get_function_name, send_email, start_subprocess, str_to_list
from fchecker.type import type_check

# Exceptions
from fexception import FCustomException


__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2021, remove"
__credits__ = ["IncognitoCoding"]
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "IncognitoCoding"
__status__ = "Development"


def start_remove(startup_settings: StartupSettings):
    """
    Starts the removal of torrents that meet the ratio.

    Args:
        startup_settings (StartupSettings):
        \t\\- The startup settings.

    Raises:
        FTypeError (fexception):
        \t\\- The object value '{startup_settings}' is not an instance of the required class(es) or subclass(es).
        TransmissionExtError:
        \t\\- Transmission Remove was not able to detect an installed version of transmission-remote.
        TransmissionExtError:
        \t\\- The torrent 'name' did not return '1' entry.
        TransmissionExtError:
        \t\\- The torrent 'ratio' did not return '1' entry.
        TransmissionExtError:
        \t\\- The torrent 'progress' did not return '1' entry.
        TransmissionExtError:
        \t\\- The torrent 'stop_location' did not return '1' entry.
        TransmissionExtError:
        \t\\- The torrent 'state' did not return '1' entry.
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"=" * 20 + get_function_name() + "=" * 20)
    # Custom flowchart tracking. This is ideal for large projects that move a lot.
    # For any third-party modules, set the flow before making the function call.
    logger_flowchart = logging.getLogger("flowchart")
    logger_flowchart.debug(f"Flowchart --> Function: {get_function_name()}")

    type_check(value=startup_settings, required_type=StartupSettings)

    # Separate commands must be in a list with each spaced entry on a separate line.
    server_connection = str_to_list(value=f"transmission-remote {startup_settings.server} --list", sep=" ")

    try:
        # Calls function to perform processing task.
        torrents: list = start_subprocess(program_arguments=server_connection).stdout
    except FileNotFoundError as exc:
        if "The system cannot find the file specified" in str(exc):
            exc_args = {
                "main_message": "Transmission Remove was not able to detect an installed version of transmission-remote.",
                "custom_type": TransmissionExtError,
                "expected_result": "Response when running: transmission-remote",
                "returned_result": "The system cannot find the file specified",
                "suggested_resolution": [
                    "Verify you have installed transmission-cli",
                    "Run 'transmission-remote' from the command line and check for usage output.",
                ],
            }
            raise TransmissionExtError(FCustomException(message_args=exc_args))
        else:
            raise

    # Loops through each torrent.
    for torrent_id in torrents:
        # Example Return:
        # - ['NAME', '  Id: 149',
        #    '  Name: Sample.Torrent.Name',
        #    '  Hash: fc298a353253232532541e3ba5adbec712f',
        #    '  Magnet: magnet:?xt=urn:btih:135315sadfa3153151rfasdfasdfadsf2f&dn=Sample.Torrent.Name&tr=https%3A%2F%2Ftracker.13351632.com%2Fannounce.php%3Fpasskey%1532523513243113',
        #    '',
        #    'TRANSFER',
        #    '  State: Idle',
        #    '  Location: /downloads/complete/sonarr',
        #    '  Percent Done: 100%',
        #    '  ETA: 0 seconds (0 seconds)',
        #    '  Download Speed: 0 kB/s',
        #    '  Upload Speed: 0 kB/s',
        #    '  Have: 3.54 GB (3.54 GB verified)',
        #    '  Availability: 100%',
        #    '  Total size: 3.54 GB (3.54 GB wanted)',
        #    '  Downloaded: 3.54 GB',
        #    '  Uploaded: 497.8 MB',
        #    '  Ratio: 0.1',
        #    '  Corrupt DL: None',
        #    '  Peers: connected to 0, uploading to 0, downloading from 0',
        #    '',
        #    'HISTORY',
        #    '  Date added:       Tue Jan 11 14:45:59 2022',
        #    '  Date finished:    Tue Jan 11 15:16:41 2022',
        #    '  Date started:     Sun Jul  3 12:15:27 2022',
        #    '  Latest activity:  Wed Jan 12 07:30:57 2022',
        #    '  Downloading Time: 34 minutes (2091 seconds)',
        #    '  Seeding Time:     20 hours (72465 seconds)',
        #    '', 'ORIGINS',
        #    '  Public torrent: No',
        #    '  Creator: mktorrent 1.0',
        #    '  Piece Count: 1688',
        #    '  Piece Size: 2.00 MiB',
        #    '', 'LIMITS & BANDWIDTH',
        #    '  Download Limit: Unlimited',
        #    '  Upload Limit: Unlimited',
        #    '  Ratio Limit: Default',
        #    '  Honors Session Limits: Yes',
        #    '  Peer limit: 50',
        #    '  Bandwidth Priority: Normal',
        #    '']

        # Required Command: transmission-remote {startup_settings.server} --torrent •{torrent_id}• --info'
        # This converts the command line to a list and inserts the torrent_id line. The torrent_id will
        # stay intact and not get split.
        server_info = str_to_list(
            value=f"transmission-remote {startup_settings.server} --torrent •{torrent_id}• --info", sep=" ", exclude="•"
        )
        torrent_info: list[str] = start_subprocess(program_arguments=server_info).stdout

        # Some torrent_info output may be empty.
        if len(torrent_info) >= 1:
            exc_msg: Union[str, None] = None
            exc_expected_result: Union[str, int, None] = None
            exc_returned_result: Union[str, int, None] = None
            name: str = ""
            ratio: float = 0
            progress: str = ""
            stop_location: str = ""
            state: str = ""

            # Pulls details from the torrent info.
            torrent_name: list[str] = [entry for entry in torrent_info if "Name:" in entry]
            if len(torrent_name) == 1:
                # Replace Example:
                #   Original: Name: TorrentName
                #   Replaced: TorrentName
                name: str = torrent_name[0].strip().replace("Name: ", "")
            else:
                exc_msg = "The torrent 'name' did not return '1' entry."
                exc_expected_result = 1
                exc_returned_result = len(torrent_name)
            torrent_ratio: list[str] = [entry for entry in torrent_info if "Ratio:" in entry]
            if len(torrent_ratio) == 1:
                # Replace Example:
                #   Original: Ratio: 1.3
                #   Replaced: 1.3
                possible_float: str = torrent_ratio[0].strip().replace("Ratio: ", "")
                if "." in possible_float:
                    ratio: float = float(possible_float)
                else:
                    exc_msg = "The torrent 'ratio' line did return a float value."
                    exc_expected_result = "A float value within the string"
                    exc_returned_result = torrent_ratio[0].strip()
            else:
                exc_msg = "The torrent 'ratio' did not return '1' entry."
                exc_expected_result = 1
                exc_returned_result = len(torrent_ratio)
            torrent_progress: list[str] = [entry for entry in torrent_info if "Percent Done:" in entry]
            if len(torrent_progress) == 1:
                # Replace Example:
                #   Original: Percent Done: 100%
                #   Replaced: 100%
                progress: str = torrent_progress[0].strip().replace("Percent Done: ", "")
            else:
                exc_msg = "The torrent 'progress' did not return '1' entry."
                exc_expected_result = 1
                exc_returned_result = len(torrent_progress)
            torrent_stop_location: list[str] = [entry for entry in torrent_info if "Location:" in entry]
            if len(torrent_stop_location) == 1:
                # Replace Example:
                #   Original: Location: /downloads/complete/radarr
                #   Replaced: /downloads/complete/radarr
                stop_location: str = torrent_stop_location[0].strip().replace("Location: ", "")
            else:
                exc_msg = "The torrent 'stop_location' did not return '1' entry."
                exc_expected_result = 1
                exc_returned_result = len(torrent_stop_location)
            torrent_state: list[str] = [entry for entry in torrent_info if "State:" in entry]
            if len(torrent_state) == 1:
                # Replace Example:
                #   Original: State: Idle
                #   Replaced: Idle
                state: str = torrent_state[0].strip().replace("State: ", "")
            else:
                exc_msg = "The torrent 'state' did not return '1' entry."
                exc_expected_result = 1
                exc_returned_result = len(torrent_state)

            # Sets the torrent path.
            torrent_path = os.path.abspath(f"{startup_settings.root_download_path}/{stop_location}/{name}")

            # Checks if an exception needs flagged.
            if exc_msg:
                exc_args = {
                    "main_message": exc_msg,
                    "custom_type": TransmissionExtError,
                    "expected_result": exc_expected_result,
                    "returned_result": exc_returned_result,
                }
                raise TransmissionExtError(FCustomException(message_args=exc_args))

            logger.debug(
                f"A torrent entry was discovered. Below are details about this torrent\n  - Name: {name}\n  - Ratio: {ratio}\n  - Progress: {progress}\n  - Stop Location: {stop_location}\n  - State: {state}"
            )

            # Converts the float values to decimal for compare.
            ratio_to_faction = format(ratio)
            removal_ratio_to_fraction = format(startup_settings.removal_ratio)
            if ratio_to_faction >= removal_ratio_to_fraction or state == "Finished":
                logger.info(
                    f"The torrent ({name}) has reached its share ratio of {startup_settings.removal_ratio}. Removing torrent from transmission and the directory"
                )
                # ########################################################
                # ###########Removes the torrent from transmission########
                # ########################################################
                server_info = str_to_list(
                    value=f"transmission-remote {startup_settings.server} --torrent •{torrent_id}• --remove",
                    sep=" ",
                    exclude="•",
                )
                # Successful Removal Response: ['x.x.x.x:9091/transmission/rpc/ responded: "success"']
                torrent_remove_info: list[str] = start_subprocess(program_arguments=server_info).stdout
                if "success" in str(torrent_remove_info):
                    logger.debug(f"Transmission returned a successful response during the torrent ({name}) removal")
                else:
                    logger.error(f"The torrent ({name}) did not removed from Transmission successfully")
                    # Converts the dataclass to a dictionary.
                    email_settings_asdict: dict = asdict(startup_settings.email_settings)
                    send_email(
                        email_settings=email_settings_asdict,
                        subject="Error: Transmission Torrent Removal Failed",
                        body=f"Transmission did not returned a successful response during the torrent ({name}) removal.\n\nResponse = {torrent_remove_info}",
                    )

                # Sleeps 10 seconds to allow time for delete before validation.
                sleep(10)

                # Calls function to get an updated list of torrents to verify the torrent was removed.
                torrents: list = start_subprocess(program_arguments=server_connection).stdout
                if any(torrent for torrent in torrents if torrent == torrent_id):
                    logger.error(f"The torrent ({name}) did not removed from Transmission successfully")
                    # Converts the dataclass to a dictionary.
                    email_settings_asdict: dict = asdict(startup_settings.email_settings)
                    send_email(
                        email_settings=email_settings_asdict,
                        subject="Error: Transmission Torrent Removal Failed",
                        body=f"The torrent ({name}) did not removed from Transmission successfully. Manually intervention is required.",
                    )
                else:
                    logger.info(f"The torrent ({name}) removed from Transmission successfully")

                # ########################################################
                # ######Removes the torrent files from the directory######
                # ########################################################
                logger.debug(f"Removing torrent from complete path: {torrent_path}")
                # Checks if the torrent folder exists.
                if not os.path.exists(torrent_path):
                    logger.warn(f"The torrent path ({torrent_path}) does not exist. No removal required")
                    # Converts the dataclass to a dictionary.
                    email_settings_asdict: dict = asdict(startup_settings.email_settings)
                    send_email(
                        email_settings=email_settings_asdict,
                        subject="Torrent Missing",
                        body=f"The torrent path ({torrent_path}) did not exist. No removal required",
                    )
                else:
                    logger.debug(f"The torrent path ({torrent_path}) exist. Removing the torrent folder")

                    # Removes the torrent folder.
                    shutil.rmtree(path=torrent_path)

                # Sleeps 10 seconds to allow time for delete before validation.
                sleep(10)

                # ########################################################
                # #####Verifies the torrent removed from the directory####
                # ########################################################
                logger.debug(f"Verifing the torrent folder was removed")
                # Checks if the torrent folder exists.
                if not os.path.exists(torrent_path):
                    logger.info(f"The torrent path ({torrent_path}) removed successfully")
                else:
                    logger.error(f"The torrent path ({torrent_path}) still exist. Removing the torrent folder failed")
                    # Converts the dataclass to a dictionary.
                    email_settings_asdict: dict = asdict(startup_settings.email_settings)
                    send_email(
                        email_settings=email_settings_asdict,
                        subject="Error: Torrent Folder Removal Failed",
                        body=f"The torrent ({name}) folder did not removed from the directory ({torrent_path}) successfully. Manually intervention is required.",
                    )
        else:
            logger.debug("No usable torrent info provided. Skipping this entry")
