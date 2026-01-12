import cv2
import subprocess
import time
import socket
import os

# --- Configuration ---
CAM_IP = "10.10.10.81"
CAM_USER = "admin"
CAM_PASS = "123456"
CAM_PORT = "554"
DATA_PATH = "data/known"

# --- Функция очистки экрана ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- RTSP LINK ---
def get_rtsp_url(channel="ch0"):
    return f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:{CAM_PORT}/live/{channel}"

RTSP_HIGH = get_rtsp_url("ch0")
RTSP_LOW  = get_rtsp_url("ch1")

def check_port(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((CAM_IP, port))
        s.close()
        return True
    except:
        return False

# --- 5) Функция Сбора Датасета (Для Диплома) ---
def collect_dataset():
    clear_screen()
    print("=== Analyse Face  ===")
    person_name = input("Write name : ").strip()
    
    if not person_name:
        print("[ERR] ERROR:")
        time.sleep(2)
        return

    
    save_dir = os.path.join(DATA_PATH, person_name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"[INFO] created folder: {save_dir}")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(RTSP_HIGH)
    
    img_count = 0
    print(f"\n[START] Collect face : {person_name}")
    print("  [S] -> Save Face screen")
    print("  [ESC] -> exit ")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Camera not working...")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) == 1:
        (x, y, w, h) = faces[0]
        face_crop = frame[y:y+h, x:x+w]
            else:
        face_crop = None


        # Инфо на экране
        cv2.putText(frame, f"User: {person_name} | Saved: {img_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'S' to Crop & Save", (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow(" Pre-Beta ", frame)

        key = cv2.waitKey(1)
        if key == 27: # ESC
            break
        elif key == ord('s') or key == ord('S'):
            if face_crop is not None:
                img_count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
                file_path = os.path.join(save_dir, f"{img_count}.jpg")
                cv2.imwrite(file_path, face_crop)
                print(f"[SAVED] {file_path}")
            else:
                print("[WARN] No face detected or multiple faces in frame !")

    cap.release()
    cv2.destroyAllWindows()

# --- 1) New Menu & AllInOne ---
def unified_stream():
    clear_screen()
    print("\n[INFO] Starting 3in1 Mode...")
    print("   [1] -> HD Quality")
    print("   [2] -> Low Quality")
    print("   [F] -> Toggle Face Detect")
    print("   [ESC] -> Quit")

    current_url = RTSP_HIGH
    quality_name = "HD Quality (ch0)"
    face_detect_on = False
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(current_url)

    if not cap.isOpened():
        print("[ERR] Cannot connect to camera.")
        time.sleep(2)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            time.sleep(2)
            cap = cv2.VideoCapture(current_url)
            continue

        if face_detect_on:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"Quality: {quality_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "[1] HD [2] Low [F] Face [ESC] Exit ---=== by Catalyst ===---", (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("---=== V380 Camera ===---", frame)

        key = cv2.waitKey(1)
        if key == 27: break
        elif key == ord('f'): face_detect_on = not face_detect_on
        elif key == ord('1'):
            if current_url != RTSP_HIGH:
                current_url, quality_name = RTSP_HIGH, "HD Quality (ch0)"
                cap.release(); cap = cv2.VideoCapture(current_url)
        elif key == ord('2'):
            if current_url != RTSP_LOW:
                current_url, quality_name = RTSP_LOW, "Low Quality (ch1)"
                cap.release(); cap = cv2.VideoCapture(current_url)

    cap.release()
    cv2.destroyAllWindows()

def show_stream_lowdelay():
    clear_screen()
    print("\n[INFO] Low-latency mode on ffmpeg (ffplay)...\n")
    cmd = ["ffplay", "-fflags", "nobuffer", "-flags", "low_delay", "-framedrop", "-rtsp_transport", "tcp", RTSP_HIGH]
    subprocess.call(cmd)

def benchmark_fps():
    clear_screen()
    cap = cv2.VideoCapture(RTSP_HIGH)
    if not cap.isOpened(): return
    print("\n[INFO] Checking Real FPS (Please wait)...")
    frames, start = 0, time.time()
    while frames < 60:
        ret, _ = cap.read()
        if not ret: break
        frames += 1
    cap.release()
    print(f"\n[RESULT] FPS : {frames / (time.time() - start):.2f}")
    input("\nPress Enter to return to menu...")

def check_ports():
    clear_screen()
    except Exception:
    print(f"\n[INFO] Checking Ports for {CAM_IP}...\n")
    for p in [554, 8899, 80]:
        print(f"Port {p}: {'Open' if check_port(p) else 'Closed'}")
    input("\nPress Enter to return to menu...")

def menu():
    while True:
        clear_screen()
        print("""
=============================
      v380 PaneL MoDe
=============================
1 -> 3in1 MODE (Stream + Face + HD/Low Quality)
2 -> Low Delay (FFmpeg external)
3 -> Benchmark FPS
4 -> Check Ports
5 -> Dataset Collector ( Pre-Beta )  [NEW]
0 -> Exit
""")
        choice = input("> ")

        if choice == "1": unified_stream()
        elif choice == "2": show_stream_lowdelay()
        elif choice == "3": benchmark_fps()
        elif choice == "4": check_ports()
        elif choice == "5": collect_dataset()
        elif choice == "0":
            print("ExitinG . . . .  ")
            break
        else:
            print("404 . . . .  NoT FounD . . . . .  "); time.sleep(1)

if __name__ == "__main__":
    menu()
