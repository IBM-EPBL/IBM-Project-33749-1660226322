from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db

#conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wgd60166;PWD=OuTi8U0vKFGF69pK", '', '')
print("Success")

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')
