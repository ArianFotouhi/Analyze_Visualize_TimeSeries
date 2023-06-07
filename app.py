from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd

app = Flask(__name__)
app.secret_key = "!241$gc"

users = {
    "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['1','2','3','4','5','6','7','8','9','10']},

    "user1": {"password": "pass", "ClientID": 1 , 'AccessCL':['1','2','3']},
    "user2": {"password": "pass", "ClientID": 2, 'AccessCL':['2']},
    "user3": {"password": "pass", "ClientID": 3, 'AccessCL':['3']},
    "user4": {"password": "pass", "ClientID": 4, 'AccessCL':['4']},
    "user5": {"password": "pass", "ClientID": 5 , 'AccessCL':['5']},
    "user6": {"password": "pass", "ClientID": 6 , 'AccessCL':['6']},
    "user7": {"password": "pass", "ClientID": 7 , 'AccessCL':['7']},
    "user8": {"password": "pass", "ClientID": 8 , 'AccessCL':['8']},
    "user9": {"password": "pass", "ClientID": 9 , 'AccessCL':['9']},
    "user10": {"password": "pass", "ClientID": 10 , 'AccessCL':['10']},
}

def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

def load_data():
    df = pd.read_csv("data/AAL.csv")
    # df['Date'] = pd.to_datetime(df['Date'])
    return df

def filter_data(username, df, selected_client, access_clients):
    if selected_client:

        if selected_client in access_clients:
            
        # filtering of client on upper left of screen
            filtered_df = df[df['ClientID'] == int(selected_client)]
        else:
            filtered_df = None

    elif users[username]["ClientID"] == 'admin':
        
        return df
    else:
       
        filtered_df = df[df['ClientID'] == users[username]["ClientID"]]
       
    return filtered_df

def LoungeCounter(client_id):
    df = load_data()
    unique_count = df.loc[df['ClientID'] == client_id, 'Lounge_ID'].nunique()
    return unique_count

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

    selected_client = request.args.get('client', '')

    username = session["username"]
    access_clients = users[username]["AccessCL"]

    df = load_data()
    filtered_df = filter_data(session["username"], df, selected_client, access_clients)
    
    
    data = filtered_df.to_dict(orient='records')
    
    
    # clients = df['ClientID'].unique().tolist() if 'admin' in access_clients else access_clients

    return render_template('visual.html', data=data, clients=access_clients)

@app.route('/update_plot', methods=['POST'])
def update_plot():
    selected_client = request.form['client']
    df = load_data()
    
    if selected_client:
        filtered_df = filter_data(session["username"], df, selected_client,selected_client)
       
        trace = {
            'x': filtered_df['Date'].tolist(),
            'y': filtered_df['Volume'].tolist(),
            'text': filtered_df.apply(lambda row: f"ClientID: {row['ClientID']}<br>Low: {row['Low']}", axis=1).tolist(),
            'hovertemplate': '%{text}',
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Time Series'
        }
        
        return jsonify([trace])
    else:
        traces = []
        
        username = session["username"]
        access_clients = users[username]["AccessCL"]


        for client in access_clients:
            
            client_df = filter_data(session["username"], df, client,access_clients)
            
            trace = {
                'x': client_df['Date'].tolist(),
                'y': client_df['Volume'].tolist(),
                'text': client_df.apply(lambda row: f"ClientID: {row['ClientID']}<br>Low: {row['Low']}", axis=1).tolist(),
                'hovertemplate': '%{text}',
                'type': 'scatter',
                'mode': 'lines',
                'name': f'Time Series - ClientID {client}'
            }
            traces.append(trace)
            
        return jsonify(traces)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
