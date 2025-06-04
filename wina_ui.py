from flask import Flask, render_template, request, Response, jsonify
import subprocess
import os
import json

app = Flask(__name__)
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'ui_configs')
os.makedirs(CONFIG_DIR, exist_ok=True)
current_process = None

@app.route('/')
def index():
    presets = [f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    return render_template('index.html', presets=presets)

@app.route('/run', methods=['POST'])
def run_command():
    global current_process
    if current_process is not None:
        return 'Another process is running', 400
    data = request.get_json()
    model = data.get('model')
    sparsity = str(data.get('sparsity', 0.5))
    mode = data.get('mode', 'wina')
    greedy = data.get('greedy', False)
    run_type = data.get('run_type', 'baseline')

    cmd = [
        'python', 'eval.py',
        '--base_model', model,
        '--save_path', 'outputs',
        '--sparse_mode', mode,
        '--sparsity', sparsity
    ]
    if greedy:
        cmd.append('--greedy')
    current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return '', 204

@app.route('/stream')
def stream():
    def generate():
        global current_process
        if current_process is None:
            yield 'data:No process running\n\n'
            return
        for line in iter(current_process.stdout.readline, ''):
            yield f'data:{line}\n\n'
        current_process.wait()
        current_process = None
    return Response(generate(), mimetype='text/event-stream')

@app.route('/presets/<name>', methods=['GET'])
def get_preset(name):
    path = os.path.join(CONFIG_DIR, f'{name}.json')
    if not os.path.exists(path):
        return jsonify({}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/presets/<name>', methods=['POST'])
def save_preset(name):
    path = os.path.join(CONFIG_DIR, f'{name}.json')
    with open(path, 'w') as f:
        json.dump(request.get_json(), f, indent=2)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
