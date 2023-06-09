from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "!241$gc"


Date_col ='Date'
CLName_Col = 'ClientID'
# LoungNm_Col = 'Lounge_ID'
Lounge_ID_Col = 'Lounge_ID'
Volume_ID_Col = 'Volume'



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
            filtered_df = df[df[CLName_Col] == int(selected_client)]
        else:
            filtered_df = None

    elif users[username]['ClientID'] == 'admin':
        
        return df
    else:
       
        filtered_df = df[df[CLName_Col] == users[username]['ClientID']]
       
    return filtered_df

def LoungeCounter(client_id):
    df = load_data()
    unique_count = df.loc[df[CLName_Col] == client_id, Lounge_ID_Col].nunique()
    return unique_count

import pandas as pd
from datetime import datetime, timedelta

def stream_on_off(scale='sec', length=10):
    no_data = {}
    df = load_data()
    unique_ids = df[CLName_Col].nunique()

    for i in range(1, unique_ids+1):
        # Assuming the 'time' column is of type datetime
        df[Date_col] = pd.to_datetime(df[Date_col])

        # Filter the DataFrame for the last record with id=X
        last_record = df[df[CLName_Col] == i].tail(1)
        # Get the timestamp of the last record
        last_time = last_record[Date_col].iat[0]

        # Calculate the time difference based on the specified scale and length
        if scale == 'sec':
            time_diff = datetime.now() - last_time
            threshold = timedelta(seconds=int(length))
        elif scale == 'min':
            time_diff = (datetime.now() - last_time) // timedelta(minutes=1)
            threshold = int(length)
        elif scale == 'hour':
            time_diff = (datetime.now() - last_time) // timedelta(hours=1)
            threshold = int(length)
        elif scale == 'day':
            time_diff = (datetime.now() - last_time) // timedelta(days=1)
            threshold = int(length)
        elif scale == 'min':
            time_diff = (datetime.now() - last_time) // timedelta(days=30)
            threshold = int(length)
        elif scale == 'year':
            time_diff = (datetime.now() - last_time) // timedelta(days=365)
            threshold = int(length)
        else:
            raise ValueError("Invalid scale. Please choose one of 'sec', 'min', 'hour', 'day', 'min', or 'year'.")

        # Check if the time difference is more than the specified threshold
        if time_diff > threshold:
            no_data[i] = last_time

    return no_data

from datetime import datetime, timedelta
import pytz
import pandas as pd

def get_latest_lounge_status(df, time_difference):
    current_date = datetime.now(pytz.UTC)
    latest_record = None

    for _, group_df in df.groupby([CLName_Col, Lounge_ID_Col]):
        group_df[Date_col] = pd.to_datetime(group_df[Date_col], format='%Y-%m-%d %H:%M:%S')
        group_df = group_df.sort_values(Date_col, ascending=False)  # Sort by date in descending order
        latest_date = group_df.iloc[0][Date_col]

        # Ensure the latest date has the same timezone as current_date
        if latest_date.tzinfo is None:
            latest_date = pytz.UTC.localize(latest_date)
        else:
            latest_date = latest_date.astimezone(pytz.UTC)

        # Calculate the difference between the current date and the latest date
        date_diff = (current_date.date() - latest_date.date()).days

        if date_diff <= time_difference:
            latest_record = group_df.iloc[0]
            break

    return latest_record


def convert_to_utc(date, time_difference, date_format, convert_option=None, local_timezone='EST', utc_timezone='UTC'):
    if convert_option is None:
        return date

    local_tz = pytz.timezone(local_timezone)
    utc_tz = pytz.timezone(utc_timezone)

    if isinstance(date, pd.Timestamp):
        # Convert pandas Timestamp to Python datetime object
        date = date.to_pydatetime()

    if convert_option == 'local':
        # Convert system local time to UTC
        local_dt = datetime.now(local_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_tz.localize(local_dt).astimezone(utc_tz)

    elif convert_option == 'input_data':
        # Convert input data date from local timezone to UTC
        local_dt = datetime.strptime(date, date_format)
        local_dt = local_tz.localize(local_dt).astimezone(utc_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_dt

    elif convert_option == 'both':
        # Convert both system local time and input data date from local timezone to UTC
        system_local_dt = datetime.now(local_tz)
        system_local_dt -= timedelta(days=time_difference)
        system_utc_dt = local_tz.localize(system_local_dt).astimezone(utc_tz)

        local_dt = datetime.strptime(date, date_format)
        local_dt = local_tz.localize(local_dt).astimezone(utc_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_dt

        return system_utc_dt, utc_dt

    return utc_dt


def get_lounge_status(date, time_difference):
    current_date = datetime.now(pytz.UTC)
    date_diff = (current_date.date() - date.date()).days

    if date_diff <= time_difference:
        return 'active'
    else:
        return 'inactive'


def active_inactive_lounges(clients, time_difference, date_format, convert_option=None):
    df = load_data()
    active_lounges = {}
    inactive_lounges = {}
    act_loung_num = 0
    inact_loung_num = 0

    for client_id in clients:
        client_df = filter_data(session["username"], df, client_id, clients)
        active_lounge_ids = set()
        inactive_lounge_ids = set()

        latest_record = get_latest_lounge_status(client_df, time_difference)
        while latest_record is not None:
            lounge_id = latest_record[Lounge_ID_Col]
            received_date = latest_record[Date_col]
            utc_date = convert_to_utc(received_date, time_difference, date_format, convert_option)

            if isinstance(utc_date, tuple):
                # Both conversion options
                lounge_status = get_lounge_status(utc_date[0], time_difference)
                input_data_lounge_status = get_lounge_status(utc_date[1], time_difference)

                if lounge_status == 'active' or input_data_lounge_status == 'active':
                    active_lounge_ids.add(lounge_id)
                else:
                    inactive_lounge_ids.add(lounge_id)
            else:
                # Single conversion option
                lounge_status = get_lounge_status(utc_date, time_difference)

                if lounge_status == 'active':
                    active_lounge_ids.add(lounge_id)
                else:
                    inactive_lounge_ids.add(lounge_id)

            # Remove the latest record from the DataFrame
            client_df = client_df[client_df[Lounge_ID_Col] != lounge_id]
            latest_record = get_latest_lounge_status(client_df, time_difference)

        if active_lounge_ids:
            act_loung_num += len(active_lounge_ids)
            active_lounges[client_id] = active_lounge_ids

        if inactive_lounge_ids:
            inact_loung_num += len(inactive_lounge_ids)
            inactive_lounges[client_id] = inactive_lounge_ids

    return active_lounges, inactive_lounges, act_loung_num, inact_loung_num



        #how many of lounges are active:
            #if  0 < pax_count 
            # (they are acttive) act++
            #else
            #(they are inactive) inact++
        #return (act, act+inact, inact/(act+inact))


    #retun:
    #how many of lounges are active
    #how many of lounges are inactive
    #percentage of active lounges

# def volume_rate(clients):  
#     #grab all pax of all lounges for a client in previous week
#     #grab all pax of all lounges for a client in current week
#     #percentage of them
#     pass

# def active_clients_percent(clients):
#     #how many of clients have at least one active lounge
#     #all clients
#     #percentage of them
#     pass




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

    #finds the active lounges for the selected clients
    
    lounges_percent = active_inactive_lounges(access_clients,time_difference=10000, date_format='%Y-%m-%d')
    print(lounges_percent)
    # volume_ratio = volume_rate(access_clients)
    # active_clients = active_clients_percent(access_clients)   

    return render_template('visual.html', data=data, clients=access_clients)

@app.route('/update_plot', methods=['POST'])
def update_plot():
    selected_client = request.form['client']
    df = load_data()
    
    no_data_dict = stream_on_off(scale='hour',length=1)

    if selected_client:
        filtered_df = filter_data(session["username"], df, selected_client, selected_client)
        lounge_num= LoungeCounter(int(selected_client))

        trace = {
            'x': filtered_df[Date_col].tolist(),
            'y': filtered_df[Volume_ID_Col].tolist(),
            'text': filtered_df.apply(lambda row: f"ClientID: {row[CLName_Col]}<br>Low: {row['Low']}", axis=1).tolist(),
            'hovertemplate': '%{text}',
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Time Series'
        }

        layout = {
            'title': f'CL ID {selected_client} Lounge num {lounge_num}',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Rate'}
        }

        
        if int(selected_client) in list(no_data_dict.keys()):
            error_message = f"Last update {no_data_dict[int(selected_client)]}"
        else:
            error_message = None

        return jsonify({'traces': [trace], 'layouts': [layout], 'error_messages': error_message})

    else:
        traces = []
        layouts = []
        errors = []

        username = session["username"]
        access_clients = users[username]["AccessCL"]

        for client in access_clients:
            client_df = filter_data(session["username"], df, client, access_clients)
            lounge_num= LoungeCounter(int(client))
            trace = {
                'x': client_df['Date'].tolist(),
                'y': client_df[Volume_ID_Col].tolist(),
                'text': client_df.apply(lambda row: f"ClientID: {row[CLName_Col]}<br>Low: {row['Low']}", axis=1).tolist(),
                'hovertemplate': '%{text}',
                'type': 'scatter',
                'mode': 'lines',
                'name': f'Time Series'
            }
            traces.append(trace)

            layout = {
                'title': f'CL {client} Active Lounge {lounge_num}/{lounge_num}',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Rate'}
            }
            layouts.append(layout)
           
            if int(client) in list(no_data_dict.keys()):
                error_message = f"Last update {no_data_dict[int(client)]}"
            else:
                error_message = None

            errors.append(error_message)

        return jsonify({'traces': traces, 'layouts': layouts , 'errors': errors})




@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
