from flask import Flask, render_template, request, redirect, url_for, session, send_file
from decouple import config
from config import config
from src import init_app

configuration = config['development']
app = init_app(configuration)

if __name__ == "__main__":
    app.run(debug=True,port=5000)
    #app.run()
