from flask import Flask, render_template, request, redirect, url_for, session
# import matplotlib.pyplot as plt
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "!241$gc"

users = {
    "user1":"pass1",
    "user2":"pass2"
}



#Authentication
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

def data_render():
    # time_series_data = [
    #     {'Date': '2022-01-01', 'Volume': 3},
    #     {'Date': '2022-01-02', 'Volume': 15},
    #     {'Date': '2022-01-03', 'Volume': 12},
    #     {'Date': '2022-01-04', 'Volume': 14},
    #     {'Date': '2022-01-05', 'Volume': 25},
    #     {'Date': '2022-01-06', 'Volume': 8},
    #     ]
    
    
        
    
    df = pd.read_csv("data/AAL.csv")
    print(df.head())
    data_dict = df.to_dict(orient='records')
    
    print(data_dict)


    # data = json.dumps(data_dict)

    
    
    return data_dict

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

    data = data_render()

            
    # Pass the time series data to the template
    return render_template('visual.html', data=data)



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
