import cv2
import os
import time

# =============================
# CONFIG
# =============================
CAM_IP   = "10.10.10.37"
CAM_USER = "admin"
CAM_PASS = "123456"
CAM_PORT = "554"

RTSP_URL = f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:{CAM_PORT}/live/ch0"

BASE_DIR = "data/known"

# =============================
# ASK PERSON NAME
# =============================
def ask_person_name():
    name = input("Enter person name: ").strip()
    while not name:
        name = input("Name cannot be empty. Enter person name: ").strip()
    return name

# =============================
# MAIN
# =============================
def main():
    person_name = ask_person_name()
    save_dir = os.path.join(BASE_DIR, person_name)
    os.makedirs(save_dir, exist_ok=True)

    saved_count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return

    face_detect = True
    last_faces = []

    print("[INFO] Press F = toggle face detect | S = save face | ESC = exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame lost")
            time.sleep(1)
            continue

        display = frame.copy()
        faces = []

        if face_detect:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            last_faces = faces

            for (x, y, w, h) in faces:
                cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # ===== Overlay =====
        cv2.putText(display, f"Person: {person_name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        cv2.putText(display, f"Saved: {saved_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        cv2.putText(display, "[S] Save face | [F] Face detect | ESC Exit",
                    (10, display.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

        cv2.imshow("Face Collector", display)

        key = cv2.waitKey(1) & 0xFF

        # ===== Exit =====
        if key == 27:
            break

        # ===== Toggle face detect =====
        if key == ord('f'):
            face_detect = not face_detect
            print(f"[INFO] Face detect: {'ON' if face_detect else 'OFF'}")

        # ===== Save face =====
        if key == ord('s'):
            if len(last_faces) != 1:
                print("[WARN] Need exactly ONE face to save")
                continue

            (x, y, w, h) = last_faces[0]
            face_crop = frame[y:y+h, x:x+w]

            if face_crop.size == 0:
                print("[WARN] Invalid crop")
                continue

            filename = f"{person_name}_{saved_count+1}.jpg"
            filepath = os.path.join(save_dir, filename)

            cv2.imwrite(filepath, face_crop)
            saved_count += 1

            print(f"[SAVED] {filepath}")

    cap.release()
    cv2.destroyAllWindows()

# =============================
if __name__ == "__main__":
    main()

