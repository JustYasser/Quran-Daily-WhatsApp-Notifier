import config
import modules
import services

client = config.client
poll_sender_client = config.poll_sender_client


def receive_message(message):
    msg = modules.Message(message)
    
    # Assign variables
    sender_id = msg.sender.jid.raw
    chat_id = msg.chat.jid.raw
    isGroup = msg.chat.is_group
    message_id = msg.id
    message_text:str = msg.text
    
    # get active group and admins
    active_group, active_admins = services.get_active_group(), services.get_active_admins()

    # Log active group and admins
    print(f"Active group is {active_group}, active admins are {active_admins}", flush=True)
    
    # check if message text is exists
    if message_text:
        # check if the text is command
        if not message_text.startswith(config.BOT_PREFIX):
            return
    else:
        return
    
    # log the received command
    print(f"Receive an command from {sender_id} in chat id {chat_id} : {message_text}", flush=True)
    
    # remove the prefix
    message_text = message_text[1:]

    # create a list for group admins
    group_admins = []
    
    # check if message in group
    if isGroup:

        # get group admins
        get_admins = client.group_admins(chat_id)
        if get_admins.get("status") == "success":
            # Assign group admins id list
            group_admins = [admin['_serialized'] for admin in get_admins['response'][0]]
        
        # check if there is an active group
        if active_group:
            print(f"Active group is {active_group}", flush=True)
            # check if the message is from the active group
            if chat_id == active_group:
                print("Message is from the active group", flush=True)
                
                # if sender is not bot admins
                if sender_id not in active_admins:
                    print(f"Sender {msg.sender.pushname}({sender_id}) is not an admin", flush=True)
                    services.send_message(chat_id, "لا يمكن استخدام البوت لغير المشرفين المضافين في البوت", message_id, True)
                    return
                
                else:
                    print("Sender is an admin!", flush=True)
                
            else:
                print("Message is not from the active group")
                services.send_message(chat_id, "يوجد مجموعة مفعلة مسبقاً، يجب تعطيلها أولاً وتفعيل هذه المجموعة", message_id, isGroup=isGroup)
                return
    
    else:
        # if sender is not bot admins
        if sender_id not in config.ADMINS:
            print(f"Sender {msg.sender.pushname}({sender_id}) is not an admin", flush=True)
            services.send_message(chat_id, "لا يمكن استخدام البوت لغير المشرفين المضافين في البوت", message_id, True)
            return
    
    # split message text to get parameters
    params = message_text.split()
    print(f"parameters is {params}", flush=True)
    
    # help message
    if message_text == 'مساعدة' or message_text == 'الاوامر':
        services.send_message(chat_id, config.help_message, message_id, isGroup=isGroup)
        
    # activate group command
    elif message_text.startswith('تفعيل'):
        # check if chat is group
        if msg.chat.is_group:
            # check if sender is group admin
            if sender_id not in group_admins:
                services.send_message(chat_id, "لا يمكن استخدام هذا الامر الا من قبل مشرفي المجموعة", message_id, isGroup=isGroup)
                return
            
            # check if there is an active group
            if active_group:
                # check if the active group is the same as the current chat
                if active_group != chat_id:
                    services.send_message(chat_id, "يوجد مجموعة مفعلة مسبقاً، يجب تعطيلها أولاً", message_id, isGroup=isGroup)
                
                # check if there is an active group
                else:
                    services.send_message(chat_id, "المجموعة مفعلة مسبقاً", message_id, isGroup=isGroup)
                return
            
            # get group members
            members = services.get_group_members_ids(chat_id)
            
            my_id = None
            
            # find bot id in members
            for member_id, member_name, is_me in members:
                if is_me:
                    my_id = member_id
                    break
            
            # activate group
            services.activate_group(chat_id, sender_id, my_id)
            services.send_message(chat_id, "تم تفعيل المجموعة", message_id, isGroup=isGroup)
        
        # if is not a group
        else:
            services.send_message(chat_id, "لا يمكن كتابة هذا الامر في هذه المحادثة", message_id, isGroup=isGroup)
    
    # disable bot command
    elif message_text.startswith("تعطيل"):
        # check if there is an active group
        if not active_group:
            services.send_message(chat_id, "لا توجد مجموعة مفعلة مسبقاً", message_id, isGroup=isGroup)
            return
        # check if the active group is the same as the current chat
        if chat_id != active_group:
            services.send_message(chat_id, "المجموعة المفعلة مسبقاً ليست هذه المجموعة", message_id, isGroup=isGroup)
            return
        # deactivate group
        services.deactivate_group()
        services.send_message(chat_id, "تم تعطيل البوت", message_id, isGroup=isGroup)
    
    # send poll command manually
    elif message_text == 'تصويت':
        # check if chat is group
        if msg.chat.is_group:
            # send poll
            poll_name = config.poll_text.format(today=services.get_today_arabic())
            poll_sender_client.send_poll_message(chat_id, poll_name, config.poll_options, selectableCount=0, isGroup=isGroup)
            client.send_message(chat_id, "❗ | لن يكون هذا التصويت ضمن التقرير الاسبوعي", isGroup=isGroup)
        # if is not a group
        else:
            services.send_message(chat_id, "لا يمكن كتابة هذا الامر في هذه المحادثة", message_id, isGroup=isGroup)
    
    # elif message_text == 'تقرير':
    #     return
    #     status = job.send_report()
    #     if status != True:
    #         services.send_message(chat_id, f"حدثت مشكلة اثناء ارسال التقرير:\n{status}", message_id, isGroup=isGroup)
    #     else:
    #         services.send_message(chat_id, "تم ارسال التقرير", message_id, isGroup=isGroup)
    
    # remaining time command
    elif message_text.startswith("متى"):
        
        # format remaining time
        format_time = services.format_time(services.get_time_remaining())
        hours = format_time[0]
        minutes = format_time[1]
        seconds = format_time[2]
        
        # create an arabic text
        texts = []
        if hours != "00":
            texts.append(f"{hours} ساعة")
        if minutes != "00":
            texts.append(f"{minutes} دقيقة")
        if seconds != '00':
            texts.append(f"{seconds} ثانية")
        
        # send
        services.send_message(chat_id, "باقي على الإرسال القادم " + " و".join(texts), message_id, isGroup=isGroup)
    
    # command for get send time or set new send time
    elif message_text.startswith("وقت"):
        # if message text is just "<prefix>command"
        if len(params) == 1:
            # Send message with the send time
            send_time = services.get_send_time()
            send_time = f"{send_time[0]}:{send_time[1]}"
            services.send_message(chat_id, f"وقت الارسال الحالي : *{services.convert_to_12hr(send_time)}*", message_id, isGroup=isGroup)
        
        # if message text is "<prefix>command something" set a new time
        elif len(params) == 2:
            new_time = message_text.split()[1].split(":")
            if len(new_time) != 2:
                services.send_message(chat_id, "ضع الوقت بشكل صحيح بنظام 24 ساعة\nمثال: 16:30 ( الساعة 4:30 عصراً )", message_id, isGroup=isGroup)
                return
            
            hours = new_time[0]
            minutes = new_time[1]
            # validate numeric
            if not hours.isnumeric() or not minutes.isnumeric():
                services.send_message(chat_id, "ضع الوقت بشكل صحيح بنظام 24 ساعة\nمثال: 16:30 ( الساعة 4:30 عصراً )", message_id, isGroup=isGroup)
                return
            
            hours = int(hours)
            minutes = int(minutes)
            # validate time
            if 0 >= hours > 24 or 0 >= minutes > 60:
                services.send_message(chat_id, "ضع الوقت بشكل صحيح بنظام 24 ساعة\nمثال: 16:30 ( الساعة 4:30 عصراً )", message_id, isGroup=isGroup)
                return
            
            # set the new time
            services.set_send_time((hours, minutes))
            
            services.send_message(chat_id, f"تم تعيين الوقت الى *{services.convert_to_12hr(f'{hours}:{minutes}')}*", message_id, isGroup=isGroup)
        else:
            services.send_message(chat_id, "ضع الوقت بشكل صحيح بنظام 24 ساعة\nمثال: 16:30 ( الساعة 4:30 عصراً )", message_id, isGroup=isGroup)
            return
    
    # to remove disabled weekday
    elif message_text.startswith("ازالة"):
        # message must be "<prefix>command something"
        if len(params) == 2:
            new_day = message_text.split()[1]
            if new_day.isnumeric():
                new_day = int(new_day)
                if 1 <= new_day <= 7:
                    weekday_number = new_day
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}ازالة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            else:
                if new_day in config.arabic_days:
                    weekday_number = config.arabic_days.index(new_day)+1
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}ازالة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            
            services.remove_disabled_weekday(weekday_number)
            services.send_message(chat_id, f"تم ازالة يوم *{config.arabic_days[weekday_number-1]}* من الأيام المستثناة من التذكير", message_id, isGroup=isGroup)
        else:
            services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}ازالة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
    
    # to add disabled weekday
    elif message_text.startswith("اضافة"):
        # message must be "<prefix>command something"
        if len(params) == 2:
            new_day = message_text.split()[1]
            if new_day.isnumeric():
                new_day = int(new_day)
                if 1 <= new_day <= 7:
                    weekday_number = new_day
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}اضافة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            else:
                if new_day in config.arabic_days:
                    weekday_number = config.arabic_days.index(new_day)+1
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}اضافة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            
            services.add_disabled_weekday(weekday_number)
            services.send_message(chat_id, f"تم اضافة يوم *{config.arabic_days[weekday_number-1]}* للأيام المستثناة من التذكير", message_id, isGroup=isGroup)
        else:
            services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}اضافة <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
    
    
    # to get disabled weekdays
    elif message_text.startswith("مستثنى"):
        days = services.get_disabled_weekdays()
        if len(days) == 0:
            days = ['لا يوجد']
        else:
            days.sort()
            for day_index in range(len(days)):
                weekday_number = int(days[day_index])
                days[day_index] = config.arabic_days[weekday_number-1]
        
        services.send_message(chat_id, f"الأيام المسثتناه من التذكير بالورد اليومي : {', '.join(days)}", message_id, isGroup=isGroup)
    
    # command to get or set the weekday of report or change it
    elif message_text.startswith("يوم التقرير"):
        # if message "<prefix>command""
        if len(params) == 2:
            # get current weekday of report
            weekday_number = services.get_weekday_of_report()
            services.send_message(chat_id, f"اليوم الحالي لإرسال التقرير الاسبوعي هو *{config.arabic_days[weekday_number-1]}*", message_id, isGroup=isGroup)

        # if message "<prefix>command <something>"
        elif len(params) == 3:
            
            # get new weekday of report from message
            new_day = message_text.split()[2]
            if new_day.isnumeric():
                new_day = int(new_day)
                if 1 <= new_day <= 7:
                    weekday_number = new_day
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}يوم التقرير <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            else:
                if new_day in config.arabic_days:
                    weekday_number = config.arabic_days.index(new_day)+1
                else:
                    services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}يوم التقرير <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)
                    return
            
            # set the new weekday of report
            services.set_weekday_of_report(weekday_number)
            services.send_message(chat_id, f"تم تعيين يوم *{config.arabic_days[weekday_number-1]}* لإرسال التقرير الاسبوعي", message_id, isGroup=isGroup)

        # if message "<prefix>command <something> <something>"
        else:
            services.send_message(chat_id, f"الاستخدام الصحيح :\n{config.BOT_PREFIX}يوم التقرير <اسم اليوم او رقم اليوم في الاسبوع>\n\n*تنبيهات:*\n- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع\n- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:\n"+"\n".join([f"{day}={config.arabic_days.index(day)+1}" for day in config.arabic_days]), message_id, isGroup=isGroup)

