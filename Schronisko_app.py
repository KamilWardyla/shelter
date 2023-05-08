from flask import Flask, request, render_template, g, flash, redirect, url_for, abort

import sqlite3

DATABASE = '/path/to/database.db'
app = Flask(__name__)
app.secret_key = "TjWnZq4t7w!z%C*F"
app_info = {
    "db_file": "database/schronisko.db"
}
"""
create table animals(id integer primary key autoincrement, name varchar(35), category varchar (40), race varchar(50), 
description text, admisson_date date not null default(date()));
"""


def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/add", methods=['GET', 'POST'])
def add_animal():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        race = request.form['race']
        description = request.form['description']

        if not name:
            flash('Imię jest wymagane')
        elif not category:
            flash('Kategoria jest wymagana')
        elif not race:
            flash('Rasa jest wymagana')
        else:
            db = get_db()
            sql_command = 'insert into animals(name, category, race, description) values (?,?,?,?)'
            db.execute(sql_command, [name, category, race, description])
            db.commit()
            db.close()
            return redirect(url_for("home"))
    return render_template("add_form.html")


@app.route('/animals')
def get_animals():
    db = get_db()
    sql_command = 'select id, name, category, race, description from animals;'
    cur = db.execute(sql_command)
    animals = cur.fetchall()
    return render_template('all_animals.html', animals=animals)


@app.route('/animal/<int:id>')
def get_animal(id):
    db = get_db()
    if request.method == "GET":
        sql_command = 'SELECT id,name, category, race, admisson_date, description from animals where id = ?'
        cur = db.execute(sql_command, [id])
        animal = cur.fetchone()
        if not animal:
            flash("Nie ma takiego zwierzecia")
            return redirect(url_for('home'))
        return render_template("animal.html", animal=animal)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == "GET":
        sql_command = 'SELECT id,name, category, race, description from animals where id = ?;'
        cur = db.execute(sql_command, [id])
        animal = cur.fetchone()

        if animal == None:
            flash("Nie ma takiego zwierzecia")
            return redirect(url_for('home'))
        else:
            return render_template('edit.html', animal=animal)

    if request.method == "POST":
        name = request.form['name']
        category = request.form['category']
        race = request.form['race']
        description = request.form['description']
        if not name:
            flash('Imię jest wymagane')
        elif not category:
            flash('Kategoria jest wymagana')
        elif not race:
            flash('Rasa jest wymagana')
        else:
            db = get_db()
            sql_command = ('UPDATE animals SET name = ?, category = ?, race = ?, description = ? where id = ?')
            db.execute(sql_command, [name, category, race, description, id])
            db.commit()
            db.close()
            return redirect(url_for("home"))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    db = get_db()
    if request.method == "GET":
        return render_template('delete.html', id=id)
    if request.method == "POST":
        sql_command = 'delete from animals where id = ?'
        db.execute(sql_command, [id])
        db.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
