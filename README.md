# Lion
Uma biblioteca simples para comunicação p2p na rede local

## Instalar
```bash
$ pip install -e lion
```

## Exemplo
```python
from random import randint
from peer import Peer

class HelloPeer(Peer):
    def on_found(self, peer: "Peer"):
        print('i am', self)
        print('found', peer)

        peer.send(b'hello peer!')
    
    def on_message(self, peer: "Peer", message: bytes):
        print('received', message, 'from', peer)


if __name__ == '__main__':
    HelloPeer('0.0.0.0', randint(8800, 8888)).run()
```

---
2022 - Marcel Guinhos de Menezes