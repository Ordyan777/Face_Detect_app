import cv2
import subprocess
import time
import socket
import os

# --- КОНФИГУРАЦИЯ ---
CAM_IP = "10.10.10.37"
CAM_USER = "admin"
CAM_PASS = "123456"
CAM_PORT = "554"

# Функция для генерации ссылки (ch0 - High, ch1 - Low)
def get_rtsp_url(channel="ch0"):
    return f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:{CAM_PORT}/live/{channel}"

# Ссылка по умолчанию (высокое качество)
RTSP_URL = get_rtsp_url("ch0")


def check_port(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((CAM_IP, port))
        s.close()
        return True
    except:
        return False


def show_stream(custom_url=None):
    # Если передали кастомную ссылку (для выбора качества), используем её
    url_to_open = custom_url if custom_url else RTSP_URL
    
    print(f"\n[INFO] Opening Stream ({url_to_open})...")
    print("[INFO] Press 'ESC' to exit stream.\n")
    
    cap = cv2.VideoCapture(url_to_open)

    if not cap.isOpened():
        print("[ERR] RTSP Not Working or Wrong Credentials.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Camera Freezing or Signal Lost.")
            break

        cv2.imshow("V380 Panel Mode", frame)

        # Выход на ESC (код 27)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# --- НОВАЯ ФУНКЦИЯ: ВЫБОР КАЧЕСТВА ---
def stream_with_quality():
    print("\n[INFO] Select Stream Quality:")
    print("1) High Quality (Main Stream - ch0) - Лучшая картинка")
    print("2) Low Quality (Sub Stream - ch1) - Меньше задержка, хуже качество")
    
    q_choice = input("Select quality > ")
    
    if q_choice == "1":
        new_url = get_rtsp_url("ch0")
        show_stream(new_url)
    elif q_choice == "2":
        new_url = get_rtsp_url("ch1")
        show_stream(new_url)
    else:
        print("[ERR] Wrong choice, opening default (High)...")
        show_stream(RTSP_URL)


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
    print("\n[INFO] Detecting Faces...\n")
    cap = cv2.VideoCapture(RTSP_URL)
    
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Stream Lost.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) > 0:
            # Можно раскомментировать, чтобы не спамило в консоль
            # print(f"[FOUND] Detected Face : {len(faces)}")
            pass

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

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

    print("\n[INFO] Checking Real FPS (Wait ~5 sec)...\n")
    frames = 0
    start = time.time()

    while frames < 120:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Camera killed. 0 FPS.")
            break
        frames += 1

    end = time.time()
    cap.release()

    total_time = end - start
    if total_time > 0:
        fps = frames / total_time
        print(f"\n[RESULT] Real FPS : {fps:.2f}\n")
    else:
        print("\n[ERR] Could not calculate FPS.\n")


def check_ports():
    print("\n[INFO] Checking Open ports:")
    # Добавил 554 (RTSP) в список проверки явно
    port_list = [554, 8899, 80, 5000, 1935]
    for p in port_list:
        status = "Open" if check_port(p) else "Closed"
        print(f"Port {p}: {status}")
    print("")


def menu():
    while True:
        print("""
=============================
v380 Panel Mode - Ordyan777 -
=============================
1) Open RTSP mode (Default High)
2) RTSP on Low Delay Mode (ffmpeg)
3) Detect Face
4) Test Real FPS
5) Check Ports
6) Select Quality & Stream [NEW]
0) Exit
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
        elif choice == "6":
            stream_with_quality()
        elif choice == "0":
            break
        else:
            print("Unknown command...")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    menu()
