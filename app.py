from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from database.database import db_connection

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

'''The login page is the main page where user will login'''
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get("psw")

        con = db_connection()
        cursor = con.cursor()
        cursor.execute("SElECT * from userData")
        li = []
        for i in cursor:
            li.clear()
            li.append(i)
            name = li[0][1] + " " + li[0][2]
            name = name.upper()
            if username == li[0][0] and password == li[0][-1]:
                session['usernamelogin'] = li[0][0]
                session['namelogin'] = name
                session['emaillogin'] = li[0][3]
                con.close()
                return render_template('menu.html', username=session.get('usernamelogin'),
                                       namelogin=session.get('namelogin'), email=session.get('emaillogin'))
        else:
            return render_template('login.html', error=0)

    return render_template("login.html")

'''The contact page has some information releated to restaurant where user can contact to 
   restaurant management'''
@app.route('/contact')
def contact():
    return render_template('contact.html')

'''The signup page is the page where user can create account for book the table'''
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        contactnumber = request.form.get('contactnumber')
        nationality = request.form.get('nationality')
        password = request.form.get('password')

        con = db_connection()
        cursor = con.cursor()
        insert = "INSERT INTO userData VALUES(?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert, (username, firstname, lastname, email, contactnumber, nationality, password))
        con.commit()
        con.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

'''The adminlogin page where admin can login and see the information about the booked table user'''
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('psw')

        con = db_connection()
        cursor = con.cursor()
        cursor.execute("select * from admin")
        li = []
        for i in cursor:
            li.append(i)
        con.close()
        if username == li[0][0] and password == li[0][1]:
            con = db_connection()
            cursor = con.cursor()
            cursor.execute('select * from tableData')
            cursor1 = con.cursor()
            commonlist = []
            for i in cursor:
                if i[-1] is not None:
                    cursor1.execute('select * from userData')
                    for j in cursor1:
                        if i[-1] == j[0]:
                            commonlist.append((j[1],) + (j[2],) + (j[4],) + i)
            size = len(commonlist)
            return render_template('bookingstatus.html', l=commonlist, size=size)
        else:
            return render_template('adminlogin.html', error="User not found")
    return render_template('adminlogin.html')

'''Some information about the restaurant'''
@app.route('/about')
def about():
    return render_template('about.html')

'''This is the feature where user can change the password of already created account'''
@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        username = request.form.get('username')
        new = request.form.get('newpassword')
        confirm = request.form.get('confirmpassword')
        con = db_connection()
        cursor = con.cursor()
        cursor.execute('select * from userData')
        error = "username is not match"
        for i in cursor:
            if i[0] == username:
                error = "Password are not match"
                if new == confirm:
                    cursor.execute("update userData set password=? where username=?", (new, username))
                    con.commit()
                    con.close()
                    return render_template('forgotpassword.html', error="Changed")
                    break
        else:
            con.close()
            return render_template('forgotpassword.html', error=error)
    return render_template('forgotpassword.html')

'''The main menu page where user can check the availability of table for booking'''
@app.route('/menu', methods=['GET', 'POST'])
def checkAvailability():
    if request.method == 'POST':
        session["numberofpeople"] = request.form.get('membercount')
        session["date"] = request.form.get('date')
        session['visitingtime'] = request.form.get('visitingtime')
        con = db_connection()
        cursor = con.cursor()
        cursor.execute("select * from tableData")
        pop = "SORRY Table is not available"
        li = []
        for i in cursor:
            if i[-1] is None and i[1] is None:
                li.append(i[0])
            if session.get('usernamelogin') == i[-1]:
                tablenumber = i[0]
                datebook = i[2]
                timebook = i[3]
                con.close()
                return render_template('menu.html', booked=session.get('namelogin'), tablenumber=tablenumber,
                                       datebook=datebook, timebook=timebook, username=session.get('usernamelogin'),
                                       namelogin=session.get('namelogin'), email=session.get('emaillogin'))
        con.close()
        return render_template('menu.html', list=li, pop=pop, username=session.get('usernamelogin'),
                               namelogin=session.get('namelogin'), email=session.get('emaillogin'))
    return render_template('login.html')

'''In this where user can book the table'''
@app.route('/tablebook', methods=['GET', 'POST'])
def booktable():
    if request.method == 'POST':
        tablename = request.form.get('tablename')
        con = db_connection()
        cursor = con.cursor()
        cursor.execute('select * from tableData')
        for i in cursor:
            if i[0] == tablename:
                update = "update tableData set numberofpeople=?, date=?, visittime=?, username=? where tablename=?"
                n1 = session.get('numberofpeople')
                n2 = session.get('date')
                n3 = session.get('visitingtime')
                n4 = session.get('usernamelogin')
                cursor.execute(update, (n1, n2, n3, n4, tablename))
                con.commit()
                con.close()
                session.clear()
                return render_template('tablebook.html')
    return render_template('menu.html')

'''Here user simply logout from the main menu page'''
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

'''Whenever admin delete the booked table this function will call'''
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        tablename = request.form.get('deletion')
        con = db_connection()
        cursor = con.cursor()
        cursor1 = con.cursor()
        cursor.execute('select * from tableData')
        cursor1.execute('select * from userData')
        for i in cursor:
            if tablename == i[0]:
                username = i[-1]
                update = "update tableData set numberofpeople=?, date=?, visittime=?, username=? where tablename=?"
                n1 = None
                n2 = None
                n3 = None
                n4 = None
                cursor.execute(update, (n1, n2, n3, n4, tablename))
                con.commit()
                deletedata = 'delete from userData where username=?'
                cursor1.execute(deletedata, (username,))
                con.commit()
                break
        con.close()
        return render_template('login.html')

    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
