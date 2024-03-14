# Service Management Website for Linux
Small website to show you a list of predefined Services, their status (active/exited/..) and the ability to
restart/start/stop them if allowed to.

Requires Python 3.11 or higher!
Runs only on Linux (for now).


## How it looks
The Overview shows you all Services you defined in the configuration including their Systemd Status, Functions to interact with the Service and the Logs.
For Services with Websites (like this tool) there are also links that will open the Website of the Service in a new tab.
<img alt="Service Overview" src="https://github.com/nikilase/service_website/assets/38077998/2450ff3f-50ea-45ec-b7e5-97ff6e69e98e">

The Live Log will show you a list of the last n logs (20 by default) and will update every second.
You can also filter that only logs above a certain log level will be shown.
<img alt="Lice Log of a Service" src="https://github.com/nikilase/service_website/assets/38077998/8c76e87b-82cf-4cd1-b59b-3fc94fbb8a53">

## Installation

#### Requirements
* Python 3.11 or higher
* *modern* Linux System like *Raspberry Pi OS* or *Ubuntu*
* optional: Git Client

##### Downloading and installing steps:
1. Download or Clone the latest version of the project
2. Configure your Services in:<br>
   `app/conf/config.toml`
    * For the encrypted User Password you can run the `hash_password.py` script which will ask you for a password and 
      return the encrypted password for you to save in the config file.
    * You can find a template config file in the same `app/conf/` folder
    * If you don't want to use https then you have to set `secure_only` to *false*, otherwise set it to *true*

3. optional: Create a python virtual environment e.g. with venv in the directory of the project:<br>
   `python3.11 -m venv .venv`<br>
   Use it with:<br>
   `source .venv/bin/activate`
4. To run the Website just execute:<br>
   `python3.11 server.py`

> [!IMPORTANT]
> It is strongly advised to use HTTPS for this website!
> As we currently do not support providing SSL Certs, you need to use a reverse proxy to supply the cert like NGINX!
