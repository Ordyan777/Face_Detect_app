import cv2

RTSP_URL = "rtsp://admin:123456@10.10.10.40:554/live/ch0"

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

video = cv2.VideoCapture(RTSP_URL)

while True:
    ret, frame = video.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    print(f"Detected {len(faces)} faces")

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("RTSP", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

