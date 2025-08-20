from http.server import BaseHTTPRequestHandler
import json
import apprise
from io import BytesIO

def handler(request):
    # 将 Vercel 的请求转换为 BaseHTTPRequestHandler 兼容格式
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self):
            self.request = request
            self.wfile = BytesIO()
        
        def do_GET(self):
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Apprise Vercel is working, use POST method to send notifications.')
            return self.wfile.getvalue()
        
        def do_POST(self):
            if self.request.headers.get('content-type') != 'application/json':
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Content-Type must be application/json')
                return self.wfile.getvalue()
            
            try:
                data = json.loads(self.request.body)
                apobj = apprise.Apprise()
                
                for url in data['urls'].split(","):
                    apobj.add(url)
                
                if apobj.notify(
                    body=data['body'],
                    title=data.get('title', ''),
                    notify_type=data.get('type', 'info'),
                    body_format=data.get('format', 'text'),
                ):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Error sending notifications')
                
                return self.wfile.getvalue()
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode())
                return self.wfile.getvalue()
    
    # 根据请求方法调用对应的处理函数
    handler = RequestHandler()
    if request.method == 'GET':
        return {
            'statusCode': 400,
            'body': handler.do_GET()
        }
    elif request.method == 'POST':
        return {
            'statusCode': 200,
            'body': handler.do_POST()
        }
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }
