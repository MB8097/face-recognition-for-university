import cv2
import face_recognition
import os
from datetime import datetime, timedelta
import sqlite3
import numpy as np
import winsound

# Constants
SAVE_INTERVAL = timedelta(seconds=5)
DATABASE = "access_log.db"

# Utility functions
def image_to_blob(image):
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

def blob_to_image(blob):
    np_array = np.frombuffer(blob, np.uint8)
    return cv2.imdecode(np_array, cv2.IMREAD_COLOR)

def save_to_database(table, name, timestamp, image):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table} (name, timestamp, image) VALUES (?, ?, ?)",
                   (name, timestamp, image_to_blob(image)))
    conn.commit()
    conn.close()
    print(f"Logged {name} at {timestamp} in {table}.")

def is_duplicate_entry(table, name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE name = ?", (name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Initialize database
def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unauthorized_logs (
            id INTEGER PRIMARY KEY,
            name TEXT,
            timestamp TEXT,
            image BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorized_logs (
            id INTEGER PRIMARY KEY,
            name TEXT,
            timestamp TEXT,
            image BLOB
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# Load known faces
known_face_encodings = []
known_face_names = []
last_save_times = {}  # Track save times for each person

def load_known_faces(directory="Known_faces"):
    global known_face_encodings, known_face_names
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    for filename in os.listdir(directory):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            filepath = os.path.join(directory, filename)
            try:
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(os.path.splitext(filename)[0])
                    print(f"Loaded face for: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

load_known_faces()

# Face detection and logging
def log_authorized_with_image(frame, name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_to_database("authorized_logs", name, timestamp, frame)

def log_unauthorized_with_image(frame, name="Unknown"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_to_database("unauthorized_logs", name, timestamp, frame)

# Capture video and recognize faces
def capture_and_display(camera_id=0, process_every_n=5):
    global last_save_times
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(f"Error: Camera {camera_id} could not be opened.")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Frame not read from camera {camera_id}")
            break

        frame_count += 1
        if frame_count % process_every_n != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = face_distances.argmin() if matches else -1

            if best_match_index != -1 and matches[best_match_index]:
                name = known_face_names[best_match_index]
                color = (0, 255, 0)
                label = f"{name} (Recognized)"
                current_time = datetime.now()

                # Check last save time for the person
                if name not in last_save_times or current_time - last_save_times[name] > SAVE_INTERVAL:
                    last_save_times[name] = current_time
                    authorized_frame = frame[top:bottom, left:right]
                    log_authorized_with_image(authorized_frame, name)
                    try:
                        winsound.Beep(800, 300)  # Green beep for authorized
                    except Exception as e:
                        print(f"Error playing tick sound: {e}")
            else:
                name = "Unknown"
                color = (0, 0, 255)
                label = "Unauthorized"
                current_time = datetime.now()

                # Log unauthorized entries
                if name not in last_save_times or current_time - last_save_times.get(name, datetime.min) > SAVE_INTERVAL:
                    last_save_times[name] = current_time
                    unauthorized_frame = frame[top:bottom, left:right]
                    log_unauthorized_with_image(unauthorized_frame, name)
                    try:
                        winsound.Beep(1000, 500)  # Red beep for unauthorized
                    except Exception as e:
                        print(f"Error playing beep sound: {e}")

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_display()
