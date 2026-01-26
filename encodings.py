import face_recognition
import os
import pickle

DATASET_PATH = "data/known"
OUTPUT_FILE = "encodings.pickle"

known_encodings = []
known_names = []

total_images = 0
total_encodings = 0

print("[INFO] Starting encoding generation...\n")

for person_name in os.listdir(DATASET_PATH):
    person_dir = os.path.join(DATASET_PATH, person_name)

    if not os.path.isdir(person_dir):
        continue

    person_count = 0

    for img_name in os.listdir(person_dir):
        img_path = os.path.join(person_dir, img_name)

        try:
            image = face_recognition.load_image_file(img_path)
            boxes = face_recognition.face_locations(image)

            if len(boxes) == 0:
                print(f"[WARNING] Skipped {img_name} (no face found)")
                continue

            if len(boxes) > 1:
                print(f"[WARNING] Skipped {img_name} (multiple faces)")
                continue

            encoding = face_recognition.face_encodings(image, boxes)[0]

            known_encodings.append(encoding)
            known_names.append(person_name)

            person_count += 1
            total_encodings += 1

        except Exception as e:
            print(f"[ERROR] Failed {img_name}: {e}")

        total_images += 1

    print(f"[INFO] {person_name} → {person_count} images processed")

data = {
    "names": known_names,
    "encodings": known_encodings
}

with open(OUTPUT_FILE, "wb") as f:
    pickle.dump(data, f)

print("\n==============================")
print(f"[INFO] Total images scanned: {total_images}")
print(f"[INFO] Total encodings created: {total_encodings}")
print(f"[INFO] Saved to: {OUTPUT_FILE}")
print("==============================")

