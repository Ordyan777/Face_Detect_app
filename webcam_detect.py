import cv2

# Օգտագործեք ձեր ճիշտ RTSP հասցեն
rtsp_url = 'rtsp://admin:123456@10.10.10.40:554/live/ch0'

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Not Working : Try Again !")
    exit()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Stream ended or error occurred.")
        break
        
    # Հենց այստեղ է, որ դուք կկատարեք ձեր AI մշակումը
    # Օրինակ: Object Detection, Face Recognition
    
    cv2.imshow('For face detect app/script', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
