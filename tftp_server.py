import tftpy
import os
import logging

class VerboseTftpHandler(tftpy.TftpPacketTypes.TftpPacket):
    def handle(self, context):
        logger = logging.getLogger('tftpy')
        if hasattr(self, 'filename'):
            logger.info(f"Processing request for file: {self.filename}")
        return super().handle(context)

class CustomTftpServer(tftpy.TftpServer):
    def __init__(self, root):
        super().__init__(root)
        # Set up logging
        self.logger = logging.getLogger('tftpy')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def handle_packet(self, packet, client_address):
        """Override to add more detailed logging"""
        ptype = packet.__class__.__name__
        self.logger.info(f"Received {ptype} from {client_address[0]}:{client_address[1]}")
        
        if hasattr(packet, 'filename'):
            self.logger.info(f"File requested: {packet.filename}")
        
        if isinstance(packet, tftpy.TftpPacketDAT):
            self.logger.info(f"Sending block #{packet.blocknumber} to {client_address[0]}:{client_address[1]}")
        elif isinstance(packet, tftpy.TftpPacketACK):
            self.logger.info(f"Received ACK for block #{packet.blocknumber} from {client_address[0]}:{client_address[1]}")
        
        return super().handle_packet(packet, client_address)

class TFTPServerWrapper:
    def __init__(self):
        self.server = None
        
    def run_server(self, server_ip):
        try:
            # Create custom TFTP server instance with verbose logging
            self.server = CustomTftpServer('tftp')
            
            # Log server start
            print(f"\n{'='*50}")
            print(f"Starting TFTP server on {server_ip}:69")
            print(f"Serving files from directory: {os.path.abspath('tftp')}")
            print(f"{'='*50}\n")
            
            # List available files
            files = os.listdir('tftp')
            if files:
                print("Available files:")
                for file in files:
                    file_path = os.path.join('tftp', file)
                    file_size = os.path.getsize(file_path)
                    print(f"- {file} ({file_size} bytes)")
            else:
                print("No files available in TFTP directory")
            print(f"\n{'='*50}")
            
            # Start the server
            self.server.listen(server_ip, 69)
            
        except Exception as e:
            print(f"Error starting TFTP server: {str(e)}")
            
    def stop_server(self):
        if self.server:
            try:
                print(f"\n{'='*50}")
                print("Stopping TFTP server...")
                self.server.stop()
                print("TFTP server stopped successfully")
                print(f"{'='*50}\n")
            except Exception as e:
                print(f"Error stopping TFTP server: {str(e)}")

# Create a global instance
tftp_server_instance = TFTPServerWrapper()

def run_tftp_server(server_ip):
    tftp_server_instance.run_server(server_ip)

def stop_server():
    tftp_server_instance.stop_server()
    