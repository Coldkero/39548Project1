from flask import Flask, render_template, request, session
import sqlite3 as sql
import os
app = Flask(__name__)

conn = sql.connect('users.db')
conn_1 = sql.connect('todolist.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (name TEXT)')
conn_1.execute('CREATE TABLE IF NOT EXISTS tasks (name TEXT, task TEXT, status TEXT)')
conn.close()
conn_1.close()
current_user = ''

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

def globalchange(user):
    global current_user
    current_user = user

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    nm = request.form['username']
    globalchange(nm)
    con = sql.connect("users.db")
    cur = con.cursor()
    cur = con.execute("SELECT * FROM users WHERE name=?", (nm,))
    user = cur.fetchall()    
    if is_empty(user):
        return "No User Exist. Please Create an Account <a href='/'>Return Home</a>"
    else:
        session['logged_in'] = True
    return home()
 
@app.route("/logout")
def logout():
    globalchange('')
    session['logged_in'] = False
    return home()

@app.route('/addrec', methods=['POST','GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['addrec']
            with sql.connect("users.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (name) VALUES (?)", (nm,))
                con.commit()
                msg = "Account has been Created."
        except:
            con.rollback()
            msg = "Error"
        finally:
            con.close()
            return render_template("result.html", msg = msg)

@app.route('/addlist', methods=['POST','GET'])
def addlist(): 
    nm = current_user
    new_entry = request.form['addlist']
    status = "Not Completed"
    if request.method == 'POST':
        try:
            with sql.connect("todolist.db") as conn_1:
                cur = conn_1.cursor()
                cur.execute("INSERT INTO tasks (name, task, status) VALUES (?,?,?)", (nm,new_entry,status))
                conn_1.commit()
        except:
            conn_1.rollback()
        finally:
            conn_1.close()
            return list()

@app.route('/list')
def list():
    nm = current_user
    conn_1 = sql.connect("todolist.db")
    conn_1.row_factory = sql.Row
    curr = conn_1.cursor()
    curr.execute("SELECT * FROM tasks WHERE name=?", (nm,))
    rows = curr.fetchall()
    conn_1.close()
    return render_template("list.html", rows = rows)

@app.route('/complete', methods=['POST','GET'])
def complete():
    nm = current_user
    entry = request.form['complete']
    status = "Completed"
    
    with sql.connect("todolist.db") as conn_1:
        cur = conn_1.cursor()
        cur.execute("UPDATE tasks SET status=? WHERE name=? AND task=?", (status, nm, entry))
        conn_1.commit()
        
    return list()
    
@app.route('/delete', methods=['POST','GET'])
def delete():
    nm = current_user
    entry = request.form['delete']
    status = "Completed"

    with sql.connect("todolist.db") as conn_1:
        cur = conn_1.cursor()
        cur.execute("UPDATE tasks SET status=? WHERE name=? AND task=?", (status, nm, entry))
        cur.execute("DELETE FROM tasks WHERE name=? AND task=?", (nm, entry))
        conn_1.commit()
        
    return list()

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host= '0.0.0.0', port = 5000)