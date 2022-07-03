# Overview:
transmission_ext is a customizable transmission torrent extension program for use on Linux systems. It is designed to be simple to use but effective in extending options within Transmission, such as monitoring and removing torrents. Transmission_ext uses transmission-remote to add the additional options to Transmission. Transmission can be installed/controlled on any supported Transmission OS, but transmission_ext must run on a Linux OS. All configuration is set up through a simple YAML configuration file.

## Current Options:
* Removing torrents from Transmission and the save directory. 

## Program Highlights:
* Requires no code modifications for use.
* Email supports standard port 25 or TLS.
* The YAML file allows updating on the fly, and each loop will use the updated YAML configuration.

## Setup Recommendations & Setup Hints:
transmission_remove is a middleman automator for use with transmission-remote. You must install transmission-cli (sudo apt install transmission-cli) on your Linux host to use transmission_remove.

Manual Usage Reference:
https://manpages.debian.org/testing/transmission-cli/transmission-remote.1.en.html

A sample settings file is provided to make the configuration smooth. Please, rename the "sample_settings.yaml" to "settings.yaml", and make the tweaks for your environment. The logging section can remain untouched unless further debugging is desired.

# Program Prerequisites:
Use the setup.cfg file to install all requirements. Go to the program's main directory and run "pip install -e ." to install all required prerequisites.

## How to Use:
The sample YAML configuration file has plenty of notes to help explain the setup process. The steps below will explain what needs to be done to get the program running.

    Step 1: For the program to recognize the YAML file, you must copy the sample_settings.yaml file and rename it to settings.yaml 
    Step 2: Update the YAML file with your configuration.
    Step 3: Run the program to make sure your settings are entered correctly. 
    Step 4: Depending on your operating system (Linux Ubuntu explained below), you can set up the program to run automatically, which is recommended. Other Linux versions will work but are not explained below. 
       Step 4.1 (Linux Ubuntu): Set up a service to run the program.
            Step 4.1.1:  Create a new service file.
                Run: cd /lib/systemd/system
                Run: sudo nano transmission_remove.service
                    Note1: The service account needs to have docker socket access. The root user is added below as an example.
                    Note2: A delayed start can help ensure all processes start before monitoring starts. Your "TimeoutStartSec" must be greater than the "ExecStartPre".
                    Paste:
                        Description=transmission_remove
                        After=multi-user.target
                        After=network.target

                        [Service]
                        Type=simple
                        User=root
                        TimeoutStartSec=240
                        ExecStartPre=/bin/sleep 120
                        WorkingDirectory=/<path to program>/transmission_remove/src
                        ExecStart=/usr/bin/python3  /<path to program>/transmission_remove/src/transmission_remove.py                                                         
                        Restart=no

                        [Install]
                        WantedBy=multi-user.target
            Step 4.1.2:  Create a new service file.
                Run: sudo systemctl daemon-reload
            Step 4.1.3: Enable the new service.
                sudo systemctl enable transmission_remove.service
            Step 4.1.4: Start the new service.
                sudo systemctl start transmission_remove.service
            Step 4.1.5: Check the status of the new service.
                sudo systemctl status transmission_remove.service
    Step 5: Verify the program is running as a service or scheduled task. 
    Step 6: Once verified, you should set the logging handler to option 2 and the file's log level to INFO. This will cut down on disk space.
## Troubleshooting:
The YAML file offers DEBUG options to troubleshoot any issues you encounter. Please report any bugs.
