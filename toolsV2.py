import cv2
import time
import socket
import os
import subprocess

# ================= CONFIG =================
CAM_IP   = "10.10.10.81"
CAM_USER = "admin"
CAM_PASS = "123456"
CAM_PORT = "554"

DATA_PATH = "data/known"
# ==========================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def get_rtsp(channel="ch0"):
    return f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:{CAM_PORT}/live/{channel}"

RTSP_HIGH = get_rtsp("ch0")
RTSP_LOW  = get_rtsp("ch1")

# ---------- USB CAMERA SEARCH ----------
def find_usb_camera():
    for i in range(6):
        if os.path.exists(f"/dev/video{i}"):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cap.release()
                return i
            cap.release()
    return None

# ---------- CAMERA SELECT ----------
def select_camera():
    clear_screen()
    print("""
Select Camera Source
--------------------
1 -> RTSP Camera
2 -> USB Camera
0 -> Back
""")
    c = input("> ").strip()

    if c == "1":
        return "rtsp", RTSP_HIGH
    elif c == "2":
        usb = find_usb_camera()
        if usb is None:
            print("[ERR] USB camera not found")
            time.sleep(2)
            return None, None
        print(f"[OK] USB camera: /dev/video{usb}")
        time.sleep(1)
        return "usb", usb
    return None, None

# ---------- PORT CHECK ----------
def check_port(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((CAM_IP, port))
        s.close()
        return True
    except:
        return False

# ================= DATASET =================
def collect_dataset():
    cam_type, cam_src = select_camera()
    if cam_src is None:
        return

    clear_screen()
    name = input("Person name: ").strip()
    if not name:
        return

    save_dir = os.path.join(DATA_PATH, name)
    os.makedirs(save_dir, exist_ok=True)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(cam_src)
    if not cap.isOpened():
        print("[ERR] Camera open failed")
        time.sleep(2)
        return

    print("\n[S] save | [ESC] exit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        face_crop = None
        if len(faces) == 1:
            x,y,w,h = faces[0]
            face_crop = frame[y:y+h, x:x+w]
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        else:
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

        count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])

        cv2.putText(frame,f"{name} | saved: {count}",
                    (10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.imshow("Dataset Collector", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key in [ord("s"), ord("S")] and face_crop is not None:
            cv2.imwrite(os.path.join(save_dir,f"{count+1}.jpg"), face_crop)
            print("[SAVED]", count+1)

    cap.release()
    cv2.destroyAllWindows()

# ================= LIVE STREAM =================
def unified_stream():
    cam_type, cam_src = select_camera()
    if cam_src is None:
        return

    cap = cv2.VideoCapture(cam_src)
    face_on = False
    quality = "HD"

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if face_on:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,1.2,5)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,f"Faces: {len(faces)}",(10,70),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.putText(frame,f"Source: {cam_type} | {quality}",
                    (10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)

        cv2.imshow("V380 MULTI TOOL", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key in [ord("f"), ord("F")]:
            face_on = not face_on
        elif key == ord("1") and cam_type == "rtsp":
            cap.release()
            cap = cv2.VideoCapture(RTSP_HIGH)
            quality = "HD"
        elif key == ord("2") and cam_type == "rtsp":
            cap.release()
            cap = cv2.VideoCapture(RTSP_LOW)
            quality = "LOW"

    cap.release()
    cv2.destroyAllWindows()

# ================= LOW DELAY =================
def low_delay():
    subprocess.call([
        "ffplay","-fflags","nobuffer",
        "-flags","low_delay",
        "-rtsp_transport","tcp",
        RTSP_HIGH
    ])

# ================= FPS TEST =================
def benchmark_fps():
    cap = cv2.VideoCapture(RTSP_HIGH)
    start = time.time()
    frames = 0
    while frames < 60:
        if not cap.read()[0]:
            break
        frames += 1
    cap.release()
    print("FPS:", frames/(time.time()-start))
    input("Enter...")

# ================= PORTS =================
def check_ports():
    clear_screen()
    for p in [80,554,8899]:
        print(f"Port {p}: {'OPEN' if check_port(p) else 'CLOSED'}")
    input("\nEnter...")

# ================= MENU =================
def menu():
    while True:
        clear_screen()
        print("""
==============================
 V380 / USB MULTI TOOL
==============================
1 -> Live Stream + Face
2 -> Low Delay (ffplay)
3 -> Benchmark FPS
4 -> Check Ports
5 -> Collect Dataset
0 -> Exit
==============================
""")
        c = input("> ")
        if c == "1": unified_stream()
        elif c == "2": low_delay()
        elif c == "3": benchmark_fps()
        elif c == "4": check_ports()
        elif c == "5": collect_dataset()
        elif c == "0": break

if __name__ == "__main__":
    menu()

