#!/usr/bin/env python3
"""Prove the playit tunnel end to end without the game: listens on 127.0.0.1:25565 (only if nothing else does),
connects to the public address with a real Minecraft handshake, and prints the status reply that came back through the tunnel.
Stop the Minecraft server first, or run it against the live server (then it just prints the server's real status)."""
import socket,threading,time,struct,json,os,sys
here=os.path.dirname(os.path.abspath(__file__)); host,port=open(os.path.join(here,"..","playit","public_address.txt")).read().strip().split(":"); port=int(port)
def varint(n):
    out=b""
    while True:
        b=n&0x7F; n>>=7; out+=bytes([b|0x80]) if n else bytes([b])
        if not n: return out
def packet(pid,payload): body=varint(pid)+payload; return varint(len(body))+body
hs=packet(0, varint(763)+varint(len(host))+host.encode()+struct.pack(">H",port)+varint(1)); req=packet(0,b"")
def fake_server():
    s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try: s.bind(("127.0.0.1",25565))
    except OSError: print("port 25565 busy (real server running): probing the real server"); return
    s.listen(1); s.settimeout(25)
    try:
        c,p=s.accept(); c.settimeout(10); d=c.recv(512); print("tunnel delivered the handshake to 127.0.0.1:25565, hostname present:", host.encode() in d)
        st=json.dumps({"version":{"name":"Little Kettle Valley","protocol":763},"players":{"max":10,"online":0},"description":{"text":"tunnel probe"}}).encode()
        c.sendall(packet(0, varint(len(st))+st)); time.sleep(1); c.close()
    except Exception as e: print("fake server:",e)
    s.close()
th=threading.Thread(target=fake_server); th.start(); time.sleep(0.5)
try:
    c=socket.create_connection((host,port),timeout=15); c.sendall(hs+req); c.settimeout(15); r=c.recv(2048); c.close()
    print("status reply through the tunnel:", r[r.find(b'{'):][:160].decode('utf-8','replace')); ok=True
except Exception as e: print("FAILED:",e); ok=False
th.join(); sys.exit(0 if ok else 1)
