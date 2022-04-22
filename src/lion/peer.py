'''
MIT License

Copyright (c) 2022 Marcel Guinhos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__author__ = 'Marcel Guinhos'
__version__ = '0.0.1'

from enum import Enum
from threading import Thread
from socket import socket
from socket import gethostbyname, gethostname

import json

HOSTNAME = gethostname()
HOSTBYNAME = gethostbyname(HOSTNAME)

class Intent(Enum):
    Check=          b'ck'
    Info=           b'if'
    Message=        b'ms'

def each_ipv4():
    a, b, c, d = HOSTBYNAME.split('.')

    for d in range(2, 255):
        yield f'{a}.{b}.{c}.{d}'
    
    return

def _recv_message(client: socket) -> bytes:
    message = b''

    while buffer := client.recv(1024):
        message += buffer

    return message

from os import walk

class Peer:
    def __init__(self, host: str, port: int, parent: "Peer"=None):
        self.host = host
        self.port = port
        self.parent = parent
    
    def __repr__(self):
        return f'Peer({self.host!r}, {self.port})'
    
    def on_found(self, peer: "Peer"):
        return self
    
    def on_message(self, peer: "Peer", message: bytes):
        return self
    
    def on_info(self, peer: "Peer"):
        return self
    
    def send(self, message: bytes):
        if self.parent is None:
            raise Exception("can't send a message without a unknown parent")
        
        client = socket()

        client.connect((self.host, self.port))
        client.send(Intent.Message.value)
        client.sendall(str(self.parent.port).encode())
        client.sendall(message)

        return self
    
    @property
    def reachable(self):
        client = socket()
        client.settimeout(0.1)

        try:
            client.connect((self.host, self.port))
            client.send(Intent.Check.value)
            client.settimeout(1)
            
            if Intent(client.recv(2)) is not Intent.Check:
                raise Exception

        except:
            return False
        
        return True
    
    @property
    def info(self) -> dict:
        client = socket()

        client.connect((self.host, self.port))
        client.send(Intent.Info.value)

        return json.loads(_recv_message(client))

    def run(self):
        def scan():
            def thread():
                for port in range(8800, 8889):
                    if port == self.port:
                        continue

                    peer = Peer('127.0.0.1', port, self)

                    if peer.reachable:
                        self.on_found(peer)

                for host in each_ipv4():
                    if host == self.host:
                        continue

                    peer = Peer(host, self.port, self)

                    if peer.reachable:
                        self.on_found(peer)
                
                return self
        
            return Thread(target=thread, daemon=True).start()

        server = socket()

        server.bind((self.host, self.port))
        server.listen(1)

        if self.host == '0.0.0.0':
            self.host = HOSTBYNAME

        scan()

        while True:
            client, (host, port) = server.accept()

            intent = Intent(client.recv(2))

            if intent is Intent.Check:
                client.send(Intent.Check.value)
                continue

            peer = Peer(host, int(client.recv(4).decode()), self)

            if intent is Intent.Message:
                self.on_message(peer, _recv_message(client))
            elif intent is Intent.Info:
                client.sendall(json.dumps(self.on_info(peer)).encode())
            
        return