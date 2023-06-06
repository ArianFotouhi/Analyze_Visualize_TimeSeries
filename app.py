from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)
app.secret_key = "!241$gc"