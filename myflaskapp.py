from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/recipes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database = SQLAlchemy(app)

class Data(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    titre = database.Column(database.String(100))
    étapes = database.Column(database.String(100))

    def __init__(self,titre, étapes):
        self.titre = titre
        self.étapes = étapes

class Ingrédients(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    quantité = database.Column(database.String(100))
    unité = database.Column(database.String(100))
    ingrédient = database.Column(database.String(100))

    def __init__(self, quantité, unité, ingrédient):
        self.quantité = quantité
        self.unité = unité
        self.ingrédient = ingrédient

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/enternewrecipe")
def enternewrecipe():
    return render_template('recipe_example.html')

@app.route("/addrecipe", methods = ['POST', 'GET'])
def addrecipe():
    if request.method == 'POST':
            titre = request.form['titre']
            étapes = request.form['étapes']

            my_data = Data(titre, étapes)
            database.session.add(my_data)
            database.session.commit()

            return redirect(url_for('recipes'))

@app.route("/addingredient", methods = ['POST'])
def addingredient():
    if request.method == 'POST':
            quantité = request.form['quantité']
            unité = request.form['unité']
            ingrédient = request.form['ingrédient']

            my_list_of_ingredients= Ingrédients(quantité, unité, ingrédient)
            database.session.add(my_list_of_ingredients)
            database.session.commit()

            return redirect(url_for('enternewrecipe'))





@app.route("/recipes")
def recipes():
    all_data = Data.query.all()
    return render_template('recipes.html', recipes = all_data)

@app.route("/login")
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
