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

# Define OAuth 2.0 credentials and scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
import base64

GOOGLE_CREDS_B64 = os.environ.get('GOOGLE_CREDS_B64')

if not os.path.exists('credentials.json') and GOOGLE_CREDS_B64:
    with open('credentials.json', 'wb') as f:
        f.write(base64.b64decode(GOOGLE_CREDS_B64))

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'sheets'
API_VERSION = 'v4'

# Authenticate Google Sheets API
def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build(API_NAME, API_VERSION, credentials=creds)

# Load GeoJSON for state boundaries
geo_data = gpd.read_file('india_states.geojson')

# Google Sheets Details
SHEET_ID = '1Cw65h0KVhJqKaYz-JnjXJ6cv59ssUTwXRiL6LErfwjA'
SHEET_NAME = 'Ramp Up'

def get_sheet_data(sheet_id, sheet_name):
    service = authenticate()
    sheet = service.spreadsheets().values()
    result = sheet.get(spreadsheetId=sheet_id, range=sheet_name).execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()

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

@app.route('/geojson')
def get_geojson():
    return jsonify(geo_data.__geo_interface__)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
