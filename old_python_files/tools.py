import cv2
import subprocess
import time
import socket
import os

os.system('cls' if os.name == 'nt' else 'clear')

# --- Configuration ---
CAM_IP = "10.10.10.37"
CAM_USER = "admin"
CAM_PASS = "123456"
CAM_PORT = "554"

# --- RTSP LINK ---
def get_rtsp_url(channel="ch0"):
    # ch0 = High, ch1 = Low
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

# --- New Menu & AllInOne ---
def unified_stream():
    print("\n[INFO] Starting 3in1 Mode...")
    print("   [1] -> HD Quality")
    print("   [2] -> Low Quality")
    print("   [F] -> Toggle Face Detect")
    print("   [ESC] -> Quit")

    # Basic Settings
    current_url = RTSP_HIGH
    quality_name = "HD Quality (ch0)"
    face_detect_on = False
    
    # Loading Cascade Face in one more
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(current_url)

    if not cap.isOpened():
        print("[ERR] Cannot connect to camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Stream lost. Trying to reconnect...")
            cap.release()
            time.sleep(2)
            cap = cv2.VideoCapture(current_url)
            continue

        # --- Logic Face Search ---
        if face_detect_on:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Writing Finding Faces...
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # --- iNfo on Monitor ---
        # Show Real Quality
        color_info = (0, 255, 255) # yEllow
        cv2.putText(frame, f"Quality: {quality_name}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_info, 2)
        
        # Hint in Monitor
        cv2.putText(frame, "[1] HD [2] Low [F] Face [ESC] Exit ---=== by Catalyst ===---", (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("---=== V380 Camera ===---", frame)

        # --- key ---
        key = cv2.waitKey(1)

        if key == 27: # ESC
            break
        
        elif key == ord('f'): # key 'f' - on/off face
            face_detect_on = not face_detect_on
           state = "ON" if face_detect_on else "OFF"
            print(f"[CMD] Face Detection: {state}")

        elif key == ord('1'): # key '1' switch on High
            if current_url != RTSP_HIGH:
                os.system('cls' if os.name == 'nt' else 'clear')
                current_url = RTSP_HIGH
                quality_name = "HD Quality (ch0)"
                cap.release()
                cap = cv2.VideoCapture(current_url)

        elif key == ord('2'): # key '2' switch on Low
            if current_url != RTSP_LOW:
                os.system('cls' if os.name == 'nt' else 'clear')
                current_url = RTSP_LOW
                quality_name = "Low Quality (ch1)"
                cap.release()
                cap = cv2.VideoCapture(current_url)

    cap.release()
    cv2.destroyAllWindows()


def show_stream_lowdelay():
    # FFMPEG WORKING IN a separate window
    print("\n[INFO] Low-latency mode on ffmpeg…\n")
    cmd = [
        "ffplay", "-fflags", "nobuffer", "-flags", "low_delay",
        "-framedrop", "-rtsp_transport", "tcp", RTSP_HIGH
    ]
    subprocess.call(cmd)

def benchmark_fps():
    cap = cv2.VideoCapture(RTSP_HIGH)
    if not cap.isOpened(): return
    print("\n[INFO] Checking Real FPS (Wait ~2 sec)...\n")
    frames = 0
    start = time.time()
    while frames < 60:
        ret, _ = cap.read()
        if not ret: break
        frames += 1
    end = time.time()
    cap.release()
    print(f"\n[RESULT] FPS : {frames / (end - start):.2f}\n")
    os.system('cls' if os.name == 'nt' else 'clear')


def check_ports():
    print("\n[INFO] Checking Ports...")
    for p in [554, 8899, 80]:
        time.sleep(2)
        print(f"Port {p}: {'Open' if check_port(p) else 'Closed'}")
def menu():
    while True:
        # ... (menu without changing)
        print(
        """ 
=============================
      v380 PaneL MoDe
=============================
1 -> 3in1 MODE (Stream + Face + HD/Low Quality)
2 -> Low Delay (FFmpeg external)
3 -> Benchmark FPS
4 -> Check Ports
0 -> Exit
""")
        choice = input("> ")

        if choice == "1":
            unified_stream()
        elif choice == "2":
            show_stream_lowdelay()
        elif choice == "3":
            benchmark_fps()
        elif choice == "4":
            check_ports()
        elif choice == "0":
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    menu()
