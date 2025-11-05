# Author Juniorkrz#7721
# Date: 15-06-2022
# Version: 0.1.0
# Description: This is a simple lib to communicate Python with WPPConnect server - https://github.com/wppconnect-team/wppconnect-server
# Based on: https://github.com/wppconnect-team/wppconnect-server/blob/main/src/routes/index.js

from json import loads as json_loads, dumps as json_dumps
from requests import request as send_request


ENDPOINTS = {
    # Auth
    "generate-token": {"method": "POST", "url": "%s/%s/generate-token"},
    "start-session": {"method": "POST", "url": "start-session"},
    "status-session": {"method": "GET", "url": "status-session"},
    "qrcode-session": {"method": "GET", "url": "qrcode-session"},
    "check-connection-session": {"method": "GET", "url": "check-connection-session"},
    "close-session": {"method": "POST", "url": "close-session"},
    "logout-session": {"method": "POST", "url": "logout-session"},
    "show-all-sessions": {"method": "GET", "url": "%s/show-all-sessions"},


    # Chat
    "all-chats": {"method": "GET", "url": "all-chats"},
    "chat-by-id": {"method": "GET", "url": "chat-by-id/%s"},
    "message-by-id": {"method": "GET", "url": "message-by-id/%s"},
    "chat-is-online": {"method": "GET", "url": "chat-is-online/%s"},
    "all-chats-with-messages": {"method": "GET", "url": "all-chats-with-messages"},
    "all-messages-in-chat": {"method": "GET", "url": "all-messages-in-chat/%s"},
    "all-new-messages": {"method": "GET", "url": "all-new-messages"},
    "unread-messages": {"method": "GET", "url": "unread-messages"},
    "all-unread-messages": {"method": "GET", "url": "all-unread-messages"},
    "last-seen": {"method": "GET", "url": "last-seen"},
    "list-mutes": {"method": "GET", "url": "list-mutes"},
    "archive-chat": {"method": "POST", "url": "archive-chat"},
    "clear-chat": {"method": "POST", "url": "clear-chat"},
    "delete-chat": {"method": "POST", "url": "delete-chat"},
    "delete-message": {"method": "POST", "url": "delete-message"},
    "mark-unseen": {"method": "POST", "url": "mark-unseen"},
    "pin-chat": {"method": "POST", "url": "pin-chat"},
    "send-mute": {"method": "POST", "url": "send-mute"},
    "chat-state": {"method": "POST", "url": "chat-state"},
    "send-seen": {"method": "POST", "url": "send-seen"},
    "temporary-messages": {"method": "POST", "url": "temporary-messages"},
    "typing": {"method": "POST", "url": "typing"},


    # Send Message
    "download-media": {"method": "POST", "url": "download-media"},
    "send-file": {"method": "POST", "url": "send-file"},
    "send-file-base64": {"method": "POST", "url": "send-file-base64"},
    "send-image": {"method": "POST", "url": "send-image"},
    "send-voice-base64": {"method": "POST", "url": "send-voice-base64"},
    "send-reply": {"method": "POST", "url": "send-reply"},
    "send-message": {"method": "POST", "url": "send-message"},
    "send-buttons": {"method": "POST", "url": "send-message"},
    "forwardMessages": {"method": "POST", "url": "forward-messages"},
    "contact-vcard": {"method": "POST", "url": "contact-vcard"},
    "send-link-preview": {"method": "POST", "url": "send-link-preview"},
    "send-location": {"method": "POST", "url": "send-location"},
    "send-mentioned": {"method": "POST", "url": "send-mentioned"},
    "send-sticker": {"method": "POST", "url": "send-sticker"},
    "send-sticker-gif": {"method": "POST", "url": "send-sticker-gif"},
    "star-message": {"method": "POST", "url": "star-message"},
    "send-poll-message": {"method": "POST", "url": "send-poll-message"},
    "votes": {"method": "GET", "url": "votes/%s"},


    # Profile
    "change-username": {"method": "POST", "url": "change-username"},
    "change-profile-image": {"method": "POST", "url": "change-profile-image"},
    "change-profile-status": {"method": "POST", "url": "profile-status"},


    # Contact
    "check-number-status": {"method": "GET", "url": "check-number-status/%s"},
    "all-contacts": {"method": "GET", "url": "all-contacts"},
    "contact": {"method": "GET", "url": "contact/%s"},
    "profile": {"method": "GET", "url": "profile/%s"},
    "profile-pic": {"method": "GET", "url": "profile-pic/%s"},
    "profile-status": {"method": "GET", "url": "profile-status/%s"},


    # Group
    "create-group": {"method": "POST", "url": "create-group"},
    "join-code": {"method": "POST", "url": "join-code"},
    "add-participant-group": {"method": "POST", "url": "add-participant-group"},
    "demote-participant-group": {"method": "POST", "url": "demote-participant-group"},
    "promote-participant-group": {"method": "POST", "url": "promote-participant-group"},
    "all-broadcast-list": {"method": "GET", "url": "all-broadcast-list"},
    "all-groups": {"method": "GET", "url": "all-groups"},
    "group-admins": {"method": "GET", "url": "group-admins/%s"},
    "group-info-from-invite-link": {"method": "POST", "url": "group-info-from-invite-link"},
    "group-invite-link": {"method": "GET", "url": "group-invite-link/%s"},
    "group-members-ids": {"method": "GET", "url": "group-members-ids"},
    "group-members": {"method": "GET", "url": "group-members"},
    "leave-group": {"method": "POST", "url": "leave-group"},
    "remove-participant-group": {"method": "POST", "url": "remove-participant-group"},
    "group-description": {"method": "POST", "url": "group-description"},
    "group-property": {"method": "POST", "url": "group-property"},
    "group-subject": {"method": "POST", "url": "group-subject"},
    "messages-admins-only": {"method": "POST", "url": "messages-admins-only"},


    # Phone Status
    "get-battery-level": {"method": "GET", "url": "get-battery-level"},


    # Block list
    "block-contact": {"method": "POST", "url": "block-contact"},
    "unblock-contact": {"method": "POST", "url": "unblock-contact"},
    "blocklist": {"method": "GET", "url": "blocklist"},
}


class Client:


    def __init__(self, api_url: str, secretKey: str, session: str):
        """
        Creates a new instance of the WPPConnect Client.

        :Args:
            - api_url (str) - URL of the WPPConnect API. Example: http://localhost:8080/api
            - secretKey (str) - Secret key of the WPPConnect API.
            - session (str) - Session name to use in the WPPConnect API.
        """
        self.api = {"URL": api_url, "secretKey": secretKey}
        self.session = session
        self.headers = {"Content-Type": "application/json"}


    def __add_header(self, key, value):
        self.headers[key] = value


    def __request_api(self, method, url, payload={}):
        resp = send_request(method, url, headers=self.headers, data=json_dumps(payload))
        try:
            return json_loads(resp.content.decode())
        except:
            print(resp.content)
            return False


    def generate_token(self):
        """
        Generate a new Bearer token for the current session.

        :Returns:
            - JSON object with the token in the "token" key.
        """
        url = self.api["URL"] + "/" +  ENDPOINTS["generate-token"]["url"] % (self.session, self.api["secretKey"])
        return self.__request_api(ENDPOINTS["generate-token"]["method"], url)


    def set_token(self, token: str):
        """
        Set the Bearer token for the current session.

        :Args:
            - token (str) - Bearer token to use in the API.
        """
        self.__add_header("Authorization", "Bearer " + token)

    def show_all_sessions(self):
        url = self.api["URL"] + "/" + ENDPOINTS["show-all-sessions"]["url"] % self.api["secretKey"]
        return self.__request_api(ENDPOINTS["show-all-sessions"]["method"], url)

    def start_session(self, webhook=False):
        """
        Start a new session.

        :Args:
            - webhook (str) - If is set, the session will be started with a webhook.

        :Returns:
            - JSON object with the session status and the QR Code if exists.
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["start-session"]["url"]
        payload = {}

        if webhook:
            payload["webhook"] = webhook

        return self.__request_api(ENDPOINTS["start-session"]["method"], url, payload)


    def status_session(self):
        """
        :Returns:
            - JSON object with the session status and the QR Code if exists.
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["status-session"]["url"]
        return self.__request_api(ENDPOINTS["status-session"]["method"], url)


    def qrcode_session(self):
        """
        :Returns:
            - The QR Code via Stream.
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["qrcode-session"]["url"]
        return self.__request_api(ENDPOINTS["qrcode-session"]["method"], url)


    def check_connection_session(self):
        """
        :Returns:
            - Connection status
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["check-connection-session"]["url"]
        return self.__request_api(ENDPOINTS["check-connection-session"]["method"], url)


    def close_session(self):
        """
        :Returns:
            - Close the session.
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["close-session"]["url"]
        return self.__request_api(ENDPOINTS["close-session"]["method"], url)

    def logout_session(self):
        """
        :Returns:
            - Logout the session.
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["logout-session"]["url"]
        return self.__request_api(ENDPOINTS["logout-session"]["method"], url)

    def all_chats(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-chats"]["url"]
        return self.__request_api(ENDPOINTS["all-chats"]["method"], url)


    def chat_by_id(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["chat-by-id"]["url"] % phone
        return self.__request_api(ENDPOINTS["chat-by-id"]["method"], url)

    def message_by_id(self, messageId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["message-by-id"]["url"] % messageId
        return self.__request_api(ENDPOINTS["message-by-id"]["method"], url)


    def chat_is_online(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["chat-is-online"]["url"] % phone
        return self.__request_api(ENDPOINTS["chat-is-online"]["method"], url)


    def all_messages_in_chat(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-messages-in-chat"]["url"] % phone
        return self.__request_api(ENDPOINTS["all-messages-in-chat"]["method"], url)


    def all_new_messages(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-new-messages"]["url"]
        return self.__request_api(ENDPOINTS["all-new-messages"]["method"], url)


    def unread_messages(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["unread-messages"]["url"]
        return self.__request_api(ENDPOINTS["unread-messages"]["method"], url)


    def all_unread_messages(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-unread-messages"]["url"]
        return self.__request_api(ENDPOINTS["all-unread-messages"]["method"], url)


    def last_seen(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["last-seen"]["url"] % phone
        return self.__request_api(ENDPOINTS["last-seen"]["method"], url)


    def list_mutes(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["list-mutes"]["url"]
        return self.__request_api(ENDPOINTS["list-mutes"]["method"], url)


    def archive_chat(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["archive-chat"]["url"]
        return self.__request_api(ENDPOINTS["archive-chat"]["method"], url, {"phone": phone})


    def clear_chat(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["clear-chat"]["url"]
        return self.__request_api(ENDPOINTS["clear-chat"]["method"], url, {"phone": phone})


    def delete_chat(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["delete-chat"]["url"]
        return self.__request_api(ENDPOINTS["delete-chat"]["method"], url, {"phone": phone})


    def delete_message(self, phone, messageId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["delete-message"]["url"]
        return self.__request_api(ENDPOINTS["delete-message"]["method"], url, {"phone": phone, "messageId": messageId})


    def mark_unseen(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["mark-unseen"]["url"]
        return self.__request_api(ENDPOINTS["mark-unseen"]["method"], url, {"phone": phone})


    def pin_chat(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["pin-chat"]["url"]
        return self.__request_api(ENDPOINTS["pin-chat"]["method"], url, {"phone": phone})


    def send_mute(self, phone, time, type):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-mute"]["url"]
        return self.__request_api(ENDPOINTS["send-mute"]["method"], url, {"phone": phone, "time": time, "type": type})


    def chat_state(self, phone, chatstate):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["chat-state"]["url"]
        return self.__request_api(ENDPOINTS["chat-state"]["method"], url, {"phone": phone, "chatstate": chatstate})


    def send_seen(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-seen"]["url"]
        return self.__request_api(ENDPOINTS["send-seen"]["method"], url, {"phone": phone})


    def temporary_messages(self, phone, value):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["temporary-messages"]["url"]
        return self.__request_api(ENDPOINTS["temporary-messages"]["method"], url, {"phone": phone, "value": value})


    def typing(self, phone, value, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["typing"]["url"]
        return self.__request_api(ENDPOINTS["typing"]["method"], url, {"phone": phone, "value": value, "isGroup": isGroup})

    def download_file(self, messageId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["download-media"]["url"]
        payload = {"messageId": messageId}
        return self.__request_api(ENDPOINTS["download-media"]["method"], url, payload)

    def send_file(self, phone, filename, base64, caption=False, isGroup=False):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-file"]["url"]
        payload = {"phone": phone, "filename": filename, "base64": base64, "isGroup": isGroup, "type":"video"}

        if caption:
            payload["caption"] = caption

        return self.__request_api(ENDPOINTS["send-file"]["method"], url, payload)
    
    def send_file_base64(self, phone, filename, base64, caption=False, isGroup=False):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-file-base64"]["url"]
        payload = {"phone": phone, "filename": filename, "base64": base64, "isGroup": isGroup}

        if caption:
            payload["caption"] = caption

        return self.__request_api(ENDPOINTS["send-file-base64"]["method"], url, payload)


    def send_image(self, phone, path, caption=False, isGroup=False):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-image"]["url"]
        payload = {"phone": phone, "path": path, "isGroup": isGroup}

        if caption:
            payload["caption"] = caption

        return self.__request_api(ENDPOINTS["send-image"]["method"], url, payload)


    def send_voice(self, phone, base64Ptt, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-voice-base64"]["url"]
        return self.__request_api(ENDPOINTS["send-voice-base64"]["method"], url, {"phone": phone, "base64Ptt": base64Ptt, "isGroup": isGroup})


    def send_reply(self, phone, message, messageId, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-reply"]["url"]
        return self.__request_api(ENDPOINTS["send-reply"]["method"], url, {"phone": phone, "message": message, "messageId": messageId, "isGroup": isGroup})


    def send_message(self, phone, message, isGroup=False):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-message"]["url"]
        return self.__request_api(ENDPOINTS["send-message"]["method"], url, {"phone": phone, "message": message, "isGroup": isGroup})


    def send_buttons(self, phone, message, buttons, title=False, footer=False):
        """
        Send a button message
        :param phone: Phone number
        :param message: Message
        :param buttons: List of buttons (Use the Buttons.get() method to get the buttons)
        :param title: Title of the message
        :param footer: Footer of the message
        """
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-buttons"]["url"]
        payload = {"phone": phone, "message": message}
        payload["options"] = {"useTemplateButtons": "true", "buttons": buttons}

        if title:
            payload["options"]["title"] = title
        if footer:
            payload["options"]["footer"] = footer

        return self.__request_api(ENDPOINTS["send-buttons"]["method"], url, payload)


    def forward_messages(self, phone, messageId, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["forwardMessages"]["url"]
        return self.__request_api(ENDPOINTS["forwardMessages"]["method"], url, {"phone": phone, "messageId": messageId, "isGroup": isGroup})


    def contact_vcard(self, phone, contactsId, name, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["contact-vcard"]["url"]
        return self.__request_api(ENDPOINTS["contact-vcard"]["method"], url, {"phone": phone, "contactsId": contactsId, "name": name, "isGroup": isGroup})


    def send_link_preview(self, phone, url, caption):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-link-preview"]["url"]
        return self.__request_api(ENDPOINTS["send-link-preview"]["method"], url, {"phone": phone, "url": url, "caption": caption})


    def send_location(self, phone, lat, lng, title):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-location"]["url"]
        return self.__request_api(ENDPOINTS["send-location"]["method"], url, {"phone": phone, "lat": lat, "lng": lng, "title": title})


    def send_mentioned(self, phone, message, mentioned):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-mentioned"]["url"]
        return self.__request_api(ENDPOINTS["send-mentioned"]["method"], url, {"phone": phone, "message": message, "mentioned": mentioned, "isGroup": True})


    def send_sticker(self, phone, path, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-sticker"]["url"]
        return self.__request_api(ENDPOINTS["send-sticker"]["method"], url, {"phone": phone, "path": path, "isGroup": isGroup})


    def send_sticker_gif(self, phone, path, isGroup):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-sticker-gif"]["url"]
        return self.__request_api(ENDPOINTS["send-sticker-gif"]["method"], url, {"phone": phone, "path": path, "isGroup": isGroup})
    
    def star_message(self, messageId, star):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["star-message"]["url"]
        return self.__request_api(ENDPOINTS["star-message"]["method"], url, {"messageId": messageId, "star": star})
    
    def send_poll_message(self, phone, name:str, choices:list[str], selectableCount=1, isGroup=False):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["send-poll-message"]["url"]
        return self.__request_api(ENDPOINTS["send-poll-message"]["method"], url, {"phone": phone, "name": name, "choices": choices, "options": {"selectableCount": selectableCount}, "isGroup": isGroup})
    
    def get_votes(self, messageId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["votes"]["url"] % messageId
        return self.__request_api(ENDPOINTS["votes"]["method"], url)

    def change_username(self, name):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["change-username"]["url"]
        return self.__request_api(ENDPOINTS["change-username"]["method"], url, {"name": name})


    def change_profile_image(self, path):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["change-profile-image"]["url"]
        return self.__request_api(ENDPOINTS["change-profile-image"]["method"], url, {"path": path})


    def change_profile_status(self, status):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["change-profile-status"]["url"]
        return self.__request_api(ENDPOINTS["change-profile-status"]["method"], url, {"status": status})


    def check_number_status(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["check-number-status"]["url"] + "/" + phone
        return self.__request_api(ENDPOINTS["check-number-status"]["method"], url)


    def all_contacts(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-contacts"]["url"]
        return self.__request_api(ENDPOINTS["all-contacts"]["method"], url)


    def contact(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["contact"]["url"] + "/" + phone
        return self.__request_api(ENDPOINTS["contact"]["method"], url)


    def profile(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["profile"]["url"] + "/" + phone
        return self.__request_api(ENDPOINTS["profile"]["method"], url)


    def profile_pic(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["profile-pic"]["url"] + "/" + phone
        return self.__request_api(ENDPOINTS["profile-pic"]["method"], url)


    def profile_status(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["profile-status"]["url"] + "/" + phone
        return self.__request_api(ENDPOINTS["profile-status"]["method"], url)


    def create_group(self, groupname, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["create-group"]["url"]
        return self.__request_api(ENDPOINTS["create-group"]["method"], url, {"groupname": groupname, "phone": phone})


    def join_code(self, inviteCode):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["join-code"]["url"]
        return self.__request_api(ENDPOINTS["join-code"]["method"], url, {"inviteCode": inviteCode})


    def add_participant_group(self, groupId, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["add-participant-group"]["url"]
        return self.__request_api(ENDPOINTS["add-participant-group"]["method"], url, {"groupId": groupId, "phone": phone})


    def demote_participant_group(self, groupId, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["demote-participant-group"]["url"]
        return self.__request_api(ENDPOINTS["demote-participant-group"]["method"], url, {"groupId": groupId, "phone": phone})


    def promote_participant_group(self, groupId, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["promote-participant-group"]["url"]
        return self.__request_api(ENDPOINTS["promote-participant-group"]["method"], url, {"groupId": groupId, "phone": phone})


    def all_broadcast_list(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-broadcast-list"]["url"]
        return self.__request_api(ENDPOINTS["all-broadcast-list"]["method"], url)


    def all_groups(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["all-groups"]["url"]
        return self.__request_api(ENDPOINTS["all-groups"]["method"], url)


    def group_admins(self, groupId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-admins"]["url"] % groupId
        return self.__request_api(ENDPOINTS["group-admins"]["method"], url)


    def group_info_from_invite_link(self, invitecode):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-info-from-invite-link"]["url"]
        return self.__request_api(ENDPOINTS["group-info-from-invite-link"]["method"], url, {"invitecode": invitecode})


    def group_invite_link(self, groupId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-invite-link"]["url"] + "/" + groupId
        return self.__request_api(ENDPOINTS["group-invite-link"]["method"], url)


    def group_members_ids(self, groupId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-members-ids"]["url"] + "/" + groupId
        return self.__request_api(ENDPOINTS["group-members-ids"]["method"], url)


    def group_members(self, groupId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-members"]["url"] + "/" + groupId
        return self.__request_api(ENDPOINTS["group-members"]["method"], url)


    def leave_group(self, groupId):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["leave-group"]["url"]
        return self.__request_api(ENDPOINTS["leave-group"]["method"], url, {"groupId": groupId})


    def remove_participant_group(self, groupId, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["remove-participant-group"]["url"]
        return self.__request_api(ENDPOINTS["remove-participant-group"]["method"], url, {"groupId": groupId, "phone": phone})


    def group_description(self, groupId, description):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-description"]["url"]
        return self.__request_api(ENDPOINTS["group-description"]["method"], url, {"groupId": groupId, "description": description})


    def group_property(self, groupId, property, value):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-property"]["url"]
        return self.__request_api(ENDPOINTS["group-property"]["method"], url, {"groupId": groupId, "property": property, "value": value})


    def group_subject(self, groupId, title):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["group-subject"]["url"]
        return self.__request_api(ENDPOINTS["group-subject"]["method"], url, {"groupId": groupId, "title": title})


    def messages_admins_only(self, groupId, value):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["messages-admins-only"]["url"]
        return self.__request_api(ENDPOINTS["messages-admins-only"]["method"], url, {"groupId": groupId, "value": value})


    def get_battery_level(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["get-battery-level"]["url"]
        return self.__request_api(ENDPOINTS["get-battery-level"]["method"], url)


    def block_contact(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["block-contact"]["url"]
        return self.__request_api(ENDPOINTS["block-contact"]["method"], url, {"phone": phone})


    def unblock_contact(self, phone):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["unblock-contact"]["url"]
        return self.__request_api(ENDPOINTS["unblock-contact"]["method"], url, {"phone": phone})


    def blocklist(self):
        url = self.api["URL"] + "/" + self.session + "/" + ENDPOINTS["blocklist"]["url"]
        return self.__request_api(ENDPOINTS["blocklist"]["method"], url)
