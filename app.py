from flask import Flask, render_template_string
import requests
import pandas as pd

app = Flask(__name__)

# Base URL for the JSON data API
base_url = "https://data.cityofnewyork.us/resource/kpav-sd4t.json"

# Parameters for pagination
limit = 1000
offset = 0
all_data = []

# Function to fetch data
def fetch_data():
    global offset
    while True:
        params = {
            "$limit": limit,
            "$offset": offset
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            chunk_data = response.json()
            if not chunk_data:
                break
            all_data.extend(chunk_data)
            offset += limit
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            break

# Route to display the data in the browser
@app.route('/')
def index():
    # Fetch data and create the DataFrame
    fetch_data()
    df = pd.DataFrame(all_data)

    # Drop rows where 'Job ID' is NaN
    df = df.dropna(subset=['job_id'])

    # Convert DataFrame to HTML
    html_table = df.to_html(classes='table table-striped', index=False)

    # Return the HTML content
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NYC Job Listings</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">NYC Job Listings</h1>
                <div class="table-responsive">
                    {{ html_table | safe }}
                </div>
            </div>
        </body>
        </html>
    """, html_table=html_table)

if __name__ == '__main__':
    app.run(debug=True)
