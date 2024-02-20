from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/enternewrecipe")
def enternewrecipe():
    return render_template('recipe_example.html')

@app.route("/addrecipe", methods = ['POST', 'GET'])
def addrecipe():
    if request.method == 'POST':
        try:
            titre = request.form['titre']
            ingrédients = request.form['ingrédients']
            étapes = request.form['étapes']

            with sqlite3.connect('recettes.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO recettes (titre, ingrédients, étapes) VALUES(?,?,?)", (titre, ingrédients, étapes))

                con.commit()
                msg = "Recette ajoutée sur Radiscool, merci!"
        except:
            con.rollback()
            msg = "Erreur"

        finally:
            con.close()
            return render_template('result.html', msg=msg)

@app.route("/recipes")
def recipes():
    con = sqlite3.connect("recettes.db")
    con.row_factory= sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM recettes")

    rows = cur.fetchall()
    con.close()
    return render_template('recipes.html', rows=rows)

@app.route("/login")
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
