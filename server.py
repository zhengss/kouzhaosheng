import json
import os
import base64
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler

DATA_FILE = 'data/products.json'
UPLOADS_DIR = 'uploads'

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    products = json.load(f)
            else:
                products = []
            self.wfile.write(json.dumps(products).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/products':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                name = data.get('name', '')
                cate = data.get('cate', '')
                desc = data.get('desc', '')
                img_base64 = data.get('img', '')
                
                if not name or not img_base64:
                    self.send_error_response(400, '缺少必填字段')
                    return
                
                if not os.path.exists(UPLOADS_DIR):
                    os.makedirs(UPLOADS_DIR)
                
                ext = img_base64.split(';')[0].split('/')[1] if 'data:image' in img_base64 else 'png'
                filename = f"{uuid.uuid4().hex}.{ext}"
                img_path = os.path.join(UPLOADS_DIR, filename)
                
                img_data = img_base64
                if ',' in img_base64:
                    img_data = img_base64.split(',')[1]
                
                with open(img_path, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                
                products = []
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                
                new_product = {
                    'id': len(products) + 1,
                    'name': name,
                    'cate': cate,
                    'desc': desc,
                    'img': f'/{UPLOADS_DIR}/{filename}'
                }
                products.append(new_product)
                
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'product': new_product}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, str(e))
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/api/products/'):
            try:
                product_id = int(self.path.split('/')[-1])
                
                products = []
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                
                product_to_delete = None
                for p in products:
                    if p['id'] == product_id:
                        product_to_delete = p
                        break
                
                if not product_to_delete:
                    self.send_error_response(404, '产品不存在')
                    return
                
                img_path = product_to_delete.get('img', '')
                if img_path and img_path.startswith('/uploads/'):
                    full_path = img_path[1:]
                    if os.path.exists(full_path):
                        os.remove(full_path)
                
                products = [p for p in products if p['id'] != product_id]
                
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, str(e))
        else:
            self.send_error(404)

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))

def main():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    
    server = HTTPServer(('0.0.0.0', 8888), MyHandler)
    print('服务器运行中: http://localhost:8888')
    server.serve_forever()

if __name__ == '__main__':
    main()