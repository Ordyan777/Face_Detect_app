import cv2
import face_recognition
import numpy as np

# Твой RTSP-поток
RTSP_URL = "rtsp://admin:123456@10.10.10.40:554/live/ch0"

video = cv2.VideoCapture(RTSP_URL)

if not video.isOpened():
    print("Ошибка: Не удалось открыть RTSP поток")
    exit()

while True:
    ret, frame = video.read()
    if not ret:
        print("Ошибка: кадр не получен")
        break

    # face_recognition работает в RGB
    rgb_frame = frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_frame)

    # выводим количество лиц
    print(f"Detected {len(face_locations)} faces")

    # рисуем боксы
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # показываем окно (если хочешь видеть картинку)
    cv2.imshow("RTSP Face Detection", frame)

    # выход по кнопке q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

