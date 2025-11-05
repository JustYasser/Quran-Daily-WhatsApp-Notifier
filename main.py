import job
import signal
import sys
import bot
from flask import Flask, jsonify, request


# app for webhook
app = Flask(__name__)

# route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    
    req_json = request.json
    event = req_json.get("event","").lower()
    print("Received webhook event:", event)
    
    # handle message event
    if event == "onmessage":
        bot.receive_message(req_json)
    return jsonify({"status": "success"})

task_ = job.start_task()

def handle_exit(signum, frame):
    job.stop_task()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    app.run(port=3000, debug=False, use_reloader=False)

# job.start_loop()

