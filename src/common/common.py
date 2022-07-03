# Built-in/Generic Imports
from dataclasses import dataclass


class GeneralTransmissionExtError(Exception):
    """Exception raised for a general remove failure."""

    __module__ = "builtins"
    pass


class TransmissionExtError(Exception):
    """Exception raised for a remove failure."""

    __module__ = "builtins"
    pass


__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2021, common"
__credits__ = ["IncognitoCoding"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "IncognitoCoding"
__status__ = "Development"


@dataclass
class EmailSettings(object):
    """
    Email settings.

    Args:
        smtp (str):
        \t\\- The smtp server or FQDN.
        authentication_required (bool):
        \t\\- Enables if authentication is required.
        use_tls (bool):
        \t\\- Enables TLS.
        username (str):
        \t\\- Username for TLS.
        password (str):
        \t\\- Password for TLS.
        from_email (str):
        \t\\- From email address.
        to_email (str):
        \t\\- To email address.
    """

    __slots__ = (
        "smtp",
        "authentication_required",
        "use_tls",
        "username",
        "password",
        "from_email",
        "to_email",
    )

    smtp: str
    authentication_required: bool
    use_tls: bool
    username: str
    password: str
    from_email: str
    to_email: str


@dataclass
class StartupSettings(object):
    """
    Startup settings from the YAML file.

    Args:
        remove_sleep (int):
        \t\\- The amount of time to sleep between removal checks.
        email_alerts (bool):
        \t\\- Sends email alerts.
        alert_program_errors (bool):
        \t\\- Sends email alerts if an exception is thrown.
        server (str):
        \t\\- Transmission connection details.
        removal_ratio (float):
        \t\\- Set the torrent ratio that needs meet to delete.
        root_download_path (str):
        \t\\- Root path of /downloads.
        email_settings (EmailSettings):
        \t\\- The email settings dataclass.
    """

    __slots__ = (
        "remove_sleep",
        "email_alerts",
        "alert_program_errors",
        "server",
        "removal_ratio",
        "root_download_path",
        "email_settings",
    )

    remove_sleep: int
    email_alerts: bool
    alert_program_errors: bool
    server: str
    removal_ratio: float
    root_download_path: str
    email_settings: EmailSettings
