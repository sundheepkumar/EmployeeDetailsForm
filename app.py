from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# File paths
EMPLOYEE_DATA_FILE = "Employee_data.xlsx"
DOMESTIC_LOC_FILE = "domestic_locations.xlsx"
INTERNATIONAL_LOC_FILE = "international_locations.xlsx"
OUTPUT_FILE = "submissions.xlsx"

# Route: Render the main form
@app.route('/')
def index():
    return render_template("index.html")

# Route: Get employee details by ID
@app.route('/get_employee', methods=['POST'])
def get_employee():
    try:
        emp_id = int(request.json['emp_id'])
        df = pd.read_excel(EMPLOYEE_DATA_FILE, engine='openpyxl')
        emp = df[df['ID'] == emp_id]

        if not emp.empty:
            emp = emp.iloc[0]
            return jsonify({"name": emp["Name"], "department": emp["Department"]})
        return jsonify({"error": "Employee not found"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Route: Load location options from Excel
@app.route('/get_locations', methods=['GET'])
def get_locations():
    try:
        # Load the domestic and international locations from the respective Excel files
        domestic_df = pd.read_excel(DOMESTIC_LOC_FILE, engine='openpyxl')
        international_df = pd.read_excel(INTERNATIONAL_LOC_FILE, engine='openpyxl')

        # Clean the data by removing NaN or empty values from the lists
        domestic_locations = {key: [value for value in values if pd.notna(value) and value.strip()]
                              for key, values in domestic_df.to_dict(orient='list').items()}
        international_locations = {key: [value for value in values if pd.notna(value) and value.strip()]
                                   for key, values in international_df.to_dict(orient='list').items()}

        return jsonify({
            "domestic": domestic_locations,
            "international": international_locations
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# Route: Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        entry = {
            "ID": data.get("emp_id"),
            "Name": data.get("name"),
            "Department": data.get("department"),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Store location preferences from loc1_1 to int3_3
        for section in ['loc', 'int']:  # 'loc' = domestic, 'int' = international
            for i in range(1, 4):  # Place 1 to 3
                for j in range(1, 4):  # Option 1 to 3
                    key = f"{section}{i}_{j}"
                    entry[key] = data.get(key, "")

        new_df = pd.DataFrame([entry])

        if os.path.exists(OUTPUT_FILE):
            existing_df = pd.read_excel(OUTPUT_FILE, engine='openpyxl')
            final_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            final_df = new_df

        final_df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
        return jsonify({"message": "Preferences saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Route: Download the final submission file
@app.route('/download-submissions')
def download_submissions():
    if os.path.exists(OUTPUT_FILE):
        return send_file(OUTPUT_FILE, as_attachment=True)
    return "Submission file not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
