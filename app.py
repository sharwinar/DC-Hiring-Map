import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Published CSV URL of your Google Sheet
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQjE0hdLpES-YfU7lX_bkiC4a8nOwL2op0LFro50yA4RxLk2Yu2sqIdxa4sedBRL6sezfEUzoylMZVB/pub?gid=349896899&single=true&output=csv"

def get_sheet_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        print(f"Error fetching sheet: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/markers', methods=['GET'])
def get_markers():
    data = get_sheet_data()
    markers = []

    for _, row in data.iterrows():
        if pd.notna(row['Location Lat']) and pd.notna(row['Location Lon']):
            color = 'blue'
            if str(row.get('Active Location', '')).strip().lower() == 'yes':
                color = 'green'
            elif str(row.get('Active Location', '')).strip().lower() == 'no':
                color = 'Gold'
            if str(row.get('Potential Exit', '')).strip().lower() == 'yes':
                color = 'red'
            if str(row.get('Active Location', '')).strip().lower() == 'no' and str(row.get('BPHR Remarks', '')).strip() != '':
                color = 'LawnGreen'

            markers.append({
                'location': row.get('Location', 'Unknown'),
                'latitude': row['Location Lat'],
                'longitude': row['Location Lon'],
                'color': color,
                'mrf_id': row.get('BPHR Remarks', 'N/A'),
                'Emp_Id': row.get('Emp ID', 'N/A'),
                'Emp_Name': row.get('Emp Name', 'N/A')
            })

    return jsonify(markers)

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
