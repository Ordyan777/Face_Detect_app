import cv2
import subprocess
import time
import socket
import os

# --- Функция очистки экрана ---
def clear_screen():
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
    clear_screen()
    print("\n[INFO] Starting 3in1 Mode...")
    print("   [1] -> HD Quality")
    print("   [2] -> Low Quality")
    print("   [F] -> Toggle Face Detect")
    print("   [ESC] -> Quit")

    current_url = RTSP_HIGH
    quality_name = "HD Quality (ch0)"
    face_detect_on = False
    
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(current_url)

    if not cap.isOpened():
        print("[ERR] Cannot connect to camera.")
        time.sleep(2)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Stream lost. Trying to reconnect...")
            cap.release()
            time.sleep(2)
            cap = cv2.VideoCapture(current_url)
            continue

        if face_detect_on:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 70),  
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        color_info = (0, 255, 255) # Yellow
        cv2.putText(frame, f"Quality: {quality_name}", (10, 30),  
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_info, 2)
        
        cv2.putText(frame, "[1] HD [2] Low [F] Face [ESC] Exit ---=== by Catalyst ===---", (10, frame.shape[0] - 20),  
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("---=== V380 Camera ===---", frame)

        key = cv2.waitKey(1)
        if key == 27: # ESC
            break
        elif key == ord('f'):
            face_detect_on = not face_detect_on
            print(f"[CMD] Face Detection: {'ON' if face_detect_on else 'OFF'}")
        elif key == ord('1'):
            if current_url != RTSP_HIGH:
                current_url = RTSP_HIGH
                quality_name = "HD Quality (ch0)"
                cap.release()
                cap = cv2.VideoCapture(current_url)
        elif key == ord('2'):
            if current_url != RTSP_LOW:
                current_url = RTSP_LOW
                quality_name = "Low Quality (ch1)"
                cap.release()
                cap = cv2.VideoCapture(current_url)

    cap.release()
    cv2.destroyAllWindows()

def show_stream_lowdelay():
    clear_screen()
    print("\n[INFO] Low-latency mode on ffmpeg (ffplay)...\n")
    cmd = [
        "ffplay", "-fflags", "nobuffer", "-flags", "low_delay",
        "-framedrop", "-rtsp_transport", "tcp", RTSP_HIGH
    ]
    subprocess.call(cmd)

def benchmark_fps():
    clear_screen()
    cap = cv2.VideoCapture(RTSP_HIGH)
    if not cap.isOpened(): 
        print("[ERR] Camera not available")
        time.sleep(2)
        return
    
    print("\n[INFO] Checking Real FPS (Please wait)...")
    frames = 0
    start = time.time()
    while frames < 60:
        ret, _ = cap.read()
        if not ret: break
        frames += 1
    end = time.time()
    cap.release()
    
    print(f"\n[RESULT] FPS : {frames / (end - start):.2f}")
    input("\nPress Enter to return to menu...") # Пауза, чтобы увидеть результат

def check_ports():
    clear_screen()
    print(f"\n[INFO] Checking Ports for {CAM_IP}...\n")
    for p in [554, 8899, 80]:
        status = "Open" if check_port(p) else "Closed"
        print(f"Port {p}: {status}")
    input("\nPress Enter to return to menu...") # Пауза

def menu():
    while True:
        clear_screen() # Очищаем экран ПЕРЕД отрисовкой меню
        print("""
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
            print("by --- ___---=== Ordyan777 ===---___--- ")
            break
        else:
            print("Invalid choice!")
            time.sleep(1)

if __name__ == "__main__":
    menu()
