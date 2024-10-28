import socket
import struct
import os
import logging
from datetime import datetime

# DHCP message types
DHCP_DISCOVER = 1
DHCP_OFFER = 2
DHCP_REQUEST = 3
DHCP_ACK = 5

# DHCP options
DHCP_MESSAGE_TYPE = 53
DHCP_SERVER_ID = 54
DHCP_REQUESTED_IP = 50
DHCP_LEASE_TIME = 51
DHCP_SUBNET_MASK = 1
DHCP_ROUTER = 3
DHCP_DNS_SERVER = 6
DHCP_TFTP_SERVER = 66
DHCP_BOOTFILE = 67

# DHCP Message Type Names for logging
DHCP_TYPES = {
    1: "DISCOVER",
    2: "OFFER",
    3: "REQUEST",
    4: "DECLINE",
    5: "ACK",
    6: "NAK",
    7: "RELEASE",
    8: "INFORM"
}

class DHCPServer:
    def __init__(self):
        self.stop_flag = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('dhcp_server')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - DHCP - %(levelname)s - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        return logger

    def _format_mac(self, mac_bytes):
        """Convert MAC bytes to readable format"""
        return ':'.join(f'{b:02x}' for b in mac_bytes)

    def _format_packet_info(self, data):
        """Extract and format basic packet information"""
        if len(data) < 240:
            return None
            
        message_type = data[0]
        hardware_type = data[1]
        hardware_addr_len = data[2]
        xid = struct.unpack('!I', data[4:8])[0]
        client_mac = data[28:28+6]
        
        return {
            'transaction_id': f'0x{xid:08x}',
            'client_mac': self._format_mac(client_mac),
            'hardware_type': hardware_type,
            'hardware_addr_len': hardware_addr_len
        }

    def create_dhcp_packet(self, message_type, xid, client_mac, yiaddr, server_ip, config_path):
        self.logger.info(f"Creating DHCP {DHCP_TYPES.get(message_type, 'UNKNOWN')} packet:")
        self.logger.info(f"  - Transaction ID: 0x{xid:08x}")
        self.logger.info(f"  - Client MAC: {self._format_mac(client_mac)}")
        self.logger.info(f"  - Assigned IP: {yiaddr}")
        self.logger.info(f"  - Server IP: {server_ip}")
        self.logger.info(f"  - Config File: {os.path.basename(config_path)}")

        packet = struct.pack('!BBBBIHH',
            2,  # Boot reply
            1,  # Ethernet
            6,  # Hardware address length
            0,  # Hops
            xid,  # Transaction ID
            0,  # Seconds elapsed
            0   # Bootp flags
        )
        packet += socket.inet_aton('0.0.0.0')  # Client IP address
        packet += socket.inet_aton(yiaddr)  # Your (client) IP address
        packet += socket.inet_aton('0.0.0.0')  # Next server IP address
        packet += socket.inet_aton('0.0.0.0')  # Relay agent IP address
        packet += client_mac + b'\x00' * 10  # Client MAC address (padded to 16 bytes)
        packet += b'\x00' * 64  # Server host name
        packet += b'\x00' * 128  # Boot file name
        
        # Magic cookie
        packet += b'\x63\x82\x53\x63'
        
        # DHCP options
        packet += struct.pack('!BBB', DHCP_MESSAGE_TYPE, 1, message_type)
        packet += struct.pack('!BB4s', DHCP_SERVER_ID, 4, socket.inet_aton(server_ip))
        packet += struct.pack('!BBL', DHCP_LEASE_TIME, 4, 86400)  # 1 day lease
        packet += struct.pack('!BB4s', DHCP_SUBNET_MASK, 4, socket.inet_aton('255.255.255.0'))
        packet += struct.pack('!BB4s', DHCP_ROUTER, 4, socket.inet_aton(server_ip))
        packet += struct.pack('!BB4s', DHCP_DNS_SERVER, 4, socket.inet_aton('8.8.8.8'))
        packet += struct.pack('!BB4s', DHCP_TFTP_SERVER, 4, socket.inet_aton(server_ip))
        packet += struct.pack('!BB%ds' % len(os.path.basename(config_path)), 
                            DHCP_BOOTFILE, 
                            len(os.path.basename(config_path)), 
                            os.path.basename(config_path).encode())
        packet += b'\xff'  # End option
        
        return packet

    def create_dhcp_offer(self, xid, client_mac, yiaddr, server_ip, config_path):
        return self.create_dhcp_packet(DHCP_OFFER, xid, client_mac, yiaddr, server_ip, config_path)

    def create_dhcp_ack(self, xid, client_mac, yiaddr, server_ip, config_path):
        return self.create_dhcp_packet(DHCP_ACK, xid, client_mac, yiaddr, server_ip, config_path)

    def run_server(self, server_ip, client_ip, config_path):
        self.stop_flag = False
        server_port = 67
        client_port = 68

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind((server_ip, server_port))
            s.settimeout(1)

            # Print server startup information
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"DHCP Server Starting")
            self.logger.info(f"  Listening on: {server_ip}:{server_port}")
            self.logger.info(f"  Offering IP: {client_ip}")
            self.logger.info(f"  Config File: {config_path}")
            self.logger.info(f"{'='*50}\n")

            while not self.stop_flag:
                try:
                    data, addr = s.recvfrom(1024)
                    packet_info = self._format_packet_info(data)
                    
                    if not packet_info:
                        self.logger.warning(f"Received malformed packet from {addr[0]}:{addr[1]}")
                        continue

                    self.logger.info(f"Received packet from {addr[0]}:{addr[1]}")
                    self.logger.info(f"  Transaction ID: {packet_info['transaction_id']}")
                    self.logger.info(f"  Client MAC: {packet_info['client_mac']}")
                    
                    options = data[240:]
                    dhcp_message_type = None
                    
                    i = 0
                    while i < len(options):
                        option_type = options[i]
                        if option_type == 255:  # End option
                            break
                        if option_type == DHCP_MESSAGE_TYPE:
                            dhcp_message_type = options[i + 2]
                            break
                        option_length = options[i + 1]
                        i += 2 + option_length
                    
                    if dhcp_message_type == DHCP_DISCOVER:
                        self.logger.info(f"Processing DHCP DISCOVER")
                        offer_packet = self.create_dhcp_offer(
                            struct.unpack('!I', data[4:8])[0],
                            data[28:28+6],
                            client_ip,
                            server_ip,
                            config_path
                        )
                        s.sendto(offer_packet, ('<broadcast>', client_port))
                        self.logger.info(f"Sent DHCP OFFER to {packet_info['client_mac']}")
                        self.logger.info(f"  Offered IP: {client_ip}")
                    
                    elif dhcp_message_type == DHCP_REQUEST:
                        self.logger.info(f"Processing DHCP REQUEST")
                        ack_packet = self.create_dhcp_ack(
                            struct.unpack('!I', data[4:8])[0],
                            data[28:28+6],
                            client_ip,
                            server_ip,
                            config_path
                        )
                        s.sendto(ack_packet, ('<broadcast>', client_port))
                        self.logger.info(f"Sent DHCP ACK to {packet_info['client_mac']}")
                        self.logger.info(f"  Assigned IP: {client_ip}")

                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing DHCP packet: {str(e)}")

            self.logger.info(f"\n{'='*50}")
            self.logger.info("DHCP Server stopped")
            self.logger.info(f"{'='*50}\n")

    def stop_server(self):
        self.stop_flag = True

# Create global instance
dhcp_server_instance = DHCPServer()

def run_dhcp_server(server_ip, client_ip, config_path):
    dhcp_server_instance.run_server(server_ip, client_ip, config_path)

def stop_server():
    dhcp_server_instance.stop_server()
    