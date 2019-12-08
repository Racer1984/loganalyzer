**Log Analyzer**

**What is it?**

This script tails the log files (files with .log extension) recursively 
in a custom directory (which is hard-coded inside the script), normalizes them 
and outputs to SQL. It is supposed to be running as a systemd daemon.
Optionally, the script can be adjusted to obtain the log directory within 
the systemd unit.
Currently, it supports two versions of the date/time format (for Unix system
logs and for Apache access logs). In case it is necessary to support more, 
the regular expression capturing the date and time must be updated accordingly.


**Installation**

**pytholog.py** - Python script (Python3) for collecting and parsing log files.
**storages.py** - classes which represent the database connection objects.

Clone these files to /opt directory.

Create a service file for systemd:
 sudo vi /usr/lib/systemd/system/pytholog.service
 
Add the following content in it:
 [Unit]
 Description=Python Log Parser
 After=multi-user.target
 
 [Service]
 Type=simple
 ExecStart=/usr/bin/python3.6 /opt/pytholog.py
 Restart=always
 
 [Install]
 WantedBy=multi-user.target

Reload the systemctl daemon to read new service file
 sudo systemctl daemon-reload

Enable the service to start on system boot, then start the service.
 sudo systemctl enable pytholog.service
 sudo systemctl start pytholog.service
 
Check the status of the service. 
 sudo systemctl status pytholog.service

The similar output should be presented:

 ● pytholog.service - Python Log Parser
    Loaded: loaded (/usr/lib/systemd/system/pytholog.service; enabled; vendor preset: disabled)
    Active: active (running) since Sun 2019-12-08 23:31:00 MSK; 59min ago
  Main PID: 19690 (python3.6)
    CGroup: /system.slice/pytholog.service
            └─19690 /usr/bin/python3.6 /opt/pytholog.py
 
 Dec 08 23:31:00 uldcbpans10.eur.mkcorp.com systemd[1]: Started Python Log Parser.
 Dec 08 23:31:00 uldcbpans10.eur.mkcorp.com systemd[1]: Starting Python Log Parser...
