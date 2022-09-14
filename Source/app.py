#from asyncore import loop
#from distutils.util import execute
#import email
import os
#import io
#import sys
from flask import send_file
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_bcrypt import Bcrypt
from flask_session import Session
from models import AccountOpenningRecord, Base, Account, Current, Customer, Saving, Transaction, TransferRecord, Card, Loan, LoanAuthorizationRecord, HomeLoan, StudentLoan
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime
from datetime import date
from flask_cors import CORS
#import xlwt
#from fpdf import FPDF
import random

app = Flask(__name__)
#bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)
engine = create_engine('postgresql://postgres:sys@localhost/Project1')
Base.metadata.bind = engine
CORS(app)
db = scoped_session(sessionmaker(bind=engine))

username = None;
password  =None



# MAIN
@app.route('/')
@app.route("/dashboard")
def dashboard():
    return render_template("home.html", home=True)

############################### LOGIN #############################
############################### Employee LOGIN #############################
'''MANAGER FUNCTIONALITY BELOW'''
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        usern = request.form.get("username")#.upper()
        passw = str(request.form.get("password"))#.encode('utf-8')
        result = db.execute("SELECT * FROM employee WHERE email = :u", {"u": usern}).fetchone()
        if result is not None:
            if str(result['e_id']) == passw:
            #if bcrypt.check_password_hash(result['password'], passw) is True:
                session['user'] = result.e_id
                session['namet'] = result.f_name
                session['usert'] = result.designation.lower()
                flash(f"{result.f_name.capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        flash("Sorry, Username or password not match.","danger")
    return render_template("login.html", login=True)
# route for 404 error
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html") 
#############################################################################################
# Logout 
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
#############################################################################################
# creating a customer
@app.route("/addcustomer" , methods=["GET", "POST"])
def addcustomer():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_id = int(request.form.get("c_id"))
            first_name = request.form.get("f_name")
            last_name = request.form.get("l_name")
            email = request.form.get("email")
            # birth_date = request.form.get("birthdate") delayed until I work out how to deal with dates
            ph_no = int(request.form.get("ph_no"))
            street = request.form.get("street")
            postcode = int(request.form.get("postcode"))

            result = db.execute("SELECT * from Customer WHERE c_id = :c", {"c": cust_id}).fetchone()
            if result is None :
                result = db.query(Customer).count()
                query = Customer(c_id=cust_id,f_name=first_name,l_name=last_name, email=email, ph_no=ph_no,street=street,postcode=postcode)
                db.add(query)
                db.commit()
                if query.c_id is None:
                    flash("Data is not inserted! Check your input.","danger")
                else:
                    flash(f"Customer {query.f_name} is created with customer ID : {query.c_id}.","success")
                    return redirect(url_for('viewcustomer'))
            flash(f'SSN id : {cust_id} is already present in database.','warning')
        
    return render_template('addcustomer.html', addcustomer=True)
#############################################################################################

@app.route("/viewcustomer/<c_id>")
@app.route("/viewcustomer" , methods=["GET", "POST"])
def viewcustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_id = request.form.get("c_id")
            flash(f"{cust_id}")
            data = db.execute("SELECT * from Customer WHERE c_id = :c", {"c": cust_id}).fetchone()
            if data is not None:
                return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
            flash("Customer not found! Please,Check your input.", 'danger')
            if cust_id is not None:
                data = db.execute("SELECT * from Customer WHERE c_id = :c", {"c": cust_id}).fetchone()
                if data is not None:
                    return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
                flash("Customer not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))

    return render_template('viewcustomer.html', viewcustomer=True)
#############################################################################################

@app.route('/editcustomer')
@app.route('/editcustomer/<c_id>', methods=["GET", "POST"])
def editcustomer(c_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if c_id is not None:
            if request.method != "POST":
                c_id = int(c_id)
                flash(f"{c_id}")
                data = db.execute("SELECT * from customer WHERE c_id = :c", {"c": c_id}).fetchone()
                if data is not None:
                    return render_template('editcustomer.html', editcustomer=True, data=data)
                else:
                    flash('Customer is not present in database.','warning')
            else:
                c_id = int(c_id)
                first_name = request.form.get("f_name")
                last_name = request.form.get("l_name")
                email = request.form.get("email")               
                ph_no = request.form.get("ph_no")
                street = request.form.get("street")
                result = db.execute("SELECT * from Customer WHERE c_id = :c", {"c": c_id}).fetchone()
                if result is not None:
                    result = db.execute("UPDATE Customer SET f_name = :n , l_name = :l , email = :e, ph_no = :p, street = :s WHERE c_id = :a", {"n": first_name,"l": last_name,"e": email, "p": ph_no, "s": street, "a": c_id})
                    db.commit()
                    flash(f"Customer data are updated successfully.","success")
                else:
                    flash('Invalid customer Id. Please, check customer Id.','warning')
    return redirect(url_for('viewcustomer'))
#############################################################################################

@app.route("/addaccount" , methods=["GET", "POST"])
def addaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_id = int(request.form.get("cust_id"))
            acc_type = request.form.get("acc_type")
            amount= float(request.form.get("amount"))
            password = random.randint(1111,9999)
            result = db.execute("SELECT * from Customer WHERE c_id = :c", {"c": cust_id}).fetchone()
            if result is not None :
                result = db.execute("SELECT * from Account WHERE c_id = :c and acc_type = :at", {"c": cust_id, "at": acc_type}).fetchone()
                if result is None:
                    result = db.query(Account).count()
                    acc_no = db.execute("SELECT account_no+1 as acc FROM ACCOUNT ORDER BY account_no DESC LIMIT 1").fetchone()
                    query = Account(account_no=acc_no.acc,acc_type=acc_type,balance=amount,c_id=cust_id,acc_password=password, interest_rate=6.0)
                    db.add(query)
                    db.commit()
                    query2 = AccountOpenningRecord(c_id=cust_id,account_no=acc_no.acc,e_id=session["user"], authorization_status='PROCESSED', openning_date=datetime.datetime.now())
                    db.add(query2)
                    db.commit()
                    
                    if acc_type=="SAVING":
                        query2 = db.execute("INSERT INTO Savings VALUES (:m,:a)", {"m":100,"a":acc_no.acc})
                    elif acc_type=="CURRENT":
                        query2 = db.execute("INSERT INTO Current VALUES (:m,:a)", {"m":10000000,"a":acc_no.acc})
                    db.commit()
                    if query.account_no is None:
                        flash("Data is not inserted! Check you input.","danger")
                    else:
                        flash(f"{query.acc_type} account is created with customer ID : {query.account_no}.","success")
                        return redirect(url_for('dashboard'))
                else:
                    flash(f'Customer with id : {cust_id} has already {acc_type} account.','warning')
            else:
                flash(f'Customer with id : {cust_id} is not present in database.','warning')

    return render_template('addaccount.html', addaccount=True)
#############################################################################################
@app.route("/viewaccount" , methods=["GET", "POST"])
def viewaccount(account_no=None):
    if 'user' not in session:
        return redirect(url_for('login'))        
    if session['usert']=="executive" or session['usert']=="teller" or session['usert']=="cashier":
        if request.method == "POST":
            account_no = request.form.get("account_no")
            c_id = request.form.get("c_id")
            data = db.execute("SELECT a.c_id as c_id, a.account_no as account_no, a.balance as balance, a.acc_type as acc_type, o.authorization_status as authorization_status from Account a, Account_openning_record o WHERE a.c_id = :c AND a.account_no=o.account_no", {"c": c_id}).fetchall()
            if data:
                return render_template('viewaccount.html', viewaccount=True, data=data)
            
            flash("Account not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('viewaccount.html', viewaccount=True)
#############################################################################################
@app.route('/activateaccount')
@app.route('/activateaccount/<account_no>')
def activateaccount(account_no=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if account_no is not None:
            account_no = int(account_no)
            max_limit = 10000000
            min_limit = 100
            result = db.execute("SELECT * from Account_openning_record WHERE account_no = :a and authorization_status = 'REMOVED'", {"a": account_no}).fetchone()
            if result is not None :
                query = db.execute("UPDATE Account_openning_record SET authorization_status='PROCESSED' WHERE account_no = :a", {"a": account_no})
                db.commit()

                sample = db.execute("SELECT acc_type FROM account WHERE account_no=:a", {"a":account_no}).fetchone()
                if sample.acc_type=="SAVING":
                    query2 = db.execute("INSERT INTO savings VALUES(:m,:a)", {"m":max_limit,"a": account_no})
                elif sample.acc_type=="CURRENT":
                    query2 = db.execute("INSERT INTO current VALUES(:m,:a)", {"m":min_limit,"a": account_no})
                db.commit()

                flash(f"Account is activated.","success")
                return redirect(url_for('dashboard'))
            flash(f'Account with id : {account_no} is already activated or not present in database.','warning')
    return redirect(url_for('viewaccount'))

@app.route("/delaccount" , methods=["GET", "POST"])
def delaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            account_no = int(request.form.get("account_no"))
            result = db.execute("SELECT * from account_openning_record WHERE account_no = :a and authorization_status='PROCESSED'", {"a": account_no}).fetchone()
            if result is not None :
                date = datetime.datetime.now()
                query = db.execute("UPDATE account_openning_record SET authorization_status='REMOVED' WHERE account_no = :a;", {"a": account_no})
                db.commit()
                
                sample = db.execute("SELECT acc_type FROM account WHERE account_no=:a", {"a":account_no}).fetchone()
                if sample.acc_type=="SAVING":
                    query2 = db.execute("DELETE FROM savings WHERE account_no=:a", {"a": account_no})
                elif sample.acc_type=="CURRENT":
                    query2 = db.execute("DELETE FROM current WHERE account_no=:a", {"a": account_no})
                db.commit()
                flash(f"Customer account is Deactivated Successfully.","success")
                return redirect(url_for('dashboard'))
            flash(f'Account with id : {account_no} is already deactivate or account not found.','warning')
    return render_template('delaccount.html', delaccount=True)
#############################################################################################

@app.route("/viewaccountstatus" , methods=["GET", "POST"])
def viewaccountstatus():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        data = db.execute("select A.c_id, A.account_no, A.acc_type, AO.authorization_status from Account A INNER JOIN Account_openning_record AO ON A.account_no=AO.account_no").fetchall()
        if data:
            return render_template('viewaccountstatus.html', viewaccountstatus=True, data=data)
        else:
            flash("Account are not found!", 'danger')
    return render_template('viewAccounttatus.html', viewAccounttatus=True)
#############################################################################################

def addYears(d, years):
    try:
#Return same day of the current year        
        return d.replace(year = d.year + years)
    except ValueError:
#If not same day, it will return other, i.e.  February 29 to March 1 etc.        
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


@app.route("/addcard" , methods=["GET", "POST"])
def addcard():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            account_no = int(request.form.get("account_no"))
            issue_date = datetime.datetime.now()
            card_type = request.form.get("card_type")

            if card_type=="Silver":
                exp_date = addYears(issue_date, 3)
            elif card_type=="Gold":
                exp_date = addYears(issue_date, 5)
            elif card_type=="Platinum":
                exp_date = addYears(issue_date, 7)
            elif card_type=="Master":
                exp_date = addYears(issue_date, 10)

            loop = True
            while loop:
                card_no = random.randint(11111111,99999999)
                cond = db.execute("SELECT * from Card_ WHERE card_no = :c", {"c": card_no}).fetchone()
                if cond is None:
                    loop=False
            cvv = random.randint(100, 999)
            query = Card(card_no=card_no,cvv_code=cvv,exp_date=exp_date,issue_date=issue_date,card_type=card_type,account_no=account_no)
            db.add(query)
            db.commit()
            if query.card_no is None:
                flash("Data is not inserted! Check your input.","danger")
            else:
                flash(f"Card {query.card_no} is created","success")
                return redirect(url_for('dashboard'))
            flash(f'Card : {card_no} is already created.',"warning")
        
    return render_template('addcard.html', addcard=True)
#############################################################################################
#############################################################################################
'''CASHIER AND TELLER FUNCTIONALITY BELOW'''
# issue cards to specific accounts. Use views brotha!!
@app.route('/deposit',methods=['GET','POST'])
@app.route('/deposit/<account_no>',methods=['GET','POST'])
def deposit(account_no=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="cashier" or session['usert']=="teller":
        if account_no is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                amount = request.form.get("amount")
                data = db.execute("select * from account_link where account_no = :a and authorization_status='PROCESSED'",{"a":account_no}).fetchone()
                if data is not None:
                    balance = int(amount) + int(data.balance)
                    query = db.execute("UPDATE Account SET balance= :b WHERE account_no = :a", {"b":balance,"a": data.account_no})
                    db.commit()
                    flash(f"{amount} Amount deposited into account: {data.account_no} successfully.",'success')
                    acc_no = db.execute("SELECT COALESCE(trans_id+1, 1) as id FROM transactions ORDER BY trans_id DESC LIMIT 1").fetchone()
                    temp = Transaction(account_no=data.account_no,status_='PROCESSED',trans_id=acc_no.id,trans_date=datetime.datetime.now(),trans_time=datetime.datetime.now(),Credit=amount)
                    db.add(temp)
                    db.commit()
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                data = db.execute("select * from account_link where account_no = :a",{"a":account_no}).fetchone()
                if data is not None:
                    return render_template('deposit.html', deposit=True, data=data)
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('dashboard'))

# Code for withdraw amount 
@app.route('/withdraw',methods=['GET','POST'])
@app.route('/withdraw/<account_no>',methods=['GET','POST'])
def withdraw(account_no=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="cashier" or session['usert']=="teller":
        if account_no is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                amount = request.form.get("amount")
                data = db.execute("select * from account_link where account_no = :a and authorization_status='PROCESSED'",{"a":account_no}).fetchone()
                if data is not None:
                    if int(data.balance)>=int(amount):
                        balance =  int(data.balance)-int(amount)
                        query = db.execute("UPDATE Account SET balance= :b WHERE account_no = :a", {"b":balance,"a": data.account_no})
                        db.commit()
                        flash(f"{amount} Amount withdrawn from account: {data.account_no} successfully.",'success')
                        acc_no = db.execute("SELECT COALESCE(trans_id+1, 1) as id FROM transactions ORDER BY trans_id DESC LIMIT 1").fetchone()
                        temp = Transaction(account_no=data.account_no,status_='PROCESSED',trans_id=acc_no.id,trans_date=datetime.datetime.now(),trans_time=datetime.datetime.now(), Debit=amount)
                        db.add(temp)
                        db.commit()
                    else:
                        flash(f"Account doesn't have sufficient Balance.",'success')
                        return redirect(url_for('viewaccount'))
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                data = db.execute("select * from account_link where account_no = :a",{"a":account_no}).fetchone()
                if data is not None:
                    return render_template('withdraw.html', deposit=True, data=data)
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('dashboard'))

@app.route("/home_loan" , methods=['GET', 'POST'])
def home_loan():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="cashier" or session['usert']=="teller":
        if request.method == "POST":
            c_id = int(request.form.get("c_id"))
            amount = float(request.form.get("amount"))
            payment_mode = request.form.get("payment_mode")
            interest_rate = int(request.form.get("interest_rate"))
            loan_period = int(request.form.get("loan_period"))
            street = request.form.get("street")
            postcode = int(request.form.get("postcode"))

            loan_id = db.execute("SELECT COALESCE(loan_id+1,1) as l_id FROM loan ORDER BY loan_id DESC LIMIT 1").fetchone()
            loan_date = datetime.datetime.now()
            loan_type = "HOME"
            authorized = True
            authorization_status = "PROCESSED"
            e_id = session['user']

            # query = Loan(loan_id=loan_id.l_id,amount=amount,payment_mode=payment_mode,interest_rate=interest_rate,loan_period=loan_period,loan_date=loan_date,loan_type=loan_type,authorized=authorized)
            # db.add(query)
            # query2 = HomeLoan(loan_id=loan_id.l_id,street=street,postcode=postcode)
            # db.add(query2)
            # query3 = LoanAuthorizationRecord(c_id=c_id,loan_id=loan_id.l_id,e_id=e_id,authorization_status=authorization_status)
            # db.add(query3)
            result = db.execute("INSERT INTO loan VALUES (:l,:a,:p,:i,:lp,:ld,:lt,:au)",{"l":loan_id.l_id,"a":amount,"p":payment_mode,"i":interest_rate,"lp":loan_period,"ld":loan_date,"lt":loan_type,"au":authorized})
            db.commit()

            result2 = db.execute("INSERT INTO Home_Loan VALUES (:l,:s,:p)",{"l":loan_id.l_id,"s":postcode,"p":street})
            db.commit()

            result3 = db.execute("INSERT INTO Loan_Authorization_Record VALUES (:c,:l,:e,:a)",{"c":c_id,"l":loan_id.l_id,"e":e_id,"a":authorization_status})
            db.commit()
            flash(f"Loan created","success")
            return redirect(url_for('home_loan'))
    return render_template('home_loan.html', home_loan=True)
#############################################################################################
@app.route("/student_loan" , methods=['GET', 'POST'])
def student_loan():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="cashier" or session['usert']=="teller":
        if request.method == "POST":
            c_id = int(request.form.get("c_id"))
            amount = float(request.form.get("amount"))
            payment_mode = request.form.get("payment_mode")
            interest_rate = int(request.form.get("interest_rate"))
            loan_period = int(request.form.get("loan_period"))
            loan_purpose = request.form.get("loan_purpose")

            loan_id = db.execute("SELECT COALESCE(loan_id+1,1) as l_id FROM loan ORDER BY loan_id DESC LIMIT 1").fetchone()
            loan_date = datetime.datetime.now()
            loan_type = "STUDENT"
            authorized = True
            authorization_status = "PROCESSED"
            e_id = session['user']

            result = db.execute("INSERT INTO loan VALUES (:l,:a,:p,:i,:lp,:ld,:lt,:au)",{"l":loan_id.l_id,"a":amount,"p":payment_mode,"i":interest_rate,"lp":loan_period,"ld":loan_date,"lt":loan_type,"au":authorized})
            db.commit()

            result2 = db.execute("INSERT INTO Student_Loan VALUES (:l,:lp)",{"lp":loan_id.l_id,"l":loan_purpose})
            db.commit()

            result3 = db.execute("INSERT INTO Loan_Authorization_Record VALUES (:c,:l,:e,:a)",{"c":c_id,"l":loan_id.l_id,"e":e_id,"a":authorization_status})
            db.commit()
            flash(f"Loan created","success")
            return redirect(url_for('student_loan'))
    return render_template('student_loan.html', student_loan=True)
#############################################################################################
#############################################################################################


'''CUSTOMER FUNCTIONALITY BELOW'''
############################### Customer LOGIN #############################
current_c_id = None
@app.route("/customerlogin", methods=["GET", "POST"])
def customer_login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        usern = request.form.get("username")#.upper()
        password = request.form.get("password")
        passw = str(password)#.encode('utf-8')
        result = db.execute("SELECT * FROM account_link WHERE account_no = :u", {"u": usern}).fetchone()
        if result is not None:
            if result.authorization_status!='REMOVED':
                if str(result['acc_password']) == passw:
                    session['user'] = result.account_no
                    session['namet'] = result.f_name
                    session['usert'] = 'customer'
                    session['userid'] = result.c_id
                    current_c_id = int(password)
                    flash(f"{result.f_name.capitalize()}, you are successfully logged in!", "success")
                    return redirect(url_for('dashboard'))
            else:
                flash("Account not active, hence cannot be logged in.","danger")
        else:
            flash("Sorry, Username or password not match.","danger")
    return render_template("customer_login.html", customer_login=True)
#############################################################################################

# view own account details

@app.route("/viewcustomeraccount/<account_no>" , methods=["GET", "POST"])
@app.route("/viewcustomeraccount")
def viewcustomeraccount(account_no=None):
    if 'user' not in session:
        return redirect(url_for('customerlogin'))
    if request.method != "POST":
        account_no = session['user']
        data = db.execute("SELECT * from account_link where account_no=:a", {"a": account_no}).fetchone()
        if data:
            return render_template('viewcustomeraccount.html', viewcustomeraccount=True, data=data)
        
        flash("Account not found! Please,Check you input.", "danger")
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('viewcustomeraccount.html', viewcustomeraccount=True)
#############################################################################################
@app.route("/viewcustomercards" , methods=["GET", "POST"])
def viewcustomercards(account_no=None):
    if 'user' not in session:
        return redirect(url_for('customerlogin'))
    if request.method != "POST":
        account_no = session['user']
        data = db.execute("SELECT * from card_ where account_no=:a", {"a": account_no}).fetchall()
        if data:
            return render_template('viewcustomercards.html', viewcustomercards=True, data=data)
        
        flash("Account not found! Please,Check you input.", "danger")
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('viewcustomercards.html', viewcustomercards=True)
##############################################################################################
# Code for transfer amount
@app.route("/transfer/<account_no>",methods=["GET","POST"])
@app.route("/transfer",methods=['GET','POST'])
def transfer(account_no=None):
    account_no = session['user']
    if 'user' not in session:
        return redirect(url_for('customerlogin'))
    if session['usert'] != "customer":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="customer":
        c_id = session['userid']
        if c_id is None:
            return redirect(url_for('dashboard'))
        else:
            if request.method == "POST":
                #src_type = request.form.get("src_type")
                target_account_no = request.form.get("target_account_no")
                amount = int(request.form.get("amount"))
                if account_no != target_account_no:
                    src_data  = db.execute("select * from Account where account_no = :a",{"a":account_no}).fetchone()
                    trg_data  = db.execute("select * from Account where account_no = :b",{"b":target_account_no}).fetchone()
                    data = db.execute("select * from Account where account_no = :a", {"a":account_no}).fetchone()
                    if src_data is not None and trg_data is not None:
                        if src_data.balance > amount:
                            src_balance = src_data.balance - amount
                            trg_balance = trg_data.balance + amount
                            print(src_balance)
                            print(trg_balance)
                            test = db.execute("update Account set balance = :b where account_no = :a",{"b":src_balance,"a":account_no})
                            db.commit()

                            test2 = db.execute("update Account set balance = :c where account_no = :d",{"c":trg_balance,"d":target_account_no})
                            db.commit()

                            acc_no = db.execute("SELECT COALESCE(trans_id+1, 1) as id FROM transactions ORDER BY trans_id DESC LIMIT 1").fetchone()
                            temp = Transaction(account_no=src_data.account_no,status_='PROCESSED',trans_id=acc_no.id,trans_date=datetime.datetime.now(),trans_time=datetime.datetime.now(), Debit=amount)
                            db.add(temp)
                            db.commit()

                            # db.execute("update Account set balance = :b where c_id = :a",{"b":trg_balance,"a":c_id})
                            # db.commit()
                            acc_no = db.execute("SELECT COALESCE(trans_id+1, 1) as id FROM transactions ORDER BY trans_id DESC LIMIT 1").fetchone()
                            #acc_no.id+=1
                            temp = Transaction(account_no=trg_data.account_no,status_='PROCESSED',trans_id=acc_no.id,trans_date=datetime.datetime.now(),trans_time=datetime.datetime.now(), Credit=amount)
                            db.add(temp)
                            db.commit()

                            #acc_no.id-=1
                            temp = TransferRecord(account_no=session['user'], trans_id=acc_no.id, account_no_receiving_funds=trg_data.account_no)
                            db.add(temp)
                            db.commit()

                            flash(f"Amount transfered to {trg_data.account_no} from {src_data.account_no} successfully",'success')
                        else:
                            flash("Insufficient amount to transfer.","danger")
                            
                    else:
                        flash("Account not found","danger")

                else:
                    flash("Can't Transfer amount to same account.","warning")

            else:
                data = db.execute("select * from Account where account_no = :a",{"a":account_no}).fetchall()[0]
                if data:
                    return render_template('transfer.html', data=data)
                else:
                    flash("Data Not found or Invalid Customer ID",'danger')
                    return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route("/statement" , methods=["GET", "POST"])
def statement():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))       
    if session['usert']=="customer":
        if request.method == "POST":
            account_no = session['user']
            number = request.form.get("number")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            data = db.execute("SELECT * FROM transactions WHERE account_no=:a AND DATE(trans_date) >= :s AND DATE(trans_date) <= :e;",{"a":account_no,"s":start_date,"e":end_date}).fetchall()
            if data:
                return render_template('statement.html', statement=True, data=data, account_no=account_no)
            else:
                flash("No Transaction", 'danger')
                return redirect(url_for('dashboard'))
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('statement.html', statement=True)


# # code for generate Statement PDF or Excel file
# @app.route('/pdf_xl_statement/<acc_id>')
# @app.route('/pdf_xl_statement/<acc_id>/<ftype>')
# def pdf_xl_statement(acc_id=None,ftype=None):
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     if session['usert'] == "executive":
#         flash("You don't have access to this page","warning")
#         return redirect(url_for('dashboard'))       
#     if session['usert']=="teller" or session['usert']=="cashier":
#         if acc_id is not None:
#             data = db.execute("SELECT * FROM transactions WHERE acc_id=:a order by time_stamp limit 20;",{"a":acc_id}).fetchall()
#             column_names = ['TransactionId', 'Description', 'Date', 'Amount']
#             if data:
#                 if ftype is None: # Check for provide pdf file as default
#                     pdf = FPDF()
#                     pdf.add_page()
                    
#                     page_width = pdf.w - 2 * pdf.l_margin
                    
#                     # code for setting header
#                     pdf.set_font('Times','B',16.0) 
#                     pdf.cell(page_width, 0.0, "Retail Banking", align='C')
#                     pdf.ln(10)

#                     # code for Showing account id
#                     msg='Account Statment : '+str(acc_id)
#                     pdf.set_font('Times','',12.0) 
#                     pdf.cell(page_width, 0.0, msg, align='C')
#                     pdf.ln(10)

#                     # code for Showing account id
#                     pdf.set_font('Times', 'B', 11)
#                     pdf.ln(1)
                    
#                     th = pdf.font_size
                    
#                     # code for table header
#                     pdf.cell(page_width/5, th, 'Transaction Id')
#                     pdf.cell(page_width/3, th, 'Description')
#                     pdf.cell(page_width/3, th, 'Date')
#                     pdf.cell(page_width/7, th, 'Amont')
#                     pdf.ln(th)

#                     pdf.set_font('Times', '', 11)

#                     # code for table row data
#                     for row in data:
#                         pdf.cell(page_width/5, th, str(row.trans_id))
#                         pdf.cell(page_width/3, th, row.trans_message)
#                         pdf.cell(page_width/3, th, str(row.time_stamp))
#                         pdf.cell(page_width/7, th, str(row.amount))
#                         pdf.ln(th)
                    
#                     pdf.ln(10)

#                     bal = db.execute("SELECT balance FROM Account WHERE acc_id=:a;",{"a":acc_id}).fetchone()
                    
#                     pdf.set_font('Times','',10.0) 
#                     msg='Current Balance : '+str(bal.balance)
#                     pdf.cell(page_width, 0.0, msg, align='C')
#                     pdf.ln(5)

#                     pdf.cell(page_width, 0.0, '-- End of statement --', align='C')
                    
#                     return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'inline;filename=statement.pdf'})
                
#                 elif ftype == 'xl': # Check for bulid and send Excel file for download

#                     output = io.BytesIO()
#                     #create WorkBook object
#                     workbook = xlwt.Workbook()
#                     #add a sheet
#                     sh = workbook.add_sheet('Account statment')

#                     #add headers
#                     sh.write(0, 0, 'Transaction ID')
#                     sh.write(0, 1, 'Description')
#                     sh.write(0, 2, 'Date')
#                     sh.write(0, 3, 'Amount')

#                     # add row data into Excel file
#                     idx = 0
#                     for row in data:
#                         sh.write(idx+1, 0, str(row.trans_id))
#                         sh.write(idx+1, 1, row.trans_message)
#                         sh.write(idx+1, 2, str(row.time_stamp))
#                         sh.write(idx+1, 3, str(row.amount))
#                         idx += 1

#                     workbook.save(output)
#                     output.seek(0)

#                     response = Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=statment.xls"})
#                     return response
#             else:
#                 flash("Invalid account Id",'danger')
#         else:
#             flash("Please, provide account Id",'warning')
#     return redirect(url_for('dashboard'))

# # code for view account statment based on the account id
# # Using number of last transaction
# # or 
# # Using Specified date duration       

# #############################################################################################

# Main
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)