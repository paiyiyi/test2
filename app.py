# -*- coding: utf-8 -*-
from flask import Flask, request, send_file, abort, jsonify
from io import BytesIO
import base64
import threading

app = Flask(__name__)

latest_frame = None          # 内存缓存
lock = threading.Lock()

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    data = request.get_json(force=True)
    img_b64 = data.get('image', '')
    if not img_b64:
        return jsonify({'error': 'no image'}), 400

    try:
        img_bin = base64.b64decode(img_b64)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    with lock:
        latest_frame = img_bin
    return jsonify({'result': 'ok'})

@app.route('/latest.jpg')
def latest():
    with lock:
        if latest_frame is None:
            abort(404)
        return send_file(
            BytesIO(latest_frame),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name='latest.jpg',
            max_age=0
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)