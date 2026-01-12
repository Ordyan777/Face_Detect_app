import cv2
import subprocess
import time
import socket
import os

RTSP_URL = "rtsp://admin:123456@10.10.10.37:554/live/ch0"
CAM_IP = "10.10.10.37"


def check_port(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((CAM_IP, port))
        s.close()
        return True
    except:
        return False


def show_stream():
    print("\n[INFO] Opening Stream , for exit press ctrl+c.. \n")
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print("[ERR] RTSP Not Working , try Login and password.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Camera Frezzing , FPS Dosen't show.")
            os.system('cls' if os.name == 'nt' else 'clear')

            break

        cv2.imshow("V380 Panel Mode", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def show_stream_lowdelay():
    print("\n[INFO] Low-latency mode on ffmpeg…\n")

    cmd = [
        "ffplay",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-framedrop",
        "-rtsp_transport", "tcp",
        RTSP_URL
    ]

    subprocess.call(cmd)


def face_detection():
    print("\n[INFO] Detecting Faces..…\n")

    cap = cv2.VideoCapture(RTSP_URL)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("[ERR] Camera has been freezed , please Restart tool")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) > 0:
            print(f"[FOUND] Detected Face : {len(faces)}")

        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

        cv2.imshow("FACE DETECT", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def benchmark_fps():
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print("[ERR] Camera Not Working.")
        return

    print("\n[INFO] Checking Real FPS…\n")

    frames = 0
    start = time.time()

    while frames < 120:
        ret, frame = cap.read()
        if not ret:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("[ERR] Camera killed . Have a 0 FPS.")
            break
        frames += 1

    end = time.time()
    cap.release()

    fps = frames / (end - start)
    print(f"\n[RESULT] Real FPS : {fps:.2f}\n")


def check_ports():
    print("\n[INFO] Checking Open ports:")
    for p in [554, 8899, 80, 5000, 1935]:
        status = "Open" if check_port(p) else "Closed"
        print(f"Port {p}: {status}")
    print("")


def menu():
    while True:
        print("""
=============================
v380 Panel Mode - Ordyan777 -
=============================
1) Open RTSP mode
2) RTSP on Low Mode(ffmpeg)
3) Detect Face
4) Test Real FPS
5) Check Ports
0) Exit ( or ctrl+x )
""")

        choice = input("> ")

        if choice == "1":
            show_stream()
        elif choice == "2":
            show_stream_lowdelay()
        elif choice == "3":
            face_detection()
        elif choice == "4":
            benchmark_fps()
        elif choice == "5":
            check_ports()
        elif choice == "0":
            break
        else:
            print("404.. Error , try ALT + F4 ...\n")
            os.system('cls' if os.name == 'nt' else 'clear')


menu()

