import cv2
import time
import socket
import os
import subprocess

# ================= CONFIG =================
CAM_IP = "10.10.10.81"
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

def check_port(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((CAM_IP, port))
        s.close()
        return True
    except:
        return False

# ============== DATASET MODE ==============
def collect_dataset():
    clear_screen()
    print("=== DATASET COLLECTOR ===\n")

    person_name = input("Person name: ").strip()
    if not person_name:
        print("[ERR] Empty name")
        time.sleep(2)
        return

    save_dir = os.path.join(DATA_PATH, person_name)
    os.makedirs(save_dir, exist_ok=True)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(RTSP_HIGH)
    if not cap.isOpened():
        print("[ERR] Camera access denied!")
        time.sleep(2)
        return

    print("\n[S] save face | [ESC] exit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Stream lost")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        face_crop = None

        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_crop = frame[y:y+h, x:x+w]
        else:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        saved_count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])

        cv2.putText(frame, f"User: {person_name} | Saved: {saved_count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.putText(frame, "Press S to save (ONLY 1 face)",
                    (10, frame.shape[0]-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

        cv2.imshow("Dataset Collector", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key in [ord("s"), ord("S")]:
            if face_crop is not None:
                filename = os.path.join(save_dir, f"{saved_count+1}.jpg")
                cv2.imwrite(filename, face_crop)
                print(f"[SAVED] {filename}")
            else:
                print("[WARN] Need exactly ONE face")

    cap.release()
    cv2.destroyAllWindows()

# ============== LIVE STREAM ==============
def unified_stream():
    clear_screen()
    print("Live Stream\n[F] face detect | [1] HD | [2] LOW | [ESC] exit")

    cap = cv2.VideoCapture(RTSP_HIGH)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    face_on = False
    current = "HD"

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if face_on:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,f"Faces: {len(faces)}",(10,70),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.putText(frame,f"Quality: {current}",(10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)

        cv2.imshow("V380 Live", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key in [ord("f"), ord("F")]:
            face_on = not face_on
        elif key == ord("1"):
            cap.release()
            cap = cv2.VideoCapture(RTSP_HIGH)
            current = "HD"
        elif key == ord("2"):
            cap.release()
            cap = cv2.VideoCapture(RTSP_LOW)
            current = "LOW"

    cap.release()
    cv2.destroyAllWindows()

# ============== LOW DELAY ==============
def low_delay():
    subprocess.call([
        "ffplay", "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-rtsp_transport", "tcp",
        RTSP_HIGH
    ])

# ============== FPS TEST ==============
def benchmark_fps():
    cap = cv2.VideoCapture(RTSP_HIGH)
    start = time.time()
    frames = 0
    while frames < 60:
        ret, _ = cap.read()
        if not ret:
            break
        frames += 1
    cap.release()
    print(f"FPS: {frames / (time.time()-start):.2f}")
    input("Enter to continue")

# ============== PORT CHECK ==============
def check_ports():
    clear_screen()
    for p in [80, 554, 8899]:
        print(f"Port {p}: {'OPEN' if check_port(p) else 'CLOSED'}")
    input("\nEnter to continue")

# ============== MENU ==============
def menu():
    while True:
        clear_screen()
        print("""
===========================
|||  V380 MULTI TOOL    |||
===========================
1 -> Live Stream        |||
2 -> Low Delay          |||
3 -> Benchmark FPS      |||
4 -> Check Ports        |||
5 -> Collect Dataset    |||
0 -> Exit               |||
===========================              
""")
        c = input("> ").strip()
        if c == "1": unified_stream()
        elif c == "2": low_delay()
        elif c == "3": benchmark_fps()
        elif c == "4": check_ports()
        elif c == "5": collect_dataset()
        elif c == "0": break

if __name__ == "__main__":
    menu()

