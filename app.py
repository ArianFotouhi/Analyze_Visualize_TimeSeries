from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import pandas as pd

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


#Routes

#Home
@app.route("/")
def home():
    return render_template("login.html")

#Login
@app.route("/login", methods=["GET,POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if authenticate(username, password):
        session["username"] = username
        return redirect(url_for("visual"))
    else:
        return render_template("login.html", error="Invalid username or password")
    
#Visualization
app.route("/visual")
def visual():
    if "username" not in session:
        return redirect(url_for("home"))
    
    df = pd.read_csv("datafile.csv")
    
    #do the analysis here
    # ...

    plt.plot(df["timestamp"], df["value"])
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.title("Time Series Data")
    plt.savefig("static/plot.png")

    return render_template("timeseries.html")




if __name__ == "__main__":
    app.run(debug=True)