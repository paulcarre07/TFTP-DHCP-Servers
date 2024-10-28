from flask import Flask, render_template, request, jsonify
import threading
import dhcp_server
from tftp_server import tftp_server_instance
import os
import ipaddress

app = Flask(__name__)

dhcp_thread = None
tftp_thread = None
server_ip = '192.168.1.1'
client_ip = '192.168.1.10'
config_filename = 'cisco-config.txt'
tftp_directory = 'tftp'

def validate_ip_addresses(server_ip, client_ip):
    try:
        server = ipaddress.ip_address(server_ip)
        client = ipaddress.ip_address(client_ip)
    except ValueError:
        return False, "Invalid IP address format"

    server_network = ipaddress.ip_network(f"{server_ip}/24", strict=False)
    if client not in server_network:
        return False, "Client IP must be in the same /24 subnet as the Server IP"

    return True, ""

@app.route('/')
def index():
    return render_template('index.html', server_ip=server_ip, client_ip=client_ip, config_filename=config_filename)

@app.route('/get_tftp_files')
def get_tftp_files():
    files = [f for f in os.listdir(tftp_directory) if os.path.isfile(os.path.join(tftp_directory, f))]
    return jsonify(files)

def run_tftp_server_thread(server_ip):
    tftp_server_instance.run_server(server_ip)

@app.route('/start_servers', methods=['POST'])
def start_servers():
    global dhcp_thread, tftp_thread, server_ip, client_ip, config_filename
    
    server_ip = request.form['server_ip']
    client_ip = request.form['client_ip']
    config_filename = request.form['config_filename']
    
    # Validate IP addresses
    is_valid, error_message = validate_ip_addresses(server_ip, client_ip)
    if not is_valid:
        return jsonify({"status": "error", "message": error_message}), 400

    # Validate config file exists in TFTP directory
    if not os.path.isfile(os.path.join(tftp_directory, config_filename)):
        return jsonify({"status": "error", "message": "Config file not found in TFTP directory"}), 400

    if dhcp_thread is None or not dhcp_thread.is_alive():
        dhcp_thread = threading.Thread(target=dhcp_server.run_dhcp_server, 
                                     args=(server_ip, client_ip, os.path.join(tftp_directory, config_filename)))
        dhcp_thread.start()
    
    if tftp_thread is None or not tftp_thread.is_alive():
        tftp_thread = threading.Thread(target=run_tftp_server_thread, args=(server_ip,))
        tftp_thread.start()
    
    return jsonify({"status": "success", "message": "Servers started"})

@app.route('/stop_servers', methods=['POST'])
def stop_servers():
    global dhcp_thread, tftp_thread
    
    if dhcp_thread and dhcp_thread.is_alive():
        dhcp_server.stop_server()
        dhcp_thread.join()
        dhcp_thread = None
    
    if tftp_thread and tftp_thread.is_alive():
        tftp_server_instance.stop_server()
        tftp_thread.join()
        tftp_thread = None
    
    return jsonify({"status": "success", "message": "Servers stopped"})

if __name__ == '__main__':
    # Ensure TFTP directory exists
    os.makedirs(tftp_directory, exist_ok=True)
    app.run(debug=True)