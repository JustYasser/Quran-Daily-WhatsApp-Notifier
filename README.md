# Quran Daily WhatsApp Notifier

A simple Python bot that reminds WhatsApp group(s) every day to read the Quran, with basic customizations.

## Features
- Daily scheduled reminders
- Multiple group support
- Custom message template
- Timezone-aware scheduling
- Optional quiet days (no reminders)
- Simple progress/reading plan support

## Notice
- You must have a WhatsApp number.
- You must run wppconnect-server on your server. See WPPConnect: https://github.com/wppconnect-team/wppconnect

## Prerequisites
- Python 3.10+ and pip
- A running wppconnect-server instance you can reach from this bot
- Network access from this bot to your wppconnect-server

## Install
- Clone this repository and open it in your environment
- Create a virtual environment and install dependencies:
    - run : `python -m venv .venv`
    - then run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
    - finally run `pip install -r requirements.txt`

## Configure
Update `config.py` to match your environment:

- Bot behavior
    - BOT_PREFIX: Command prefix (default: !)
    - ADMINS: List of admin WhatsApp IDs (E.164 number + @c.us), e.g., 966555555555@c.us
    - TIMEZONE: IANA timezone via pytz (default: Asia/Riyadh)
    - poll_text: Daily poll text; supports {today} (Arabic day name)
    - poll_options: Poll choices list (customize labels/emojis)

# Advanced Configuration
- WPPConnect connection
    - client_host: Base URL of your wppconnect-server (default: http://localhost)
    - client_port: Port of your wppconnect-server (default: 21465)
    - client_secret_key: Server secret/key configured in wppconnect-server
    - webhook URL: In client.start_session('http://localhost:3000/webhook'), set your public webhook receiver or adjust/remove as needed

- Sessions
    - client_session: Primary session name (default: NotifyBotSession)
    - poll_sender_session: Secondary session name (default: PollSenderSession)
    - Tokens are generated at runtime; on first run, scan the printed QR code to pair

- Persistence
    - SETTINGS_FILE: settings.json is managed by the bot (stores group enablement, reminder time, excluded days, weekly report day). Do not edit manually.

- Requirements
    - Ensure wppconnect-server is running and reachable at client_host:client_port with the configured secret

## Use
- Ensure your wppconnect-server is running and reachable
- Activate the virtual environment
- Run the bot: `python main.py`
- Keep the process running (e.g., a process manager or service) if deploying

## Screenshots
- Help command:

    ![Help command](https://github.com/JustYasser/Quran-Daily-WhatsApp-Notifier/blob/main/docs/screenshots/2.PNG?raw=true)
- Daily reminder:

    ![Daily reminder](https://github.com/JustYasser/Quran-Daily-WhatsApp-Notifier/blob/main/docs/screenshots/1.PNG?raw=true)

## Notes
- This project only mentions WPPConnect and does not explain it or its setup.
- Configure credentials and group IDs responsibly.
- For development, use a test group before production.