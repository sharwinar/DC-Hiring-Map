import os
import pickle
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import geopandas as gpd

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
    data = get_sheet_data(SHEET_ID, SHEET_NAME)
    markers = []
    
    for _, row in data.iterrows():
        if pd.notna(row['Location Lat']) and pd.notna(row['Location Lon']):
            color = 'blue'  # Default color for all locations
            if row.get('Active Location', '').strip().lower() == 'yes':
                color = 'green'
            elif row.get('Active Location', '').strip().lower() == 'no':
                color = 'Gold'
            if row.get('Potential Exit', '').strip().lower() == 'yes':
                color = 'red'
            if row.get('Active Location', '').strip().lower() == 'no' and row.get('BPHR Remarks', '').strip().lower() != '':
                color = 'LawnGreen'
            
            markers.append({
                'location': row['Location'],
                'latitude': row['Location Lat'],
                'longitude': row['Location Lon'],
                'color': color,
                'mrf_id':row.get('BPHR Remarks', 'N/A'),
                'Emp_Id': row.get('Emp ID', 'N/A'),
                'Emp_Name': row.get('Emp Name', 'N/A')
            })
        
        # Separate New Proposed Locations
        # if pd.notna(row['New Proposed Lat']) and pd.notna(row['New Proposed Lon']):
        #     markers.append({
        #         'location': row['New Proposed Location'],
        #         'latitude': row['New Proposed Lat'],
        #         'longitude': row['New Proposed Lon'],
        #         'color': 'Purple',
        #         'mrf_id': 'Proposed Location'
        #     })
    
    return jsonify(markers)

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
