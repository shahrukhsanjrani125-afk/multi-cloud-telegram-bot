import subprocess
import time
import requests
import stem.process
from stem.control import Controller
import logging

logger = logging.getLogger(__name__)

class TorManager:
    def __init__(self, torrc_path="/etc/tor/torrc", control_port=9051):
        self.torrc_path = torrc_path
        self.control_port = control_port
        self.tor_process = None
        self.controller = None
    
    def start_tor(self):
        """Start Tor service with SOCKS5 proxy"""
        try:
            # Kill existing tor processes
            subprocess.run(["pkill", "-f", "tor"])
            time.sleep(2)
            
            # Configure and start Tor
            torrc_config = f"""
            SocksPort 9050
            ControlPort {self.control_port}
            HashedControlPassword {self._hash_password("shark_erp_password")}
            Log notice file /var/log/tor/notices.log
            DataDirectory /var/lib/tor
            """
            
            with open(self.torrc_path, 'w') as f:
                f.write(torrc_config)
            
            # Start Tor process
            self.tor_process = stem.process.launch_tor_with_config(
                config={
                    'SocksPort': str(9050),
                    'ControlPort': str(self.control_port),
                    'HashedControlPassword': self._hash_password("shark_erp_password"),
                },
                init_msg_handler=lambda line: logger.info(f"TOR: {line}"),
            )
            
            # Connect to control port
            self.controller = Controller.from_port(port=self.control_port)
            self.controller.authenticate(password="shark_erp_password")
            
            logger.info("Tor SOCKS5 proxy started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            return False
    
    def renew_identity(self):
        """Renew Tor circuit for new IP"""
        if self.controller:
            self.controller.signal("NEWNYM")
            logger.info("Tor identity renewed")
            return True
        return False
    
    def _hash_password(self, password):
        """Hash password for Tor control"""
        from hashlib import sha256
        import base64
        hashed = sha256(password.encode()).digest()
        return base64.b64encode(hashed).decode()
    
    def stop_tor(self):
        """Stop Tor service"""
        if self.tor_process:
            self.tor_process.terminate()
            self.tor_process.wait()
            logger.info("Tor service stopped")