from random import randint
from lion.peer import Peer

class HelloPeer(Peer):
    def on_found(self, peer: "Peer"):
        print('i am', self)
        print('found', peer)

        peer.send(b'hello peer!')

        print(peer.info)
    
    def on_message(self, peer: "Peer", message: bytes):
        print('received', message, 'from', peer)
    
    def on_info(self, peer: "Peer"):
        return {"hi": "sup"}


if __name__ == '__main__':
    HelloPeer('0.0.0.0', randint(8800, 8888)).run()