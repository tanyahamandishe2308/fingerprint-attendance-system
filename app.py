from flask import Flask, request, jsonify, render_template
import serial
import adafruit_fingerprint
import time
from datetime import datetime

app = Flask(__name__)

# Initialize the fingerprint sensor
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
fingerprint = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# Temporary in-memory storage
enrollments = []  # Stores enrolled fingerprints with name and surname
attendance_records = []  # Stores attendance logs


def enroll_fingerprint():
    """Enroll a fingerprint."""
    print("Place your finger on the sensor for enrollment.")
    while fingerprint.get_image() != adafruit_fingerprint.OK:
        print("Waiting for finger...")
        time.sleep(1)

    if fingerprint.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Failed to capture the first image.")
        return None

    print("Remove your finger...")
    time.sleep(2)

    print("Place the same finger again.")
    while fingerprint.get_image() != adafruit_fingerprint.OK:
        print("Waiting for finger...")
        time.sleep(1)

    if fingerprint.image_2_tz(2) != adafruit_fingerprint.OK:
        print("Failed to capture the second image.")
        return None

    if fingerprint.create_model() != adafruit_fingerprint.OK:
        print("Failed to create a fingerprint model.")
        return None

    for i in range(1, 128):
        if fingerprint.store_model(i) == adafruit_fingerprint.OK:
            print(f"Fingerprint enrolled successfully at ID {i}")
            return i

    print("No available slots for fingerprint storage.")
    return None


def verify_fingerprint():
    """Verify a fingerprint."""
    print("Place your finger on the sensor for verification.")
    while fingerprint.get_image() != adafruit_fingerprint.OK:
        print("Waiting for finger...")
        time.sleep(1)

    if fingerprint.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Failed to capture fingerprint image.")
        return None

    if fingerprint.finger_search() == adafruit_fingerprint.OK:
        print(f"Fingerprint matched with ID {fingerprint.finger_id}")
        return fingerprint.finger_id
    else:
        print("Fingerprint not recognized.")
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        surname = data.get('surname')

        if not name or not surname:
            return jsonify({"status": "failure", "message": "Name and surname are required."})

        fingerprint_id = enroll_fingerprint()
        if fingerprint_id is None:
            return jsonify({"status": "failure", "message": "Failed to enroll fingerprint. Try again."})

        # Save enrollment in memory
        enrollments.append({
            "fingerprint_id": fingerprint_id,
            "name": name,
            "surname": surname
        })

        return jsonify({"status": "success", "message": f"Fingerprint enrolled successfully with ID {fingerprint_id}."})

    return render_template('enroll.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        fingerprint_id = verify_fingerprint()
        if fingerprint_id is None:
            return jsonify({"status": "failure", "message": "Fingerprint not recognized. Try again."})

        # Find the enrollment with the matching ID
        for enrollment in enrollments:
            if enrollment['fingerprint_id'] == fingerprint_id:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                attendance_records.append({
                    "name": enrollment['name'],
                    "surname": enrollment['surname'],
                    "timestamp": timestamp
                })
                return jsonify({
                    "status": "success",
                    "message": f"Welcome {enrollment['name']} {enrollment['surname']}! Verified at {timestamp}."
                })

        return jsonify({"status": "failure", "message": "Fingerprint not linked to any enrollment."})

    return render_template('verify.html')


@app.route('/attendance')
def attendance():
    return render_template('attendance.html', records=attendance_records)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
