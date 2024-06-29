# app.py
from flask import Flask, request, render_template, jsonify
from psn_receiver import PSNReceiver
from data_converter import DataConverter
import json
import os
import threading

app = Flask(__name__)

CONFIG_FILE = 'config.json'

# Load configurationss
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'psn_ip': '0.0.0.0',
        'psn_port': 56565,
        'mappings': []
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

config = load_config()
psn_receiver = PSNReceiver(config['psn_ip'], config['psn_port'])
data_converter = DataConverter(CONFIG_FILE)

# Apply mappings from config
# for mapping in config['mappings']:
#     data_converter.add_mapping(
#         mapping['psn_field'],
#         mapping['sacn_universe'],
#         mapping['sacn_address'],
#         mapping['osc_ip'],
#         mapping['osc_port'],
#         mapping['osc_address'],
#         mapping['scale']
#     )

@app.route('/')
def index():
    return render_template('index.html', config=config)

@app.route('/configure', methods=['POST'])
def configure():
    config['psn_ip'] = request.form['psn_ip']
    config['psn_port'] = int(request.form['psn_port'])
    save_config(config)
    return jsonify('Configuration saved')

@app.route('/add_mapping', methods=['POST'])
def add_mapping():
    mapping = {
        'psn_field': request.form['psn_field'],
        'sacn_universe': int(request.form['sacn_universe']),
        'sacn_address': int(request.form['sacn_address']),
        'osc_ip': request.form['osc_ip'],
        'osc_port': int(request.form['osc_port']),
        'osc_address': request.form['osc_address'],
        'scale': float(request.form['scale'])
    }
    config['mappings'].append(mapping)
    save_config(config)
    data_converter.add_mapping(
        mapping['psn_field'],
        mapping['sacn_universe'],
        mapping['sacn_address'],
        mapping['osc_ip'],
        mapping['osc_port'],
        mapping['osc_address'],
        mapping['scale']
    )
    return jsonify('Mapping added')

@app.route('/start', methods=['POST'])
def start():
    def run():
        while True:
            tracker_id, position_data, speed_data, orientation_data = psn_receiver.receive_data()
            psn_data = {
                'tracker_id':tracker_id,
                'position': position_data,
                'speed': speed_data,
                'orientation': orientation_data
            }
            data_converter.convert_data(psn_data)
    threading.Thread(target=run).start()
    return jsonify('Data conversion started now')

@app.route('/stop', methods=['POST'])
def stop():
    data_converter.stop()
    return jsonify('Data conversion stopped')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
