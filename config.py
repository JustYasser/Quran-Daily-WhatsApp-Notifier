import pytz
from client import Client

# here put the prefix you want to use
BOT_PREFIX = "!"
# here put the admin phone numbers in list like that
ADMINS = ['966500000000@c.us']

# here you can customize the notify poll, {today} is for today name in arabic
poll_text = 'ورد اليوم {today}'
poll_options = ['✅ تم', '❌ لم يتم', '❗ نسيان', '⌛ تأخر']

# here put your timezone
TIMEZONE = pytz.timezone('Asia/Riyadh')

# Please don't replace these variables unless you know what you're doing
SETTINGS_FILE = 'settings.json'
client_host = "http://localhost"
client_port = 21465
client_api_url = f"{client_host}:{client_port}/api"
client_secret_key = 'THISISMYSECURETOKEN'

client_session = 'NotifyBotSession'
client = Client(client_api_url, client_secret_key, client_session)

poll_sender_session = "PollSenderSession"
poll_sender_client = Client(client_api_url, client_secret_key, poll_sender_session)

# generate token and start session
token = client.generate_token()
# print("Generated token:", token)
client.set_token(token.get("token"))
client.start_session('http://localhost:3000/webhook')

# generate token and start poll sender session
poll_sender_token = poll_sender_client.generate_token()
# print("Generated Poll Sender token:", poll_sender_token)
poll_sender_client.set_token(poll_sender_token.get("token"))
poll_sender_client.start_session()

arabic_days = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']

help_message = """===============
اعداد المجموعة
===============
لتفعيل مجموعة استخدم امر:
{b}تفعيل

لتعطيل مجموعة استخدم امر:
{b}تعطيل

لإرسال تذكير بشكل يدوي استخدم امر:
{b}تصويت

===============
اعداد الوقت
===============
لمعرفة الزمن المتبقي للارسال التذكير القادم استخدم امر:
{b}متى

لمعرفة وقت التذكير خلال اليوم استخدم امر:
{b}وقت

لتغيير وقت التذكير خلال اليوم استخدم امر:
{b}وقت <الوقت الجديد بنظام 24 ساعة>
مثال لتعيين وقت التذكير الى الساعة 4:40 عصراً : {b}وقت 16:40


===============
اعداد الأيام المستثناة من التذكير
===============
لمعرفة الايام المستثناة من التذكير استخدم امر:
{b}مستثنى

لإضافة يوم مستثنى من التذكير استخدم امر:
{b}اضافة <اسم اليوم او رقمه في الاسبوع>

لإزالة يوم مستثنى من التذكير استخدم امر:
{b}ازالة <اسم اليوم او رقمه في الاسبوع>

===============
اعدادات التقرير الأسبوعي
===============
لمعرفة اليوم الحالي لإرسال التقرير الأسبوعي استخدم امر:
{b}يوم التقرير

لتغيير اليوم لإرسال التقرير الأسبوعي استخدم امر:
{b}يوم التقرير <اسم اليوم او رقمه في الاسبوع>
مثال لتعيين يوم إرسال التقرير الى الجمعة : {b}يوم التقرير الجمعة

ملاحظات:
- التقرير يُرسل دائمًا في يومه المخصص، إذا كان اليوم مشمول بالتذكير، سيتم إرسال التقرير قبل التذكير، أما إذا كان اليوم مستثنى من التذكير، فسيتم إرسال التقرير بدون إرسال التذكير لهذا اليوم
- عند تغيير يوم التقرير، يعتمد النظام اليوم الجديد مباشرة، وعند وصول ذلك اليوم، سيتم إرسال التقرير الأسبوعي لآخر 7 ايام قبل يوم التقرير
- بعد إرسال التقرير الاسبوعي، يحذف البوت جميع الأصوات المسجلة لديه للأسبوع السابق

===============
تنبيهات بخصوص آلية تحديد الأيام
===============
- ادخل اسم اليوم بشكل صحيح مع مراعاة الهمزات او ادخل رقم اليوم في الاسبوع
- عند ادخال رقم اليوم في الاسبوع يجب ان يكون بين 1 و7 على النحو التالي:
1 = الإثنين
2 = الثلاثاء
3 = الأربعاء
4 = الخميس
5 = الجمعة
6 = السبت
7 = الأحد""".format(b=BOT_PREFIX)