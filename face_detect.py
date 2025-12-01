import sys
import os
import cv2
import face_recognition

def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_faces_image.py <image_path>")
        return

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    # Load image
    image = face_recognition.load_image_file(image_path)

    # Detect faces
    face_locations = face_recognition.face_locations(image)

    # Convert to BGR for OpenCV drawing
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Create output folder
    os.makedirs("output", exist_ok=True)

    # Draw boxes
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)

    # Save file
    filename = os.path.basename(image_path)
    output_path = f"output/{filename.replace('.', '_output.')}"
    cv2.imwrite(output_path, image_bgr)

    # Print result
    print(f"Detected {len(face_locations)} faces")
    print(f"Saved result to: {output_path}")

if __name__ == "__main__":
    main()

