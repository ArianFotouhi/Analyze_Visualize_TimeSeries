from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd

app = Flask(__name__)
app.secret_key = "!241$gc"

users = {
    "user0": {"password": "pass", "ClientID": 'admin'},

    "user1": {"password": "pass", "ClientID": 1},
    "user2": {"password": "pass", "ClientID": 2},
    "user3": {"password": "pass", "ClientID": 3},
    "user4": {"password": "pass", "ClientID": 4},
    "user5": {"password": "pass", "ClientID": 5},
    "user6": {"password": "pass", "ClientID": 6},
    "user7": {"password": "pass", "ClientID": 7},
    "user8": {"password": "pass", "ClientID": 8},
    "user9": {"password": "pass", "ClientID": 9},
    "user10": {"password": "pass", "ClientID": 10},
}

def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

def load_data():
    df = pd.read_csv("data/AAL.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def filter_data(username, df, selected_country):
    if selected_country:
        #filtering of country on upper left of screen
        filtered_df = df[df['Country'] == selected_country]
    elif users[username]["ClientID"] == 'admin':
        return df
    else:
        filtered_df = df[df['ClientID'] == users[username]["ClientID"]]
    return filtered_df

@app.route('/', methods=['GET'])
def index():
    if 'username' in session:
        return redirect('/visual')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session["username"] = username
            return redirect('/visual')
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/visual', methods=['GET'])
def visual():
    if 'username' not in session:
        return redirect('/login')

    selected_country = request.args.get('country', '')
    df = load_data()
    filtered_df = filter_data(session["username"], df, selected_country)
    
    data = filtered_df.to_dict(orient='records')
    categories = df['Country'].unique().tolist()

    return render_template('visual.html', data=data, countries=categories)

@app.route('/update_plot', methods=['POST'])
def update_plot():
    selected_country = request.form['country']
    df = load_data()
    filtered_df = filter_data(session["username"], df, selected_country)
    
    trace = {
        'x': filtered_df['Date'].tolist(),
        'y': filtered_df['Volume'].tolist(),
        'text': filtered_df.apply(lambda row: f"Country: {row['Country']}<br>Low: {row['Low']}", axis=1).tolist(),
        'hovertemplate': '%{text}',
        'type': 'scatter',
        'mode': 'lines',
        'name': 'Time Series'
    }
    
    return jsonify(trace)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
