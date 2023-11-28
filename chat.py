import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI
import os
import atexit

client = OpenAI(
    api_key = os.getenv('apitoken') or json.load(open('config.json'))['APITOKEN']
)

STARTCONVOPROMPT = [{"role": "system", "content": "you are an AI chat bot that is helping a user learn more about their crypto wallet and crypto currencies as a whole."}]
chat_logs = dict()


def save_chat_logs():
    with open('chat_logs.json', 'w') as file:
        json.dump(chat_logs, file)


def load_chat_logs():
    global chat_logs
    try:
        with open('chat_logs.json', 'r') as file:
            chat_logs = json.load(file)
    except FileNotFoundError:
        pass  # If the file doesn't exist, start with an empty chat_logs dictionary


def callAPI(chatId, uinp):
    try:
        if len(uinp) == 0:
            return 'Please provide a message!'
        
        # get the previous data or init
        if chatId not in chat_logs: return
        chat_logs[chatId].append({"role": "user", "content": "user: " + uinp})

        chat_completion = client.chat.completions.create(
            messages=chat_logs[chatId],
            model="gpt-3.5-turbo",
            stream=True
        )

        retStr = ''
        for part in chat_completion:
            retStr += part.choices[0].delta.content or ""

        chat_logs[chatId].append({"role": "assistant", "content": retStr})

        return retStr, chat_logs[chatId]
    except Exception as err:
        return str(err)
    

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open('chat.html')
            content = f.read()
            f.close()
            self.wfile.write(bytes(content, "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/initChat":
            chatId = self.headers.get("chatId")
            if (not chatId): return

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if chatId not in chat_logs:
                chat_logs[chatId] = STARTCONVOPROMPT.copy()

            self.wfile.write(bytes(json.dumps(chat_logs[chatId]), "utf-8"))


        if self.path == "/callAPI":
            content_length = int(self.headers.get("Content-Length"))

            chatId = self.headers.get("chatid")
            if (not chatId): return

            content = self.rfile.read(content_length).decode("utf-8")
            if (len(content) == 0): return

            [retStr, chat_log] = callAPI(chatId, content)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write(bytes(retStr, "utf-8"))


atexit.register(save_chat_logs)
load_chat_logs()

webServer = HTTPServer((hostName, serverPort), MyServer)
print("Server started http://%s:%s" % (hostName, serverPort))


try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")
