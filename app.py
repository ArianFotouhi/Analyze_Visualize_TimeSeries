from flask import Flask, render_template, request, redirect, session, jsonify
from utils import load_data, filter_data_by_cl, dropdown_menu_filter, LoungeCounter, stream_on_off, active_inactive_lounges, active_clients_percent, volume_rate, cl_lounges_dict, lounge_crowdedness, get_notifications, ParameterCounter
from config import Date_col, Lounge_ID_Col, CLName_Col, Volume_ID_Col,  users, time_alert, crowdedness_alert, Airport_Name_Col, Time_col
from authentication import Authentication

authenticate = Authentication().authenticate
app = Flask(__name__)
app.secret_key = "!241$gc"



@app.route('/', methods=['GET'])
def index():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session["username"] = username
            return redirect('/home')
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")



@app.route('/home', methods=['GET','POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    df = load_data()

    username = session["username"]
    access_clients = users[username]["AccessCL"]

    accessed_df = filter_data_by_cl(session["username"], df, '', access_clients)

    data = accessed_df.to_dict(orient='records')
    crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert)

    

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)
    cl_lounges_ = cl_lounges_dict('lounges')
    notifications = get_notifications(inact_loung_num,inactive_clients,crowdedness)
    
    

    stat_list = [act_loung_num, inact_loung_num,vol_curr, vol_prev, len(active_clients), len(inactive_clients),inactive_lounges, crowdedness, notifications]

    
    return render_template('index.html', data= data, clients= access_clients, stats= stat_list, cl_lounges_= cl_lounges_)


  
    

@app.route('/update_plot', methods=['POST'])
def update_plot():
    selected_client = request.form['client']
    selected_lounge = request.form['lounge_name']
   
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    
    df = load_data()


    #scales: sec, min, hour, day, mo, year
    no_data_dict = stream_on_off(scale='day', length=time_alert)

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
                airport_list, airport_num = ParameterCounter(name = selected_client, base= CLName_Col, to_be_counted= Airport_Name_Col)
        
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
            'title': f'CL {selected_client} Active Lounge {actives}/{ actives + inactives}, Airport No. {airport_num}',
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
            airport_list, airport_num = ParameterCounter(name = client, base= CLName_Col, to_be_counted= Airport_Name_Col)

            layout = {
                'title': f'{client} Active Lounge {actives}/{ actives + inactives}, AP No. {airport_num}',
                'font': {
                        'size': 8 },
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


@app.route('/intelligence_hub', methods=['GET'])
def intelligence_hub():
    username = session["username"]
    access_clients = users[username]["AccessCL"]

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    crowdedness = lounge_crowdedness(date='latest',alert = crowdedness_alert)

    stat_list = [inactive_clients,inactive_lounges,crowdedness]
    
    return render_template('intelligence_hub.html', clients= access_clients, stats= stat_list)



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
