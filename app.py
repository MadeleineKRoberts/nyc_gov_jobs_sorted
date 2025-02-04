from flask import Flask, render_template, request
import pandas as pd
import requests

app = Flask(__name__)

# NYC Jobs API URL
API_URL = "https://data.cityofnewyork.us/resource/kpav-sd4t.json"

def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return []

@app.route('/')
def index():
    # Fetch data and create the DataFrame
    all_data = fetch_data()
    df = pd.DataFrame(all_data)

    # Drop rows where 'Job ID' is NaN
    df = df.dropna(subset=['job_id'])
    df = df.drop_duplicates()

    # Convert date fields to datetime for sorting
    df['posting_updated'] = pd.to_datetime(df['posting_updated'], errors='coerce')
    df['post_until'] = pd.to_datetime(df['post_until'], errors='coerce')

    # Define columns to display
    cols_to_display = ['job_id', 'number_of_positions', 'business_title', 'job_category',
        'full_time_part_time_indicator', 'career_level', 'salary_range_from',
        'salary_range_to', 'division_work_unit', 'to_apply',
        'posting_date', 'post_until', 'posting_updated'
    ]
    df = df[cols_to_display]

    # Handle sorting
    sort_order = request.args.get('sort', 'desc')  # Default: descending
    df = df.sort_values(by='posting_updated', ascending=(sort_order == 'asc'))

    # Handle search
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        df = df[df['business_title'].str.lower().str.contains(search_query, na=False)]

    return render_template('index.html', jobs=df.to_dict(orient='records'), sort_order=sort_order, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True)

