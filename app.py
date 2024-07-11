# app.py
from flask import Flask, request, render_template, jsonify
from psn_receiver import PSNReceiver
from data_converter import DataConverter
import json
import os
import threading
import time
app = Flask(__name__)

CONFIG_FILE = 'config.json'

# Load configurations
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'psn_ip': '0.0.0.0',
        'psn_port': 56565,
        'psn_multicast_ip': '236.10.10.10',
        'mappings': []
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

config = load_config()
psn_receiver = PSNReceiver()
data_converter = DataConverter(CONFIG_FILE)

@app.route('/')
def index():
    return render_template('index.html', config=config)

@app.route('/configure', methods=['POST'])
def configure():
    config['psn_ip'] = request.form['psn_ip']
    config['psn_port'] = int(request.form['psn_port'])
    save_config(config)
    return jsonify('Configuration saved')

@app.route('/add_osc_mapping', methods=['POST'])
def add_osc_mapping():
    mapping = {
        'psn_source': request.form['psn_source'],
        'server_name': request.form['server_name'],
        'tracker_id': int(request.form['tracker_id']),
        'tracker_name': request.form['tracker_name'],
        'axis': request.form['axis'],
        'psn_min': float(request.form['psn_min']),
        'psn_max': float(request.form['psn_max']),
        'osc_min': float(request.form['osc_min']),
        'osc_max': float(request.form['osc_max']),
        'osc_addr': request.form['osc_addr'],
    }
    config['mappings'].append(mapping)
    save_config(config)
    data_converter.add_mapping(
        mapping['psn_source'],
        mapping['server_name'],
        mapping['tracker_id'],
        mapping['tracker_name'],
        mapping['axis'],
        mapping['psn_min'],
        mapping['psn_max'],
        mapping['osc_min'],
        mapping['osc_max'],
        mapping['osc_addr']
    )
    return jsonify('OSC Mapping added')

@app.route('/add_sacn_mapping', methods=['POST'])
def add_sacn_mapping():
    mapping = {
        'psn_source': request.form['psn_source'],
        'server_name': request.form['server_name'],
        'tracker_id': int(request.form['tracker_id']),
        'tracker_name': request.form['tracker_name'],
        'axis': request.form['axis'],
        'psn_min': float(request.form['psn_min']),
        'psn_max': float(request.form['psn_max']),
        'dmx_min': int(request.form['dmx_min']),
        'dmx_max': int(request.form['dmx_max']),
        'sacn_universe': int(request.form['sacn_universe']),
        'sacn_addr': int(request.form['sacn_addr']),
    }
    config['mappings'].append(mapping)
    save_config(config)
    data_converter.add_mapping(
        mapping['psn_source'],
        mapping['server_name'],
        mapping['tracker_id'],
        mapping['tracker_name'],
        mapping['axis'],
        mapping['psn_min'],
        mapping['psn_max'],
        mapping['dmx_min'],
        mapping['dmx_max'],
        mapping['sacn_universe'],
        mapping['sacn_addr']
    )
    return jsonify('SACN Mapping added')

@app.route('/start', methods=['POST'])
def start():
    def run():
        psn_receiver.start_psn()
        psn_receiver.start_dmx()
        while True:
            try:
                tracker_id, data = psn_receiver.receive_data()
                if tracker_id is not None:
                    psn_data = {
                        tracker_id: data
                    }
                    print("psn data received ",psn_data)
                    data_converter.convert_data(psn_data)
                    time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
    threading.Thread(target=run).start()
    return jsonify('Data conversion started')

@app.route('/stop', methods=['POST'])
def stop():
    psn_receiver.stop_dmx()
    psn_receiver.stop_psn()
    data_converter.stop()
    return jsonify('Data conversion stopped')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
