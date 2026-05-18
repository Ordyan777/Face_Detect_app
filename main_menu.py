import cv2
import time
import socket
import os
import subprocess
import json
import pickle
import face_recognition
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
from datetime import datetime
import csv

# ================= TERMINAL COLORS =================
class Colors:
    GREEN = '\033[92m'     # Success
    RED = '\033[91m'       # Error
    CYAN = '\033[96m'      # Info
    RESET = '\033[0m'      # Reset color

# ================= CONFIG MANAGER & LOGGING =================
CONFIG_FILE = "camera_config.json"
DATA_PATH = "data/known"
ENCODINGS_FILE = "encodings.pickle"

# --- Настройка логера ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "recognition_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Name", "Status"])

def log_recognition(name):
    """Записывает распознанное лицо в CSV файл"""
    status = "Recognized" if name != "Unknown" else "Unrecognized"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, name, status])
    print(f"{Colors.CYAN}[CSV LOG] Saved: {timestamp} | {name} | {status}{Colors.RESET}")

class ConfigManager:
    @staticmethod
    def load_config():
        default_config = {
            "cameras": [
                {
                    "name": "Main Camera",
                    "ip": "10.10.10.81",
                    "user": "admin",
                    "pass": "123456",
                    "port": 554,
                    "active": True
                }
            ],
            "last_used_camera": 0,
            "auto_detect_usb": True
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        ConfigManager.save_config(default_config)
        return default_config
    
    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    
    @staticmethod
    def add_camera(name, ip, user, passwd, port=554):
        config = ConfigManager.load_config()
        for cam in config["cameras"]:
            if cam["ip"] == ip:
                return False, "Camera with this IP already exists"
        
        new_camera = {
            "name": name,
            "ip": ip,
            "user": user,
            "pass": passwd,
            "port": port,
            "active": True
        }
        
        config["cameras"].append(new_camera)
        ConfigManager.save_config(config)
        return True, "Camera added successfully"
    
    @staticmethod
    def remove_camera(index):
        config = ConfigManager.load_config()
        if 0 <= index < len(config["cameras"]):
            removed_name = config["cameras"][index]["name"]
            del config["cameras"][index]
            if config["last_used_camera"] >= len(config["cameras"]):
                config["last_used_camera"] = max(0, len(config["cameras"]) - 1)
            ConfigManager.save_config(config)
            return True, f"Removed camera: {removed_name}"
        return False, "Invalid camera index"
    
    @staticmethod
    def get_active_camera():
        config = ConfigManager.load_config()
        idx = config["last_used_camera"]
        if 0 <= idx < len(config["cameras"]):
            return config["cameras"][idx]
        return None
    
    @staticmethod
    def set_active_camera(index):
        config = ConfigManager.load_config()
        if 0 <= index < len(config["cameras"]):
            config["last_used_camera"] = index
            ConfigManager.save_config(config)
            return True
        return False

# ================= CAMERA FUNCTIONS =================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def get_rtsp_url(camera_config, channel="ch0"):
    return f"rtsp://{camera_config['user']}:{camera_config['pass']}@{camera_config['ip']}:{camera_config['port']}/live/{channel}"

def test_camera_connection(ip, port=554, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except socket.error:
        return False

def auto_detect_ip():
    return auto_detect_ip_optimized()

def auto_detect_ip_optimized():
    print("[INFO] Scanning for cameras (optimized mode)...")
    current_ip = get_current_ip()
    if current_ip:
        print(f"[INFO] Current IP: {current_ip}")

    networks_to_scan = []
    if current_ip:
        network = get_network_from_ip(current_ip)
        if network:
            networks_to_scan.append(network)

    networks_to_scan.extend([
        "10.10.10.0/24",
        "192.168.1.0/24",
        "192.168.0.0/24",
        "192.168.2.0/24",
        "192.168.178.0/24",
    ])

    networks_to_scan = list(dict.fromkeys(networks_to_scan))
    found_cameras = []

    for network in networks_to_scan:
        print(f"\n[INFO] Scanning {network}...")
        cameras = scan_network_fast(network)
        found_cameras.extend(cameras)
        if cameras:
            print(f"{Colors.GREEN}  ✓ Found {len(cameras)} camera(s) in {network}{Colors.RESET}")
            for ip in cameras:
                print(f"    • {ip}")

    if not found_cameras:
        print(f"\n{Colors.RED}[WARNING] No cameras found in common networks{Colors.RESET}")
        found_cameras = scan_with_multiple_ports()

    return found_cameras

def get_current_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_network_from_ip(ip):
    try:
        return f"{'.'.join(ip.split('.')[:3])}.0/24"
    except Exception:
        return None

def scan_network_fast(network, timeout=0.3, max_workers=50):
    found = []
    hosts = []
    try:
        if '/' in network:
            net = ipaddress.ip_network(network, strict=False)
            hosts = [str(ip) for ip in net.hosts()][:254]
        elif network.endswith('.'):
            hosts = [f"{network}{i}" for i in range(1, 255)]
        else:
            return []
    except ValueError:
        return []

    def check_host(ip):
        if test_camera_connection(ip, 554, timeout):
            return ip
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_host, host) for host in hosts]
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)

    return found

def scan_with_multiple_ports():
    print("[INFO] Scanning common camera ports (multithreaded)...")
    common_ports = [554, 80, 8080, 8899, 8554]
    found = []
    current_ip = get_current_ip()
    
    if not current_ip:
        return found

    base_network = '.'.join(current_ip.split('.')[:3]) + '.'
    
    def check_ip(ip):
        for port in common_ports:
            if test_camera_connection(ip, port, timeout=0.2):
                return ip
        return None

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(1, 255):
            ip = f"{base_network}{i}"
            futures.append(executor.submit(check_ip, ip))
            
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                print(f"{Colors.GREEN}  ✓ Found camera at {result}{Colors.RESET}")

    return list(set(found))

# ================= CAMERA MANAGEMENT MENU =================
def camera_management_menu():
    while True:
        clear_screen()
        config = ConfigManager.load_config()
        
        print("=" * 50)
        print("        CAMERA MANAGEMENT")
        print("=" * 50)
        print("\nConfigured cameras:")
        print("-" * 40)
        
        for idx, cam in enumerate(config["cameras"]):
            active = "✓" if idx == config["last_used_camera"] else " "
            status = f"{Colors.GREEN}ACTIVE{Colors.RESET}" if cam["active"] else f"{Colors.RED}INACTIVE{Colors.RESET}"
            print(f"[{active}] {idx+1}. {cam['name']}")
            print(f"     IP: {cam['ip']}:{cam['port']}")
            print(f"     User: {cam['user']} | Status: {status}\n")
        
        print("-" * 40)
        print("1. Add new camera")
        print("2. Remove camera")
        print("3. Set active camera")
        print("4. Test connection")
        print("5. Auto-detect cameras")
        print("0. Back to main menu")
        print("=" * 50)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1": add_camera_menu()
        elif choice == "2": remove_camera_menu()
        elif choice == "3": set_active_camera_menu()
        elif choice == "4": test_camera_connections()
        elif choice == "5": auto_detect_menu()
        elif choice == "0": break
        else:
            print(f"{Colors.RED}Invalid option!{Colors.RESET}")
            time.sleep(1)

def add_camera_menu():
    clear_screen()
    print("=" * 50)
    print("        ADD NEW CAMERA")
    print("=" * 50)
    
    name = input("Camera name: ").strip()
    ip = input("IP address: ").strip()
    user = input("Username [admin]: ").strip() or "admin"
    passwd = input("Password: ").strip()
    port = input("Port [554]: ").strip() or "554"
    
    try: port = int(port)
    except ValueError: port = 554
    
    print(f"\nTesting connection to {ip}:{port}...")
    if test_camera_connection(ip, port):
        print(f"{Colors.GREEN}✓ Connection successful!{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Connection failed!{Colors.RESET}")
        if input("Add anyway? (y/n): ").lower() != 'y':
            return
    
    success, message = ConfigManager.add_camera(name, ip, user, passwd, port)
    if success:
        print(f"\n{Colors.GREEN}{message}{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{message}{Colors.RESET}")
    
    if success and input("\nTest RTSP stream? (y/n): ").lower() == 'y':
        cam = {"ip": ip, "user": user, "pass": passwd, "port": port}
        rtsp_url = get_rtsp_url(cam)
        test_stream(rtsp_url)
    
    input("\nPress Enter to continue...")

def remove_camera_menu():
    config = ConfigManager.load_config()
    clear_screen()
    print("=" * 50)
    print("        REMOVE CAMERA")
    print("=" * 50)
    
    if not config["cameras"]:
        print(f"{Colors.RED}No cameras configured!{Colors.RESET}")
        time.sleep(1)
        return
    
    for idx, cam in enumerate(config["cameras"]):
        print(f"{idx+1}. {cam['name']} ({cam['ip']})")
    
    try:
        choice = int(input("\nCamera number (0 to cancel): "))
        if choice == 0: return
        if 1 <= choice <= len(config["cameras"]):
            success, message = ConfigManager.remove_camera(choice-1)
            print(f"{Colors.GREEN}{message}{Colors.RESET}" if success else f"{Colors.RED}{message}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Invalid selection!{Colors.RESET}")
    except ValueError:
        print(f"{Colors.RED}Invalid input!{Colors.RESET}")
    time.sleep(1)

def set_active_camera_menu():
    config = ConfigManager.load_config()
    clear_screen()
    
    if not config["cameras"]:
        print(f"{Colors.RED}No cameras configured!{Colors.RESET}")
        time.sleep(1)
        return
    
    for idx, cam in enumerate(config["cameras"]):
        active = f"{Colors.GREEN} [ACTIVE]{Colors.RESET}" if idx == config["last_used_camera"] else ""
        print(f"{idx+1}. {cam['name']} ({cam['ip']}){active}")
    
    try:
        choice = int(input("\nCamera number: "))
        if 1 <= choice <= len(config["cameras"]):
            if ConfigManager.set_active_camera(choice-1):
                print(f"{Colors.GREEN}Camera {choice} set as active!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Invalid selection!{Colors.RESET}")
    except ValueError:
        print(f"{Colors.RED}Invalid input!{Colors.RESET}")
    time.sleep(1)

def test_camera_connections():
    clear_screen()
    config = ConfigManager.load_config()
    for idx, cam in enumerate(config["cameras"]):
        print(f"\nTesting {cam['name']} ({cam['ip']}:{cam['port']})...")
        if test_camera_connection(cam["ip"], cam["port"]):
            print(f"  {Colors.GREEN}✓ TCP connection: OK{Colors.RESET}")
            rtsp_url = get_rtsp_url(cam)
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    print(f"  {Colors.GREEN}✓ RTSP stream: OK{Colors.RESET}")
                else:
                    print(f"  {Colors.RED}✗ RTSP stream: No frames{Colors.RESET}")
            else:
                print(f"  {Colors.RED}✗ RTSP stream: Cannot open{Colors.RESET}")
        else:
            print(f"  {Colors.RED}✗ TCP connection: FAILED{Colors.RESET}")
    input("\nPress Enter to continue...")

def auto_detect_menu():
    clear_screen()
    found = auto_detect_ip()
    if not found:
        print(f"\n{Colors.RED}No cameras found!{Colors.RESET}")
        input("\nPress Enter to continue...")
        return
    
    if input("\nAdd detected cameras? (y/n): ").lower() == 'y':
        config = ConfigManager.load_config()
        for ip in found:
            if not any(cam["ip"] == ip for cam in config["cameras"]):
                ConfigManager.add_camera(f"Auto-detected {ip}", ip, "admin", "123456")
                print(f"{Colors.GREEN}Added {ip}{Colors.RESET}")
    input("\nPress Enter to continue...")

def test_stream(rtsp_url, duration=5):
    cap = cv2.VideoCapture(rtsp_url)
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret: break
        cv2.imshow("Test Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()

# ================= SELECT CAMERA =================
def select_camera():
    clear_screen()
    print("\nSelect Camera Source\n--------------------\n1 -> RTSP Camera\n2 -> USB Camera\n3 -> Camera Management\n0 -> Back\n")
    c = input("> ").strip()

    if c == "1":
        camera = ConfigManager.get_active_camera()
        if camera: return "rtsp", get_rtsp_url(camera)
        print(f"{Colors.RED}[ERR] No RTSP camera configured!{Colors.RESET}")
        time.sleep(2)
        return None, None
    elif c == "2":
        usb = find_usb_camera()
        if usb is None:
            print(f"{Colors.RED}[ERR] USB camera not found{Colors.RESET}")
            time.sleep(2)
            return None, None
        return "usb", usb
    elif c == "3":
        camera_management_menu()
    return None, None

def find_usb_camera():
    for i in range(6):
        if os.path.exists(f"/dev/video{i}"):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cap.release()
                return i
    return None

def check_port(ip, port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except socket.error:
        return False

def collect_dataset():
    cam_type, cam_src = select_camera()
    if cam_src is None: return

    clear_screen()
    name = input("Person name: ").strip()
    if not name: return

    save_dir = os.path.join(DATA_PATH, name)
    os.makedirs(save_dir, exist_ok=True)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(cam_src)
    
    print("\n[S] Save | [ESC] Exit\n")
    while True:
        ret, frame = cap.read()
        if not ret: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
        cv2.putText(frame,f"{name} | Saved: {count}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow("Dataset Collector", frame)

        key = cv2.waitKey(1)
        if key == 27: break
        elif key in [ord("s"), ord("S")] and face_crop is not None:
            cv2.imwrite(os.path.join(save_dir,f"{count+1}.jpg"), face_crop)
            print(f"{Colors.GREEN}[SAVED] {count+1}{Colors.RESET}")

    cap.release()
    cv2.destroyAllWindows()

# ================= THREADED CAMERA CLASS =================
class ThreadedCamera:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            self.ret = False
            self.frame = None
            self.running = False
            return
            
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.ret, self.frame = ret, frame
            else:
                self.ret = False
                time.sleep(0.01)

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.cap.release()

# ================= LIVE RECOGNITION (TASK 6) =================
def unified_stream():

    cam_type, cam_src = select_camera()
    if cam_src is None:
        return

    print(f"{Colors.CYAN}[INFO] Connecting to camera... Please wait.{Colors.RESET}")
    cap = ThreadedCamera(cam_src)
    
    if not getattr(cap, 'running', False) or not cap.cap.isOpened():
        print(f"\n{Colors.RED}[ERROR] Failed to connect to camera! Check network or power.{Colors.RESET}")
        time.sleep(2)
        return

    face_on = False
    recognition_on = False
    quality = "HD"

    known_encodings = []
    known_names = []
    
    try:
        with open(ENCODINGS_FILE, 'rb') as f:
            data = pickle.load(f)
            known_encodings = data["encodings"]
            known_names = data["names"]
        print(f"\n{Colors.GREEN}[SUCCESS] Database loaded: {len(known_names)} profiles.{Colors.RESET}")
    except FileNotFoundError:
        print(f"\n{Colors.RED}[ERROR] File {ENCODINGS_FILE} not found!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}[CRITICAL ERROR] Error reading {ENCODINGS_FILE}: {e}{Colors.RESET}")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    process_this_frame = True
    tolerance_threshold = 0.45  
    print("\n[CONTROLS] 'F' - Face Detection | 'R' - Recognition | 'ESC' - Exit")

    face_locations = []
    face_names = []
    timeout_counter = 0
    last_seen_names = set()
    last_logged_time = {}
    LOG_COOLDOWN = 5
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            timeout_counter += 1
            if timeout_counter > 100: 
                print(f"\n{Colors.RED}[ERROR] Camera signal lost! Returning to main menu...{Colors.RESET}")
                time.sleep(2)
                break
            time.sleep(0.01)
            continue
            
        timeout_counter = 0
        display_frame = frame.copy()

        if recognition_on and known_encodings:
            if process_this_frame:
                small_frame = cv2.resize(display_frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                face_names = []
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance_threshold)
                    name = "Unknown"
                    distance_info = "N/A"
                    
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        min_distance = face_distances[best_match_index]
                        
                        if min_distance < tolerance_threshold:
                            name = known_names[best_match_index]
                        else:
                            name = "Unknown"
                    
                    face_names.append(name)
                    
                    if name != "Unknown":
                        print(f"{Colors.GREEN}[DEBUG] ✅ MATCH | Object: {name} | Distance: {distance_info}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}[DEBUG] ❌ UNKNOWN | Object: {name} | Distance: {distance_info}{Colors.RESET}")

                # --- ЛОГИКА CSV ЛОГИРОВАНИЯ ---
                current_names = set(face_names)
                current_time = time.time()

                for name in current_names:
                    last_time = last_logged_time.get(name, 0)

                    if (name not in last_seen_names) or (current_time - last_time > LOG_COOLDOWN):
                        log_recognition(name)
                        last_logged_time[name] = current_time

            last_seen_names = current_names.copy()
            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4; right *= 4; bottom *= 4; left *= 4
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(display_frame, name, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        elif face_on and not recognition_on:
            gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 0), 2)

        info_line = f"SRC: {cam_type} | DET: {'ON' if face_on else 'OFF'} | REC: {'ON' if recognition_on else 'OFF'}"
        cv2.putText(display_frame, info_line, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("V380 MULTI TOOL - PRO", display_frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key in [ord("f"), ord("F")]:
            face_on = not face_on
        elif key in [ord("r"), ord("R")]:
            recognition_on = not recognition_on

    cap.release()
    cv2.destroyAllWindows()

def low_delay():
    camera = ConfigManager.get_active_camera()
    if camera:
        subprocess.call(["ffplay","-fflags","nobuffer","-flags","low_delay","-rtsp_transport","tcp", get_rtsp_url(camera)])
    else:
        print(f"{Colors.RED}[ERR] No camera configured!{Colors.RESET}")

def benchmark_fps():
    camera = ConfigManager.get_active_camera()
    if not camera: return
    
    cap = cv2.VideoCapture(get_rtsp_url(camera))
    start = time.time()
    frames = 0
    while frames < 60:
        if not cap.read()[0]: break
        frames += 1
    cap.release()
    print(f"FPS: {frames/(time.time()-start):.2f}")
    input("\nPress Enter...")

def check_ports():
    clear_screen()
    camera = ConfigManager.get_active_camera()
    if not camera: return
    ip = camera["ip"]
    for p in [80, 554, 8899]:
        status = f"{Colors.GREEN}OPEN{Colors.RESET}" if check_port(ip, p) else f"{Colors.RED}CLOSED{Colors.RESET}"
        print(f"Port {p}: {status}")
    input("\nPress Enter...")

def generate_encodings_menu():
    clear_screen()
    if not os.path.exists(DATA_PATH):
        print(f"{Colors.RED}[ERR] Dataset path not found!{Colors.RESET}")
        time.sleep(2)
        return
    
    known_encodings = []
    known_names = []
    
    for person_name in os.listdir(DATA_PATH):
        person_dir = os.path.join(DATA_PATH, person_name)
        if not os.path.isdir(person_dir): continue
        
        count = 0
        for img_name in os.listdir(person_dir):
            try:
                image = face_recognition.load_image_file(os.path.join(person_dir, img_name))
                boxes = face_recognition.face_locations(image)
                if len(boxes) == 1:
                    known_encodings.append(face_recognition.face_encodings(image, boxes)[0])
                    known_names.append(person_name)
                    count += 1
            except Exception:
                continue
        if count > 0: print(f"{Colors.GREEN}✓ {person_name}: {count} images{Colors.RESET}")
    
    if known_encodings:
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump({"names": known_names, "encodings": known_encodings}, f)
        print(f"\n{Colors.GREEN}[SUCCESS] Saved {len(known_names)} encodings{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}[ERROR] No valid face images found!{Colors.RESET}")
    input("\nPress Enter...")

def menu():
    while True:
        clear_screen()
        active_camera = ConfigManager.get_active_camera()
        
        print("#" * 50)
        print("    Advanced Control Panel for Cameras    ")
        print("#" * 50)
        if active_camera:
            print(f"Active Camera: {active_camera['name']} ({active_camera['ip']}:{active_camera['port']})")
        else:
            print(f"{Colors.RED}Active Camera: NOT SET{Colors.RESET}")
        print("=" * 50)
        print("1 -> Live Stream + Face Detection (PRO + Anti-Lag)")
        print("2 -> Low Delay Stream (ffplay)")
        print("3 -> Benchmark FPS")
        print("4 -> Check Ports")
        print("5 -> Collect Dataset")
        print("6 -> Camera Management")
        print("7 -> Generate Face Encodings")
        print("0 -> Exit")
        print("=" * 50)
        
        c = input("\n> ").strip()
        if c == "1": unified_stream()
        elif c == "2": low_delay()
        elif c == "3": benchmark_fps()
        elif c == "4": check_ports()
        elif c == "5": collect_dataset()
        elif c == "6": camera_management_menu()
        elif c == "7": generate_encodings_menu()
        elif c == "0": break

if __name__ == "__main__":
    os.makedirs(DATA_PATH, exist_ok=True)
    ConfigManager.load_config()
    menu()
