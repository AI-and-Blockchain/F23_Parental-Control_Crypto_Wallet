from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('apitoken'),
)

chat_log = [{"role": "system", "content": "you are an AI chat bot that is helping a user learn more about their crypto wallet and crypto currencies as a whole."}]

def callAPI(uinp):
    try:
        if len(uinp) == 0:
            return 'Please provide a message!'
        
        chat_log.append({"role": "user", "content": "user: " + uinp})

        chat_completion = client.chat.completions.create(
            messages=chat_log,
            model="gpt-3.5-turbo",
            stream=True
        )

        retStr = ''
        for part in chat_completion:
            retStr += part.choices[0].delta.content or ""

        # chat_log.append({"role": "user", "content": content})
        chat_log.append({"role": "assistant", "content": retStr})

        return retStr, chat_log
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
            self.wfile.write(bytes("<html><head><title>OpenAI API</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<h1>OpenAI API Example</h1>", "utf-8"))
            self.wfile.write(bytes("<form id='apiForm' method='POST' action='/callAPI'>", "utf-8"))
            self.wfile.write(bytes("<input type='text' name='content' id='content' placeholder='Enter a message'>", "utf-8"))
            self.wfile.write(bytes("<input type='button' value='Call API' id='callApiButton'>", "utf-8"))
            self.wfile.write(bytes("</form>", "utf-8"))
            self.wfile.write(bytes("<div id='chatLog'></div>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/callAPI":
            content_length = int(self.headers.get("Content-Length"))
            content = self.rfile.read(content_length).decode("utf-8")
            [retStr, chat_log] = callAPI(content.split('content=')[1])
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(retStr, "utf-8"))

webServer = HTTPServer((hostName, serverPort), MyServer)
print("Server started http://%s:%s" % (hostName, serverPort))

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")
