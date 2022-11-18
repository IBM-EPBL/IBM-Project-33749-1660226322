from turtle import st
from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
import ibm_db
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime

from flask import Flask

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wgd60166;PWD=OuTi8U0vKFGF69pK", '', '')

app = Flask(__name__)

var_list = []


app.secret_key = 'your secret key'


@app.route('/')
def home():
    if not session.get("name"):
        return render_template('home.html')
    return render_template('home.html', session=session)


@app.route('/register')
def new_student():
    return render_template('Register.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        cname = request.form['cname']
        state = request.form['state']
        city = request.form['city']
        mobileno = request.form['mobileno']
        emailid = request.form['emailid']
        password = request.form['password']
        pincode = request.form['pincode']

        sql = "SELECT * FROM Users WHERE EMAILID =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, emailid)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            users = []
            sql = "SELECT * FROM Users"
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_both(stmt)
            while dictionary != False:
                # print ("The Name is : ",  dictionary)
                users.append(dictionary)
                dictionary = ibm_db.fetch_both(stmt)
            return render_template('list.html', msg="You are already a member, please login using your details", users=users)
        else:

            var_list.append(fname)
            var_list.append(lname)
            var_list.append(cname)
            var_list.append(state)
            var_list.append(city)
            var_list.append(mobileno)
            var_list.append(emailid)
            var_list.append(password)
            var_list.append(pincode)

            bodytemp = r"C:\IBM\Project Development phase\SPRINT 3\templates\email.html"
            with open(bodytemp, "r", encoding='utf-8') as f:
                html = f.read()

            # Set up the email addresses and password. Please replace below with your email address and password
            email_from = 'jjishnu6@gmail.com'
            epassword = 'cwnttdcvtdkaudau'
            email_to = emailid

            # Generate today's date to be included in the email Subject
            date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = email_from
            email_message['To'] = email_to
            email_message['Subject'] = f'Report email - {date_str}'

            # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
            email_message.attach(MIMEText(html, "html"))
            # Convert it as a string
            email_string = email_message.as_string()

            # Connect to the Gmail SMTP server and Send Email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_from, epassword)
                server.sendmail(email_from, email_to, email_string)
            return render_template('notify.html')


@app.route('/confirm')
def confirnation():
    insert_sql = "INSERT INTO Users (FIRSTNAME, LASTNAME, COMPANYNAME, STATE, CITY, MOBILENO, EMAILID, PASSWORD, PINCODE)  VALUES (?,?,?,?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, var_list[0])
    ibm_db.bind_param(prep_stmt, 2, var_list[1])
    ibm_db.bind_param(prep_stmt, 3, var_list[2])
    ibm_db.bind_param(prep_stmt, 4, var_list[3])
    ibm_db.bind_param(prep_stmt, 5, var_list[4])
    ibm_db.bind_param(prep_stmt, 6, var_list[5])
    ibm_db.bind_param(prep_stmt, 7, var_list[6])
    ibm_db.bind_param(prep_stmt, 8, var_list[7])
    ibm_db.bind_param(prep_stmt, 9, var_list[8])
    ibm_db.execute(prep_stmt)
    return render_template('confirm.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM Users WHERE EMAILID =? AND PASSWORD =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            session['loggedin'] = True
            session['email'] = account['EMAILID']
            session['name'] = account['FIRSTNAME']

            return render_template('dashboard/dashboard.html')
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg=msg)


@app.route('/dashboard')
def dashboard():
    if session['loggedin'] == True:
        return render_template('dashboard/dashboard.html')
    else:
        return redirect(url_for('home'))


@app.route('/addproduct')
def addproduct():
    if session['loggedin'] == True:
        return render_template('dashboard/addproduct.html')
    else:
        return redirect(url_for('home'))


@app.route('/movement')
def movement():
    if session['loggedin'] == True:
        products = []
        sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, session['name'])
        ibm_db.execute(prep_stmt)
        dictionary = ibm_db.fetch_both(prep_stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            products.append(dictionary)
            dictionary = ibm_db.fetch_both(prep_stmt)

        if products:
            return render_template("dashboard/movement.html", products=products, session=session)
        else:
            return render_template("dashboard/movement.html")
    else:
        return redirect(url_for('home'))


@app.route('/moveproc', methods=['POST', 'GET'])
def moveproc():

    if request.method == 'POST':
        pname = request.form['pname']
        quantityout = request.form['quantityout']
        tow = request.form['to']
        print(quantityout)

    insert_sql = "UPDATE products SET QUANTITYOUT = ?, TO = ? WHERE PRODUCTNAME = ? AND HOLDERNAME = ?;"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, quantityout)
    ibm_db.bind_param(prep_stmt, 2, tow)
    ibm_db.bind_param(prep_stmt, 3, pname)
    ibm_db.bind_param(prep_stmt, 4, session['name'])
    ibm_db.execute(prep_stmt)
    select_sql = "SELECT QUANTITYIN from PRODUCTS WHERE PRODUCTNAME = ? AND HOLDERNAME = ?;"
    print(session['name'])
    prep_stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.bind_param(prep_stmt, 1, pname)
    ibm_db.bind_param(prep_stmt, 2, session['name'])
    ibm_db.execute(prep_stmt)
    outofstock = ibm_db.fetch_both(prep_stmt)
    if int(outofstock['QUANTITYIN']) <= int(quantityout):
        bodytemp = r"C:\IBM\Project Development phase\SPRINT 3\templates\email.html"
        with open(bodytemp, "r", encoding='utf-8') as f:
            html = f.read()

        # Set up the email addresses and password. Please replace below with your email address and password
        email_from = 'jjishnu6@gmail.com'
        epassword = 'cwnttdcvtdkaudau'
        email_to = session['email']

        # Generate today's date to be included in the email Subject
        date_str = pd.Timestamp.today().strftime('%d-%m-%Y')

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'Warning!!! {pname} - Out Of Stock - {date_str}'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))
        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, epassword)
            server.sendmail(email_from, email_to, email_string)
    products = []
    sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, session['name'])
    ibm_db.execute(prep_stmt)
    dictionary = ibm_db.fetch_both(prep_stmt)
    while dictionary != False:
        # print ("The Name is : ",  dictionary)
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(prep_stmt)

    return render_template('dashboard/movement.html', msg="Product movement noted!", products=products)


@app.route('/report')
def report():
    if session['loggedin'] == True:
        products = []
        stockonhand = []
        sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, session['name'])
        ibm_db.execute(prep_stmt)
        dictionary = ibm_db.fetch_both(prep_stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            products.append(dictionary)
            dictionary = ibm_db.fetch_both(prep_stmt)

        for i in products:
            if (i['QUANTITYIN'] != None and i['QUANTITYOUT'] != None):
                calc = int((i['QUANTITYIN'])) - int(i['QUANTITYOUT'])
                stockonhand.append(str(calc))

        return render_template('dashboard/report.html', row_row1=zip(products, stockonhand))
    else:
        return redirect(url_for('home'))


@app.route('/stockupdate')
def stock():
    if session['loggedin'] == True:
        products = []
        sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, session['name'])
        ibm_db.execute(prep_stmt)
        dictionary = ibm_db.fetch_both(prep_stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            products.append(dictionary)
            dictionary = ibm_db.fetch_both(prep_stmt)

        if products:
            return render_template("dashboard/stockupdate.html", products=products, session=session)
        else:
            return render_template("dashboard/stockupdate.html")
    else:
        return redirect(url_for('home'))


@app.route('/proc_delete', methods=['POST', 'GET'])
def proc_delete():
    prod_name = request.args.get('pname')
    delete_sql = "DELETE FROM products WHERE PRODUCTNAME = ? AND HOLDERNAME = ?;"
    prep_stmt = ibm_db.prepare(conn, delete_sql)
    ibm_db.bind_param(prep_stmt, 1, prod_name)
    ibm_db.bind_param(prep_stmt, 2, session['name'])
    ibm_db.execute(prep_stmt)

    products = []
    sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, session['name'])
    ibm_db.execute(prep_stmt)
    dictionary = ibm_db.fetch_both(prep_stmt)
    while dictionary != False:
        # print ("The Name is : ",  dictionary)
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(prep_stmt)
    return render_template('dashboard/stockupdate.html', msg='Product successfully deleted!', products=products)


@app.route('/proc_update', methods=['POST', 'GET'])
def proc_update():
    if request.method == 'POST':
        pname = request.form['pname']
        quantityin = request.form['quantityin']
        pid = request.form['pid']
    update_sql = "UPDATE products SET  QUANTITYIN = ? WHERE  HOLDERNAME = ? AND PRODUCTNAME = ?;"
    prep_stmt = ibm_db.prepare(conn, update_sql)

    ibm_db.bind_param(prep_stmt, 1, quantityin)
    ibm_db.bind_param(prep_stmt, 2, session['name'])
    ibm_db.bind_param(prep_stmt, 3, pname)

    ibm_db.execute(prep_stmt)

    products = []
    sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, session['name'])
    ibm_db.execute(prep_stmt)
    dictionary = ibm_db.fetch_both(prep_stmt)
    while dictionary != False:
        # print ("The Name is : ",  dictionary)
        products.append(dictionary)
        print(dictionary)
        dictionary = ibm_db.fetch_both(prep_stmt)
    return render_template('dashboard/stockupdate.html', msg='Product successfully updated!', products=products)


@app.route('/addproc', methods=['POST', 'GET'])
def addproc():
    if request.method == 'POST':
        pname = request.form['pname']
        quantity = request.form['quantity']
        the_time = datetime.now()
        the_time = the_time.replace(second=0, microsecond=0)

        sql = "SELECT * FROM Products WHERE HOLDERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['name'])
        ibm_db.execute(stmt)
        product = ibm_db.fetch_assoc(stmt)
        if product:

            if product['PRODUCTNAME'] == pname:

                return render_template('dashboard/addproduct.html', msg="Product already added! Add a new product.")
            else:
                sql = "INSERT INTO Products (PRODUCTNAME,QUANTITYIN,QUANTITYOUT,TO,DATE,HOLDERNAME) VALUES (?,?,?,?,?,?);"
                prep_stmt = ibm_db.prepare(conn, sql)
                ibm_db.bind_param(prep_stmt, 1, pname)
                ibm_db.bind_param(prep_stmt, 2, quantity)
                ibm_db.bind_param(prep_stmt, 3, '0')
                ibm_db.bind_param(prep_stmt, 4, '')
                ibm_db.bind_param(prep_stmt, 5, str(the_time))
                ibm_db.bind_param(prep_stmt, 6, session['name'])
                ibm_db.execute(prep_stmt)
                return render_template('dashboard/addproduct.html', msg="Product added")
        else:
            sql = "INSERT INTO Products (PRODUCTNAME,QUANTITYIN,QUANTITYOUT,TO,DATE,HOLDERNAME) VALUES (?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, pname)
            ibm_db.bind_param(prep_stmt, 2, quantity)
            ibm_db.bind_param(prep_stmt, 3, '0')
            ibm_db.bind_param(prep_stmt, 4, '')
            ibm_db.bind_param(prep_stmt, 5, str(the_time))
            ibm_db.bind_param(prep_stmt, 6, session['name'])
            ibm_db.execute(prep_stmt)
            return render_template('dashboard/addproduct.html', msg="Product added")


@app.route('/productlist')
def productlist():
    if session['loggedin'] == True:
        products = []
        sql = "SELECT * FROM Products WHERE HOLDERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, session['name'])
        ibm_db.execute(prep_stmt)
        dictionary = ibm_db.fetch_both(prep_stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            products.append(dictionary)
            dictionary = ibm_db.fetch_both(prep_stmt)

        if products:
            return render_template("dashboard/productlist.html", products=products, session=session)
        else:
            return render_template("dashboard/productlist.html")
    else:
        return redirect(url_for('home'))


@app.route('/contactsupport')
def contactsupport():
    if session['loggedin'] == True:
        return render_template('dashboard/contactsupport.html')
    else:
        return redirect(url_for('home'))


@app.route('/contactsup', methods=['POST', 'GET'])
def contactsup():
    if request.method == 'POST':
        name = request.form['name']
        mobileno = request.form['mobileno']
        emailid = request.form['emailid']
        query = request.form['query']

        html = "<h1>Query from, </h1><br/><b>Name: </b>"+name+"<br/><b>Email ID: </b>" + \
            emailid+"<br/><b>Contact no: </b>"+mobileno + \
            "<br/><b>Query: </b><b>"+query+"</b>"

        # Set up the email addresses and password. Please replace below with your email address and password
        email_from = 'jjishnu6@gmail.com'
        epassword = 'cwnttdcvtdkaudau'
        email_to = emailid

        # Generate today's date to be included in the email Subject
        date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'Query email - {date_str}'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))
        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, epassword)
            server.sendmail(email_from, email_to, email_string)
        return render_template('dashboard/contactsupport.html', msg="We have mailed your query to our Support team! Soon they will reach you.")


@app.route('/feedback')
def feedback():
    if session['loggedin'] == True:
        return render_template('dashboard/feedback.html')
    else:
        return redirect(url_for('home'))


@app.route('/feedbackadd', methods=['POST', 'GET'])
def feedbackadd():
    if request.method == 'POST':
        interface = request.form['interface']
        availability = request.form['availability']
        userfriendly = request.form['userfriendly']
        chatbot = request.form['chatbot']
        suggest = request.form['suggest']

        sql = "SELECT * FROM Feedback WHERE NAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['name'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('dashboard/feedback.html', msg="Your feedback was submitted already.")
        else:
            ins_sql = "INSERT INTO Feedback (interface,availability,userfriendly,chatbot,suggest,name) VALUES (?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, ins_sql)
            ibm_db.bind_param(prep_stmt, 1, interface)
            ibm_db.bind_param(prep_stmt, 2, availability)
            ibm_db.bind_param(prep_stmt, 3, userfriendly)
            ibm_db.bind_param(prep_stmt, 4, chatbot)
            ibm_db.bind_param(prep_stmt, 5, suggest)
            ibm_db.bind_param(prep_stmt, 6, session['name'])
            ibm_db.execute(prep_stmt)

            return render_template('dashboard/feedback.html', msg="Your feedback was submitted.")


@app.route('/logout')
def logout():
    session['loggedin'] = False
    session.pop('id', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('home'))


@app.route('/list')
def list():
    users = []
    sql = "SELECT * FROM Users"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        # print ("The Name is : ",  dictionary)
        users.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if users:
        return render_template("list.html", users=users, session=session)

    return "No users..."
