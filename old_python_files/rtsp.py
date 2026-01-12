import socket
import sys

IP = "10.10.10.40"
PORT = 8899

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

try:
    s.connect((IP, PORT))
    print("[+] Connected to port 8899")

    # Стандартный ONVIF-like hello пакет
    packet = bytes.fromhex("02000000100000000000000000000000")

    s.send(packet)
    data = s.recv(4096)

    print("[+] Raw response:")
    print(data.hex())

    if b"rtsp" in data.lower():
        print("\n[+] Found RTSP in response!")
    else:
        print("\n[-] RTSP not visible directly.")
except Exception as e:
    print("Error:", e)
finally:
    s.close()

