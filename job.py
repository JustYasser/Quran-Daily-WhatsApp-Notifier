from datetime import datetime
from config import poll_sender_client, TIMEZONE, poll_options, poll_text
import services
import time as t
from threading import Event, Thread
import sys
import signal

stop_event = Event()
REFRESH_INTERVAL = 5

def send_notify():
    # get active group
    group_id = services.get_active_group()
    
    # cancel process if the group is not exists
    if not group_id:
        # return error
        return "Must be group activated"
    
    # format the text
    poll_name = poll_text.format(today=services.get_today_arabic())
    # send
    message = poll_sender_client.send_poll_message(group_id, poll_name, poll_options, selectableCount=1, isGroup=True)
    
    # return succuss
    return True, message

def send_report():
    # get active group
    group_id = services.get_active_group()
    
    # cancel process if the group is not exists
    if not group_id:
        # return error
        return "Must be group activated"
    
    details, errors = services.get_votes_details()
    report_text = "*التقرير الاسبوعي*"
    mentioned = []
    for raw_member_id, info in details.items():
        votes = info.get("votes", {})

        member_id = raw_member_id.split('@')[0]

        report_text += f"\n\n@{member_id}"
        mentioned.append(raw_member_id)
        if not votes:
            report_text += "\n- لم يصوت"
            continue
        for option, count in votes.items():
            report_text += f"\n- {option}: {count} يوم"
    if errors:
        report_text += "\n\n*الأخطاء اثناء اعداد التقرير:*"
        for error in errors:
            report_text += f"\n- {error}"

    poll_sender_client.send_mentioned(group_id, report_text, mentioned)
    
    # return succuss
    return True

def send_task(print_counter:bool=__name__=="__main__"):

    print("Starting task...", flush=True)
    
    while not stop_event.is_set():
        # update waiting time every second
        print(flush=True)
        while not stop_event.is_set():
            
            # Get time remaining in seconds
            time_remaining = round(services.get_time_remaining())
            
            # Wait 5 seconds to update time remaining again
            for _ in range(REFRESH_INTERVAL):
                if print_counter:
                    print("\rWating for", ":".join(services.format_time(time_remaining)), "        ", end='', flush=True)
                
                t.sleep(1)
                time_remaining -= 1
                if time_remaining <= 0 or stop_event.is_set():
                    break
            if time_remaining <= 0 or stop_event.is_set():
                break
        print(flush=True)
        
        t.sleep(1)
        now = datetime.now(tz=TIMEZONE) 
        weekday_number = now.isoweekday()
        
        if weekday_number == services.get_weekday_of_report():
            print("Sending report to admins...", flush=True)
            group_id = services.get_active_group()
            if not group_id:
                print("No active group found", flush=True)
            else:
                status = send_report()
                services.reset_poll_messages()
                if not status:
                    print(status)
                else:
                    print("Report sent!", flush=True)
        
        # check if today is disabled
        if weekday_number in services.get_disabled_weekdays():
            print("Today is disabled", flush=True)
        
        # if not disabled send a notification
        else:
            print("sending...", flush=True)
            status, message = send_notify()
            if not status:
                print(status, flush=True)
            else:
                print("Sended!", flush=True)
                poll_message_id = message.get("response", [{}])[0].get("id")
                my_id = services.get_my_id()
                poll_message_id = poll_message_id.replace(poll_message_id.split("_")[-1], my_id)
                services.add_message_to_poll_messages(weekday_number, poll_message_id)

        
        t.sleep(3) # delay for not sending another poll

def start_task():
    th = Thread(target=send_task, daemon=True)
    th.start()
    return th

def stop_task():
    stop_event.set()
    t.sleep(1)
    
def handle_exit(signum, frame):
    stop_task()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    start_task()