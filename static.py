from flask import Flask, render_template, url_for

app = Flask(__name__)

# Serve static files
app.static_folder = 'static'
app.static_url_path = '/static'

