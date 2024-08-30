from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

SUPABASE_URL = "https://haqjxxgbibdokqkvmpsq.supabase.co/rest/v1/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhcWp4eGdiaWJkb2txa3ZtcHNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNDQzMjA3MiwiZXhwIjoyMDQwMDA4MDcyfQ.FDPI9YA-Zt_D_0LoylWGTxoSEznm1vP2gcqgQuyTePA"


@app.route('/')
def detailed_history():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    response = requests.get(f"{SUPABASE_URL}Users", headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        data = []

    # Aggregate data by user
    user_data = defaultdict(
        lambda: {
            'username': '',
            'Pool': 0,
            'oldapt': 0,
            'newapt': 0,
            'gym': 0,
            'session_time': 0,  # Total session time
            'rating': 0,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    for entry in data:
        username = entry.get('username', 'Anonymous')
        option = entry.get('option', '')
        timer_value = round(entry.get('timer_value', 5))
        rating = entry.get('rating', 0)

        if username not in user_data:
            user_data[username]['username'] = username

        if option in ['Pool', 'oldapt', 'newapt', 'gym']:
            user_data[username][option] += timer_value
            user_data[username][
                'rating'] = rating  # Assuming the latest rating should be used

        # Update session time
        user_data[username]['session_time'] = sum([
            user_data[username][key]
            for key in ['Pool', 'oldapt', 'newapt', 'gym']
        ])

    return render_template('index.html', users=user_data.values())


@app.route('/add_model', methods=['POST'])
def add_model():
    model_url = request.form.get('model_url')

    if not model_url:
        return "Model URL is required", 400

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    data = {"Model_url": model_url}

    response = requests.post(f"{SUPABASE_URL}Models",
                             headers=headers,
                             json=data)

    if response.status_code == 201:
        return "Model added successfully", 201
    else:
        return f"Failed to add model: {response.text}", response.status_code


if __name__ == '__main__':
    app.run(debug=True)
