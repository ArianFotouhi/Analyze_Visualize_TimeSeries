from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)
app.secret_key = "!241$gc"

users = {
    "user1":"pass1",
    "user2":"pass2"
}

def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

