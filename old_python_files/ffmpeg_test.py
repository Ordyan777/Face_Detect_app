import subprocess
import cv2
import numpy as np

RTSP_URL = "rtsp://admin:123456@10.10.10.40:554/live/ch0"

ffmpeg_cmd = [
    "ffmpeg",
    "-rtsp_transport", "tcp",
    "-i", RTSP_URL,
    "-f", "image2pipe",
    "-pix_fmt", "bgr24",
    "-vcodec", "rawvideo",
    "-"
]

pipe = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**8)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

while True:
    raw_image = pipe.stdout.read(1280 * 720 * 3)   # размер твоего видео
    if len(raw_image) != 1280 * 720 * 3:
        continue

    frame = np.frombuffer(raw_image, dtype=np.uint8).reshape((720, 1280, 3))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    print(f"Detected {len(faces)} faces")

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("RTSP", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

pipe.terminate()
cv2.destroyAllWindows()

