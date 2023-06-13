from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = "!241$gc"


# Date_col ='Date'
# CLName_Col = 'ClientID'
# # LoungNm_Col = 'Lounge_ID'
# Lounge_ID_Col = 'Lounge_ID'
# Volume_ID_Col = 'Volume'
# users = {
#     "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['1','2','3','4','5','6','7','8','9','10']},

#     "user1": {"password": "pass", "ClientID": 1 , 'AccessCL':['1','2','3']},
#     "user2": {"password": "pass", "ClientID": 2, 'AccessCL':['2']},
#     "user3": {"password": "pass", "ClientID": 3, 'AccessCL':['3']},
#     "user4": {"password": "pass", "ClientID": 4, 'AccessCL':['4']},
#     "user5": {"password": "pass", "ClientID": 5 , 'AccessCL':['5']},
#     "user6": {"password": "pass", "ClientID": 6 , 'AccessCL':['6']},
#     "user7": {"password": "pass", "ClientID": 7 , 'AccessCL':['7']},
#     "user8": {"password": "pass", "ClientID": 8 , 'AccessCL':['8']},
#     "user9": {"password": "pass", "ClientID": 9 , 'AccessCL':['9']},
#     "user10": {"password": "pass", "ClientID": 10 , 'AccessCL':['10']},
# }



Date_col ='DATE_UTC'
CLName_Col = 'CLIENT_NAME'
Lounge_ID_Col = 'lounge_name'
Volume_ID_Col = 'COUNT_PAX_ALLOWED'
users = {
    "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['LH','LX','MAG']},

    "user1": {"password": "pass", "ClientID": 1 , 'AccessCL':['MAG','LX']},
    "user2": {"password": "pass", "ClientID": 2, 'AccessCL':['LH']},
    "user3": {"password": "pass", "ClientID": 3, 'AccessCL':['LX']},
}


def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

def load_data():
    df = pd.read_csv("data/data.txt")
    # df['Date'] = pd.to_datetime(df['Date'])
    return df








def filter_data_by_cl(username, df, selected_client, access_clients):
    
    if selected_client:
        if selected_client in access_clients:
        # filtering of client on upper left of screen
            filtered_df = df[df[CLName_Col] == str(selected_client)]
        else:
            filtered_df = None

    elif users[username]['ClientID'] == 'admin':
        return df
    else:
        # filtered_df = df[df[CLName_Col] == users[username]['AccessCL']]
        filtered_df = df[df[CLName_Col].isin(list(users[username]['AccessCL']))]
    return filtered_df


def dropdown_menu_filter(df, col_name,selected_val):
    
    filtered_df = df[df[col_name] == selected_val]


    return filtered_df



def LoungeCounter(name, modality='cl'):
    df = load_data()
    if modality == 'cl':
        unique_count = df.loc[df[CLName_Col] == name, Lounge_ID_Col].nunique()
        return unique_count
    elif modality == 'lg':
        cl = df.loc[df[Lounge_ID_Col] == name][CLName_Col][-1:].values[0]
        unique_count = LoungeCounter(name=cl)
        return unique_count, cl



def stream_on_off(scale='sec', length=10):
    no_data = {}
    df = load_data()
    # unique_ids = df[CLName_Col].nunique()
    unique_ids = set(df[CLName_Col].unique())
    for i in unique_ids:
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
        elif scale == 'mo':
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


def active_inactive_lounges(clients):
    time_difference=3 
    date_format= '%Y-%m-%d'
    convert_option=None
    df = load_data()
    active_lounges = {}
    inactive_lounges = {}
    act_loung_num = 0
    inact_loung_num = 0

    for client_id in clients:
        client_df = filter_data_by_cl(session["username"], df, client_id, clients)
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




def active_clients_percent(clients,actdict, inactdict):
    active_cli=[]
    inact_cli=[]

    for i in clients:
        if i in  actdict:
            active_cli.append(i)
        else:
            inact_cli.append(i)
    return active_cli, inact_cli

def volume_rate(clients, amount=5):
    rates = {}
    df = load_data()
    df[Date_col] = pd.to_datetime(df[Date_col])
   
   
    volume_sum_x = 0
    volume_sum_2x = 0
    current_vol = 0
    prev_vol = 0
    for client_id in clients:
        client_df = df[df[CLName_Col] == client_id]  # Filter the DataFrame for a particular client
        
       
        
        latest_record = client_df.iloc[-1]  # Get the latest record for the client
        
        last_date = latest_record[Date_col]
        start_date_x = last_date - pd.DateOffset(days=amount)
        start_date_2x = last_date - pd.DateOffset(days=2 * amount)
        
        print('start datex',start_date_x)
        print('start date 2x',start_date_2x)

        volume_sum_x = client_df[(client_df[Date_col] > start_date_x) & (client_df[Date_col] <= last_date)][Volume_ID_Col].sum()
        volume_sum_2x = client_df[(client_df[Date_col] > start_date_2x) & (client_df[Date_col] <= start_date_x)][Volume_ID_Col].sum()
        
        print('volume sum x',volume_sum_x)
        print('volume sum 2x',volume_sum_2x)
        current_vol += volume_sum_x
        prev_vol += volume_sum_2x

        rates[client_id] = [volume_sum_x, volume_sum_2x]
        print('rates',rates,'\n')
    

            


    return rates, current_vol,  prev_vol


def cl_lounges_dict(column):
    if column =='lounges':
        username = session["username"]
        cl_list = users[username]["AccessCL"]
        
        actives, inactives, _, _ = active_inactive_lounges(users[username]["AccessCL"])

        
        output = {}
        for i in cl_list:
            if i in actives and i in inactives:
                output[i] = list(set(actives[i].extend(inactives[i])))
            elif i in actives:
                output[i] = actives[i]
            else:
                output[i] = inactives[i]
        
        output[''] = []
        for i in output:
            if i != '':
                output[''].extend(output[i])


        return output
    
    elif column == 'airport':
        pass







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



@app.route('/visual', methods=['GET','POST'])
def visual():
    if 'username' not in session:
        return redirect('/login')

    df = load_data()

    username = session["username"]
    access_clients = users[username]["AccessCL"]

    accessed_df = filter_data_by_cl(session["username"], df, '', access_clients)

    data = accessed_df.to_dict(orient='records')

    

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)

    volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)
    cl_lounges_ = cl_lounges_dict('lounges')
  

    stat_list = [act_loung_num, inact_loung_num,vol_curr, vol_prev, len(active_clients), len(inactive_clients),inactive_lounges]

    print(active_clients)
    return render_template('visual.html', data= data, clients= access_clients, stats= stat_list, cl_lounges_= cl_lounges_)

################################

  
    

@app.route('/update_plot', methods=['POST'])
def update_plot():
    selected_client = request.form['client']
    selected_lounge = request.form['lounge_name']
   
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    
    df = load_data()


    #scales: sec, min, hour, day, mo, year
    no_data_dict = stream_on_off(scale='day', length=7)

    #to avoid strem monitoring
    # no_data_dict = {}

    if selected_client or selected_lounge :
        active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)

        # lounge_num  = LoungeCounter(str(client))

                
      

        if selected_client:
            df = dropdown_menu_filter(df,CLName_Col ,selected_client)
            # lounge_num = LoungeCounter(name = str(selected_client))
            

        if selected_lounge:
            df = dropdown_menu_filter(df,Lounge_ID_Col ,selected_lounge)
           
            # modality can be 'lg' or'cl'
            if selected_client == '':
                lounge_num, selected_client  = LoungeCounter(name = str(selected_lounge), modality='lg')
                
        
        if selected_client in active_lounges:
                actives = len(active_lounges[selected_client])
        else:
                actives = 0
        if selected_client in inactive_lounges:
                inactives = len(inactive_lounges[selected_client])
        else:
                inactives = 0
                # lounge_num = 0


        trace = {
            'x': df[Date_col].unique().tolist(),
            'y': df.groupby(Date_col)[Volume_ID_Col].sum().to_list(),
            'text': df.groupby(Date_col)[Volume_ID_Col].sum().apply(lambda x: f"Rate: {x}<br>").tolist(),
            'hovertemplate': '%{text}',
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Time Series'
        }

        layout = {
            'title': f'CL {selected_client} Active Lounge {actives}/{ actives + inactives}',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Rate'}
        }

        
        if str(selected_client) in list(no_data_dict.keys()):
            error_message = f"Last update {no_data_dict[str(selected_client)]}"
        else:
            error_message = None

        return jsonify({'traces': [trace], 'layouts': [layout], 'error_messages': error_message})

    else:
        traces = []
        layouts = []
        errors = []
       

        active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)


        for client in access_clients:
            client_df = filter_data_by_cl(session["username"], df, client, access_clients)
            # lounge_num  = LoungeCounter(str(client))

            if str(client) in active_lounges:
                actives = len(active_lounges[str(client)])
            else:
                actives = 0
            if client in inactive_lounges:
                inactives = len(inactive_lounges[str(client)])
            else:
                inactives = 0
          
            trace = {
                'x': client_df[Date_col].unique().tolist(),
                'y': client_df.groupby(Date_col)[Volume_ID_Col].sum().to_list(),
                'text': client_df.groupby(Date_col)[Volume_ID_Col].sum().apply(lambda x: f"Rate: {x}<br>").tolist(),
                'hovertemplate': '%{text}',
                'type': 'scatter',
                'mode': 'lines',
                'name': f'Time Series'
            }
            traces.append(trace)

            layout = {
                'title': f'{client} Active Lounge {actives}/{ actives + inactives}',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Rate'}
            }
            layouts.append(layout)
           
            if str(client) in list(no_data_dict.keys()):
                error_message = f"Last update {no_data_dict[str(client)]}"
            else:
                error_message = None

            errors.append(error_message)

        
        
        return jsonify({'traces': traces, 'layouts': layouts , 'errors': errors})


@app.route('/dormant', methods=['GET'])
def dormant():
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)

    stat_list = [inactive_clients,inactive_lounges]
    
    return render_template('dormant.html', clients= access_clients, stats= stat_list)



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
