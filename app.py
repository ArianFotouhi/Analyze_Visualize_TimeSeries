from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# import matplotlib.pyplot as plt
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "!241$gc"

users = {
    "user1":"pass1",
    "user2":"pass2"
}


# df = pd.read_csv("data/AAL.csv")


#Authentication
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

def data_render(to_dict=True):
    # time_series_data = [
    #     {'Date': '2022-01-01', 'Volume': 3},
    #     {'Date': '2022-01-02', 'Volume': 15},
    #     {'Date': '2022-01-03', 'Volume': 12},
    #     {'Date': '2022-01-04', 'Volume': 14},
    #     {'Date': '2022-01-05', 'Volume': 25},
    #     {'Date': '2022-01-06', 'Volume': 8},
    #     ]
    
    
    df = pd.read_csv("data/AAL.csv")
    categories = df['Country'].unique().tolist()
    
    if to_dict:
        print(df.head())
        df = df.to_dict(orient='records')
    
    return df,categories

#Routes

#Home
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
    
  

    
#Visualization
@app.route('/visual', methods=['GET','POST'])
def visual():
    if 'username' not in session:

        return redirect('/login')

    data, categories = data_render(to_dict=True)

            
    # Pass the time series data to the template
    
    return render_template('visual.html', data=data, countries=categories)

# Update plot based on country filter

@app.route('/update_plot', methods=['POST'])
def update_plot():
    df, _ = data_render(to_dict=False)
    selected_country = request.form['country']
    
    if selected_country:
        filtered_df = df[df['Country'] == selected_country]
    else:
        filtered_df = df
    
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
