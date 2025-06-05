from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # السماح بطلبات CORS

# مسار ملف CSV
CSV_FILE = "confirmed_reservations.csv"

# التأكد من وجود ملف CSV وإضافة رؤوس الأعمدة
if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    df = pd.DataFrame(columns=["Reservation ID", "Stadium Name", "Day", "Date", "Time", "Additional Time", "Mobile Number", "Payment Method", "Payment Name", "Payment Image Path"])
    df.to_csv(CSV_FILE, index=False)

@app.route("/confirm", methods=["POST"])
def confirm_reservation():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    new_reservation = {
        "Reservation ID": data.get("reservationId"),
        "Stadium Name": data.get("stadiumName"),
        "Day": data.get("reservationDay"),
        "Date": data.get("reservationDate"),
        "Time": data.get("reservationTime"),
        "Additional Time": data.get("additionalTime"),
        "Mobile Number": data.get("mobileNumber"),
        "Payment Method": data.get("paymentMethod"),
        "Payment Name": data.get("paymentName"),
        "Payment Image Path": ""
    }
    
    # تحميل البيانات الحالية
    df = pd.read_csv(CSV_FILE)

    # Save the payment image if provided
    payment_image_data = data.get("paymentImage")
    if payment_image_data:
        import base64
        import re
        from datetime import datetime

        # Extract base64 string from data URL
        img_str = re.sub('^data:image/.+;base64,', '', payment_image_data)
        img_data = base64.b64decode(img_str)

        # Create images directory if not exists
        images_dir = "payment_images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # Save image with unique name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_filename = f"{images_dir}/payment_{timestamp}.png"
        with open(image_filename, "wb") as f:
            f.write(img_data)

        new_reservation["Payment Image Path"] = image_filename

    # إضافة الحجز الجديد باستخدام concat
    df = pd.concat([df, pd.DataFrame([new_reservation])], ignore_index=True)

    # حفظ الملف
    df.to_csv(CSV_FILE, index=False)

    return jsonify({"message": "Reservation confirmed and saved!"}), 201

from flask import send_from_directory

@app.route("/schedule", methods=["GET"])
def get_schedule():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "Schedule file not found"}), 404
    df = pd.read_csv(CSV_FILE)
    # Convert dataframe to JSON
    schedule_json = df.to_dict(orient="records")
    return jsonify(schedule_json), 200

import io
from flask import request
import pandas as pd

@app.route("/upload_schedule", methods=["POST"])
def upload_schedule():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        if file.filename.endswith('.csv'):
            # Save CSV file directly
            file.save(CSV_FILE)
        elif file.filename.endswith(('.xls', '.xlsx')):
            # Convert Excel to CSV
            df = pd.read_excel(file)
            df.to_csv(CSV_FILE, index=False)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Schedule file uploaded successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
