import os
import platform
import subprocess
import json
from flask import Flask, request, jsonify, render_template
from wakeonlan import send_magic_packet

app = Flask(__name__)

# Load the target devices from a JSON file
with open('devices.json', 'r') as f:
    targets = json.load(f)

# Function to check if a device is online
def is_online(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = f"ping {param} 1 {ip}"
    return os.system(command) == 0

# Function to shut down a device via SSH
def shutdown_device(target, delay=None):
    try:
        if delay is None:
            command = f"ssh -o StrictHostKeyChecking=no {target['ssh_user']}@{target['ip']} sudo /sbin/shutdown -h now"
        else:
            command = f"ssh -o StrictHostKeyChecking=no {target['ssh_user']}@{target['ip']} sudo /sbin/shutdown -h {delay}"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()
def shutdown_cancel_device(target):
    try:
        command = f"ssh -o StrictHostKeyChecking=no {target['ssh_user']}@{target['ip']} sudo /sbin/shutdown -c"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

# Route to trigger the Wake-on-LAN
@app.route('/wake', methods=['POST'])
def wake():
    try:
        data = request.get_json()
        mac_address = data['mac']

        # Send the magic packet
        send_magic_packet(mac_address)

        return jsonify({'status': 'success', 'message': f'Magic packet sent to {mac_address}'}), 200
    except KeyError:
        return jsonify({'status': 'error', 'message': 'MAC address is required'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to shut down a device
@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        data = request.get_json()
        target_id = data['id']
        delay = data.get('delay')

        # Find the target device by ID
        target = next((t for t in targets if t['id'] == target_id), None)
        if not target:
            return jsonify({'status': 'error', 'message': 'Target not found'}), 404

        success, message = shutdown_device(target, delay)

        if success:
            return jsonify({'status': 'success', 'message': f'Shutdown command sent to {target["ip"]}'}), 200
        else:
            return jsonify({'status': 'error', 'message': message}), 500
    except KeyError:
        return jsonify({'status': 'error', 'message': 'ID is required'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/shutdown/cancel', methods=['GET'], )
def shutdown_cancel():
    try:
        target_id = request.args.get('id')

        # Find the target device by ID
        target = next((t for t in targets if t['id'] == int(target_id)), None)
        if not target:
            return 'Target not found ' + str(target_id) + ' ' + str(targets), 404


        success, message = shutdown_cancel_device(target)

        if success:
            return f'Shutdown cancel command sent to {target["ip"]}', 200
        else:
            return message, 500
    except KeyError:
        return 'ID is required', 400
    except Exception as e:
        return str(e), 500
# Route to check the status of devices
@app.route('/status', methods=['GET'])
def status():
    statuses = []
    # Get optional parameters
    device = request.args.get('device')

    if device:
        # If a device ID is provided, return only that device
        # Find the target device by ID
        target = next((t for t in targets if t['id'] == int(device)), None)
        if not target:
            return jsonify({'status': 'error', 'message': 'Target not found'}), 404
        online_status = is_online(target['ip'])
        statuses = {
            'id': target['id'],
            'name': target['name'],
            'mac': target['mac'],
            'ip': target['ip'],
            'online': online_status
        }
        return jsonify(statuses)

    # If no device ID is provided, return all devices
    for target in targets:
        online_status = is_online(target['ip'])
        statuses.append({
            'id': target['id'],
            'name': target['name'],
            'mac': target['mac'],
            'ip': target['ip'],
            'online': online_status
        })
    return jsonify(statuses)

# Home route that renders the HTML page
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', targets=targets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
