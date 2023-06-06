from flask import Flask, render_template, request, redirect, url_for, session
# import matplotlib.pyplot as plt
# import pandas as pd

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
    time_series_data = [
        {'date': '2022-01-01', 'value': 3},
        {'date': '2022-01-02', 'value': 15},
        {'date': '2022-01-03', 'value': 12},
        {'date': '2022-01-04', 'value': 14},
        {'date': '2022-01-05', 'value': 25},
        {'date': '2022-01-06', 'value': 8},
        ]
    return time_series_data

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
