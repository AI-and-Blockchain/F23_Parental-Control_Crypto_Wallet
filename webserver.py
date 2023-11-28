import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import atexit
from . import middleware


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
                chat_logs[chatId] = middleware.STARTCONVOPROMPT.copy()

            self.wfile.write(bytes(json.dumps(chat_logs[chatId]), "utf-8"))


        if self.path == "/callAPI":
            content_length = int(self.headers.get("Content-Length"))

            chatId = self.headers.get("chatid")
            if (not chatId): return

            content = self.rfile.read(content_length).decode("utf-8")
            if (len(content) == 0): return

            [retStr, chat_log] = middleware.callAPI(chatId, content)

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
