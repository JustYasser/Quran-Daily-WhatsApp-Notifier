from datetime import datetime, timedelta
from config import TIMEZONE, SETTINGS_FILE, arabic_days, client, poll_options
import json
from client import Client



def get_today_arabic():
    # get datetime now with timezone
    now = datetime.now(tz=TIMEZONE)
    
    # get weekday number (1-7)
    weekday_number = now.isoweekday()
    
    # get name from list (0-6)
    today_name = arabic_days[weekday_number-1]
    
    # return arabic name
    return today_name

def get_time_remaining():
    # get datetime now with timezone
    now = datetime.now(tz=TIMEZONE)
    # get send time as tuple or list
    send_time = get_send_time()
    
    # set send time today with now replaced the time to send time
    next_time_to_send = now.replace(hour=send_time[0], minute=send_time[1], second=0, microsecond=0)
    
    # check if send time today is in the past
    if now > next_time_to_send:
        # make send time tomorrow
        next_time_to_send = next_time_to_send + timedelta(days=1)
    
    # return time remaining in seconds
    return (next_time_to_send-now).seconds

def get_send_time():
    # load settings from settings file
    data = load_settings()
    
    # return send time
    return data.get("send_time", [0, 0])

def set_send_time(time:tuple[int,int]|list[int,int]):
    if type(time) not in [tuple, list]:
        return
    
    # load settings from settings file
    data = load_settings()
    
    # update send time
    data['send_time'] = time
    
    # save
    dump_settings(data)

def get_disabled_weekdays():
    # load settings from settings file
    data = load_settings()
    
    # return disabled weekdays
    return data.get("disabled_weekdays", [])

def add_disabled_weekday(weekday_number):
    # load settings from settings file
    data = load_settings()
    
    # get disabled weekdays
    weekdays:list = data.get("disabled_weekdays", [])
    
    # check if weekday is already exists in list
    if weekday_number not in weekdays:
        # add weekday
        weekdays.append(weekday_number)
        # update the list
        data['disabled_weekdays'] = weekdays
        # save
        dump_settings(data)

def remove_disabled_weekday(weekday_number):
    # load settings from settings file
    data = load_settings()
    
    # get disabled weekday
    weekdays:list = data.get("disabled_weekdays", [])
    
    # check if weekday is in list
    if weekday_number in weekdays:
        
        # remove weekday
        weekdays.remove(weekday_number)
        
        # update list
        data['disabled_weekdays'] = weekdays
        
        # save
        dump_settings(data)
    

def format_time(seconds: int) -> str:
    # Dividing seconds by seconds per hour
    hours = seconds // 3600
    
    # Dividing remain seconds by seconds per minutes
    minutes = (seconds % 3600) // 60
    
    # extract remaining seconds
    secs = seconds % 60
    
    # return with str
    return f"{hours:02}", f"{minutes:02}", f"{secs:02}"

def convert_to_12hr(time_str: str) -> str:
    hour, minute = map(int, time_str.split(":"))
    
    # PM or AM in arabic
    period = "ص" if hour < 12 else "م"
    
    # to 12hrs
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    
    return f"{hour_12}:{minute:02}{period}"

def load_settings():
    # get settings from json file
    with open(SETTINGS_FILE, "r") as file:
        data = json.load(file)
    
    # return
    return data

def dump_settings(data):
    # put the data in settings file
    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_poll_messages_ids():
    # get settings from json file
    with open('poll_messages_ids.json', "r") as file:
        data = json.load(file)
    
    # return
    return data
def dump_poll_messages_ids(data):
    # put the data in settings file
    with open('poll_messages_ids.json', "w") as file:
        json.dump(data, file, indent=4)


def get_active_group():
    # load settings from settings file
    data = load_settings()
    # get group id
    group_id = data.get("group_id")
    # return
    return group_id

def get_active_admins():
    # load settings from settings file
    data = load_settings()
    # get admins list
    admins = data.get("admins", [])
    # return
    return admins

def get_my_id():
    # load settings from settings file
    data = load_settings()
    # get my id
    my_id = data.get("my_id")
    # return
    return my_id

def activate_group(group_id, admin_id, my_id):
    # load settings from settings file
    data = load_settings()
    # update group id
    data['group_id'] = group_id
    data['admins'] = [admin_id]
    data['my_id'] = my_id
    # save
    dump_settings(data)

def deactivate_group():
    # load settings from settings file
    data = load_settings()
    # remove group id
    data['group_id'] = None
    data['admins'] = []
    data['my_id'] = None
    # save
    dump_settings(data)

def get_weekday_of_report():
    # load settings from settings file
    data = load_settings()
    # get weekday of report
    weekday_of_report = data.get("weekday_of_report", 5) # default to friday
    # return
    return weekday_of_report

def set_weekday_of_report(weekday_number):
    # load settings from settings file
    data = load_settings()
    # update weekday of report
    data['weekday_of_report'] = weekday_number
    # save
    dump_settings(data)

def add_message_to_poll_messages(day_number, message_id):
    # load settings from settings file
    data = load_poll_messages_ids()
    # get poll messages dict
    poll_messages = data.get("poll_messages", {})
    # update dict
    poll_messages[str(day_number)] = message_id
    # update in data
    data['poll_messages'] = poll_messages
    # save
    dump_poll_messages_ids(data)

def get_messages_from_poll_messages() -> dict:
    # load settings from settings file
    data = load_poll_messages_ids()
    # get poll messages dict
    poll_messages = data.get("poll_messages", {})
    # return message id or None
    return poll_messages

def reset_poll_messages():
    # load settings from settings file
    data = load_poll_messages_ids()
    # reset poll messages dict
    data['poll_messages'] = {}
    # save
    dump_poll_messages_ids(data)

def get_group_members_ids(group_id):
    members = client.group_members(group_id)
    if members.get("status") != "success":
        return []
    members = members.get("response", [])
    member_ids = [(member.get("id", {}).get("_serialized"), member.get("pushname", "اسم عضو غير معروف"), member.get("isMe", False)) for member in members]
    return member_ids


def get_votes_details():
    details = {}
    errors = []
    poll_messages = get_messages_from_poll_messages()

    active_group_id = get_active_group()
    members = get_group_members_ids(active_group_id)

    for member_id, member_name, is_me in members:
        if is_me:
            continue
        details[member_id] = {
            "name": member_name,
            "votes": {}
        }
    
    for day_number, message_id in poll_messages.items():
        day_votes:dict = client.get_votes(message_id)
        print(day_votes)
        if day_votes.get("status") != "success":
            errors.append(f"حدثت مشكلة في جلب التصويتات ليوم {arabic_days[int(day_number)-1]}، الرسالة قد تكون محذوفة.")
            continue
        day_votes = day_votes.get("response", {})
        message = day_votes.get("msgId", {})
        chat = day_votes.get("chatId", {})
        votes = day_votes.get("votes", [])
        if not message.get("fromMe"):
            continue
        if chat.get("_serialized") != get_active_group():
            continue
        for vote in votes:
            voter = vote.get("sender", {})
            voter_id = voter.get("_serialized")
            selected_options = vote.get("selectedOptions", [])
            
            if voter_id not in details:
                errors.append(f"عضو غير معروف قام بالتصويت ليوم {arabic_days[int(day_number)-1]}، قد يكون العضو غادر المجموعة.")
                continue
            
            for option in selected_options:
                if not option:
                    continue
                option_name = option.get("name")
                if option_name not in poll_options:
                    errors.append(f"عضو @{voter_id} قام بالتصويت ليوم {arabic_days[int(day_number)-1]} بخيار غير معروف: {option_name}.")
                    continue
                details[voter_id]['votes'][option_name] = details[voter_id]['votes'].get(option_name, 0) + 1
    return details, errors


def send_message(chat_id, text, reply_to_message_id=None, isGroup=False, *args, **kwargs):
    if reply_to_message_id:
        print("Replying...")
        status = client.send_reply(chat_id, text, reply_to_message_id, isGroup)
        if str(status.get("status")) == "success":
            print("Replayed!")
            return
        print("Reply error:")
        print(status)
        print("-"*10)
        print("Try with sendText")
    print("Sending...")
    status = client.send_message(chat_id, text, isGroup=isGroup)
    if str(status.get("status")) == "success":
        print("Sended!")
        return  
    print("Send error:")
    print(status)
    print("-"*10)
    



def clear_sessions():
    """
    :Returns:
        - Clear all sessions.
    """
    sessions = client.show_all_sessions().get('response', [])
    result = {}
    
    if sessions:
        for session in sessions:
            session_client = Client(client.api["URL"], client.api["secretKey"], session)
            session_client.set_token(session_client.generate_token().get("token"))
            if session_client.status_session().get('status') == 'CLOSED':
                result[session_client.session] = session_client.status_session()
                continue
            session_client.logout_session()
            session_client.close_session()
            result[session_client.session] = session_client.status_session()

    return result