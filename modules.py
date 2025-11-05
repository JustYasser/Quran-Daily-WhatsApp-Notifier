from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from enum import Enum


# ---------- Helpers ----------
def _pick(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def _to_int(x, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default

def _epoch_to_dt(epoch: Optional[int]) -> Optional[datetime]:
    if epoch is None:
        return None
    try:
        # واتساب يعطي ثواني (مو ملي) عادة في أمثلتك
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    except Exception:
        return None


# ---------- Core value objects ----------
@dataclass
class JID:
    raw: str
    user: Optional[str] = None
    server: Optional[str] = None

    def __post_init__(self):
        if self.raw and '@' in self.raw and (self.user is None or self.server is None):
            self.user, self.server = self.raw.split('@', 1)

    @property
    def is_group(self) -> bool:
        return self.server == "g.us"

    @property
    def is_contact(self) -> bool:
        return self.server in {"c.us", "lid"}

    def __str__(self) -> str:
        return self.raw or ""


@dataclass
class Contact:
    jid: JID
    name: Optional[str] = None
    pushname: Optional[str] = None
    verified_name: Optional[str] = None
    is_business: Optional[bool] = None
    is_me: Optional[bool] = None
    is_wa_contact: Optional[bool] = None

    @classmethod
    def from_message(cls, data: Dict[str, Any]) -> "Contact":
        s = data.get("sender") or {}
        # في القروب المرسل الحقيقي في author، وفي الخاص في from
        candidate_id = _pick(
            data,
            "author",  # group sender
            "from",    # private chat sender
            default=None
        )
        # أولوية id داخل sender إن وجد
        jid_raw = _pick(s, "id", default=candidate_id) or ""
        return cls(
            jid=JID(jid_raw),
            name=_pick(s, "name", "formattedName", default=None),
            pushname=_pick(s, "pushname", default=_pick(data, "notifyName", default=None)),
            verified_name=_pick(s, "verifiedName", default=None),
            is_business=_pick(s, "isBusiness", default=None),
            is_me=_pick(s, "isMe", default=None),
            is_wa_contact=_pick(s, "isWAContact", default=None),
        )

#3
@dataclass
class Chat:
    jid: JID
    title: Optional[str] = None
    is_group: bool = False

    @classmethod
    def from_message(cls, data: Dict[str, Any]) -> "Chat":
        chat_id = _pick(data, "chatId", "from", default="")
        is_group = bool(data.get("isGroupMsg", False) or (chat_id.endswith("@g.us")))
        return cls(jid=JID(chat_id), title=_pick(data, "chatName", default=None), is_group=is_group)


# ---------- Content types ----------
@dataclass
class Media:
    kind: str  # "image" | "video" | "audio" | "ptt" | "sticker" | "document"
    mimetype: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[Union[int, float]] = None
    page_count: Optional[int] = None
    filehash: Optional[str] = None
    enc_filehash: Optional[str] = None
    direct_path: Optional[str] = None
    deprecated_url: Optional[str] = None
    media_key: Optional[str] = None
    caption: Optional[str] = None
    content_b64: Optional[str] = None


@dataclass
class Location:
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    label: Optional[str] = None
    preview_b64: Optional[str] = None  # الصورة المصغرة (لو وُجدت كنص base64)


@dataclass
class PollOption:
    local_id: int
    name: str


@dataclass
class Poll:
    name: str
    content_type: Optional[str] = None
    options: List[PollOption] = field(default_factory=list)


@dataclass
class VCard:
    formatted_name: Optional[str] = None
    content: Optional[str] = None  # نص vCard كامل BEGIN:VCARD...


class MessageType(str, Enum):
    CHAT = "chat"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PTT = "ptt"
    STICKER = "sticker"
    DOCUMENT = "document"
    LOCATION = "location"
    VCARD = "vcard"
    POLL_CREATION = "poll_creation"
    UNKNOWN = "unknown"


# ---------- Main aggregate ----------
class Message:
    """
    واجهتك الأساسية: مرّر dict_data مباشرة.
    """
    def __init__(self, data: Dict[str, Any]):
        self.raw: Dict[str, Any] = data

        # الهوية والتوقيت
        self.id: str = str(_pick(data, "id", default=""))
        self.timestamp: Optional[int] = _to_int(_pick(data, "timestamp", "t", default=None), default=0) or None
        self.datetime: Optional[datetime] = _epoch_to_dt(self.timestamp)
        self.from_me: bool = bool(data.get("fromMe", False))
        self.is_forwarded: bool = bool(data.get("isForwarded", False))
        self.forwarding_score: Optional[int] = _pick(data, "forwardingScore", default=None)

        # القناة (قروب/خاص) والمرسل
        self.chat: Chat = Chat.from_message(data)
        self.sender: Contact = Contact.from_message(data)

        # نوع الرسالة
        self.kind: MessageType = self._detect_kind(data)

        # نص/منشن/كابتشن
        self.text: Optional[str] = self._extract_text(data)
        self.mentions: List[str] = list(data.get("mentionedJidList") or [])

        # كيانات متخصصة (واحد منها فقط عادة)
        self.media: Optional[Media] = self._build_media_if_any(data, self.kind)
        self.location: Optional[Location] = self._build_location_if_any(data, self.kind)
        self.poll: Optional[Poll] = self._build_poll_if_any(data, self.kind)
        self.vcard: Optional[VCard] = self._build_vcard_if_any(data, self.kind)

    # --------- Builders / Detectors ----------
    def _detect_kind(self, d: Dict[str, Any]) -> MessageType:
        t = d.get("type")
        if t in set(m.value for m in MessageType):
            return MessageType(t)  # وثّق إن النوع جاي جاهز

        # سلوك بديل لو ما فيه type (مثل رسائل الشات النصية في أمثلتك)
        if "lat" in d and "lng" in d:
            return MessageType.LOCATION
        if "pollOptions" in d or "pollName" in d:
            return MessageType.POLL_CREATION
        body_or_content = _pick(d, "content", "body", default=None)
        if isinstance(body_or_content, str):
            if body_or_content.startswith("BEGIN:VCARD"):
                return MessageType.VCARD
            # heuristic بسيط: base64 طويل عادة للميديا، نص قصير غالبًا شات
            if len(body_or_content) < 200 and d.get("mediaData") in (None, {}):
                return MessageType.CHAT

        # ميديا عامة: وجود هذه الحقول مؤشر قوي
        if any(k in d for k in ("filehash", "encFilehash", "directPath", "deprecatedMms3Url", "mediaKey")):
            # تحديد أدق إن أمكن
            mt = d.get("mimetype", "")
            if mt.startswith("image/"):
                return MessageType.IMAGE
            if mt.startswith("video/"):
                return MessageType.VIDEO
            if mt.startswith("audio/"):
                # WhatsApp يميز ptt أحيانًا عبر type، لكن إن ما وُجد نتركها صوت
                return MessageType.AUDIO
            # fallback حسب naming الشائع
            if "pageCount" in d:
                return MessageType.DOCUMENT
        # آخر محاولة: أسماء الملفات/الكابتشن
        if _pick(d, "caption", default=None) is not None:
            # عادة يكون مع صورة/فيديو/مستند
            return MessageType.IMAGE

        return MessageType.UNKNOWN

    def _extract_text(self, d: Dict[str, Any]) -> Optional[str]:
        # للرسائل النصية والاستبيان والفي كارد والموقع نقرأ من body/content
        if self.kind in {MessageType.CHAT, MessageType.POLL_CREATION, MessageType.VCARD, MessageType.LOCATION}:
            return _pick(d, "body", "content", default=None)
        # للميديا نرجّح الكابتشن لو فيه
        if self.kind in {MessageType.IMAGE, MessageType.VIDEO, MessageType.DOCUMENT, MessageType.STICKER, MessageType.AUDIO, MessageType.PTT}:
            return _pick(d, "caption", default=None)
        # غير ذلك
        return _pick(d, "body", "content", default=None)

    def _build_media_if_any(self, d: Dict[str, Any], kind: MessageType) -> Optional[Media]:
        if kind not in {MessageType.IMAGE, MessageType.VIDEO, MessageType.AUDIO, MessageType.PTT, MessageType.STICKER, MessageType.DOCUMENT}:
            # قد تكون رسائل الشات تحمل body نص صِرف؛ نتجنب اعتبارها ميديا
            # ولو كانت ميديا بدون type، المؤشرات أدناه ستلتقطها إن لزم.
            pass

        # نعتبرها ميديا إن توفرت مؤشرات
        has_media_signals = any(k in d for k in ("filehash", "encFilehash", "directPath", "deprecatedMms3Url", "mediaKey", "mimetype", "pageCount", "height", "width"))
        if not has_media_signals and kind not in {MessageType.IMAGE, MessageType.VIDEO, MessageType.AUDIO, MessageType.PTT, MessageType.STICKER, MessageType.DOCUMENT}:
            return None

        return Media(
            kind=kind.value if kind != MessageType.UNKNOWN else "unknown",
            mimetype=_pick(d, "mimetype", default=None),
            size=_pick(d, "size", default=None),
            width=_pick(d, "width", default=None),
            height=_pick(d, "height", default=None),
            duration=_pick(d, "duration", default=None),
            page_count=_pick(d, "pageCount", default=None),
            filehash=_pick(d, "filehash", default=None),
            enc_filehash=_pick(d, "encFilehash", default=None),
            direct_path=_pick(d, "directPath", default=None),
            deprecated_url=_pick(d, "deprecatedMms3Url", default=None),
            media_key=_pick(d, "mediaKey", default=None),
            caption=_pick(d, "caption", default=None),
            content_b64=_pick(d, "content", "body", default=None),
        )

    def _build_location_if_any(self, d: Dict[str, Any], kind: MessageType) -> Optional[Location]:
        if kind != MessageType.LOCATION:
            return None
        return Location(
            latitude=_pick(d, "lat", default=None),
            longitude=_pick(d, "lng", default=None),
            label=_pick(d, "loc", default=None),
            preview_b64=_pick(d, "content", "body", default=None),
        )

    def _build_poll_if_any(self, d: Dict[str, Any], kind: MessageType) -> Optional[Poll]:
        if kind != MessageType.POLL_CREATION:
            return None
        options = []
        for opt in d.get("pollOptions", []) or []:
            options.append(PollOption(local_id=int(opt.get("localId", 0)), name=str(opt.get("name", ""))))
        return Poll(name=_pick(d, "pollName", default=""), content_type=_pick(d, "pollContentType", default=None), options=options)

    def _build_vcard_if_any(self, d: Dict[str, Any], kind: MessageType) -> Optional[VCard]:
        if kind != MessageType.VCARD:
            return None
        return VCard(
            formatted_name=_pick(d, "vcardFormattedName", default=None),
            content=_pick(d, "content", "body", default=None),
        )

    # --------- Utilities ----------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "from_me": self.from_me,
            "is_forwarded": self.is_forwarded,
            "forwarding_score": self.forwarding_score,
            "kind": self.kind.value,
            "chat": {
                "jid": str(self.chat.jid),
                "is_group": self.chat.is_group,
                "title": self.chat.title,
            },
            "sender": {
                "jid": str(self.sender.jid),
                "name": self.sender.name,
                "pushname": self.sender.pushname,
                "verified_name": self.sender.verified_name,
                "is_business": self.sender.is_business,
                "is_me": self.sender.is_me,
            },
            "text": self.text,
            "mentions": self.mentions,
            "media": asdict(self.media) if self.media else None,
            "location": asdict(self.location) if self.location else None,
            "poll": {
                "name": self.poll.name,
                "content_type": self.poll.content_type,
                "options": [asdict(o) for o in self.poll.options],
            } if self.poll else None,
            "vcard": asdict(self.vcard) if self.vcard else None,
        }

    def __repr__(self) -> str:
        base = f"<Message {self.kind.value} id={self.id[:12]} chat={self.chat.jid} sender={self.sender.jid}>"
        if self.text:
            return base + f" text={self.text[:40]!r}>"
        return base + ">"


# ---------- Example usage ----------
# msg = Message(dict_data)
# print(msg.kind, msg.chat.is_group, msg.sender.jid, msg.text)
# print(msg.media)
# print(msg.location)
# print(msg.poll)
# print(msg.vcard)
# print(msg.to_dict())
