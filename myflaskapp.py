from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/radiscool'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database = SQLAlchemy(app)

class Recettes(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    titre = database.Column(database.String(100), nullable = False)
    étapes = database.Column(database.String(100), nullable = False)

    def __init__(self, id, titre, étapes):
        self.id = id
        self.titre = titre
        self.étapes = étapes

class Ingrédients(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    quantité = database.Column(database.String(100), nullable = False)
    unité = database.Column(database.String(100), nullable = False)
    ingrédient = database.Column(database.String(100), nullable = False)

    def __init__(self, quantité, unité, ingrédient):
        self.quantité = quantité
        self.unité = unité
        self.ingrédient = ingrédient
    
    def to_dict(self):
         return {
              'id': self.id,
              'quantité': self.quantité,
              'unité': self.unité,
              'ingrédient': self.ingrédient
         }

class Steps(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    recette_id = database.Column(database.Integer, database.ForeignKey('recettes.id'), nullable=False)
    step_text = database.Column(database.String(100), nullable = False)
    step_order = database.Column(database.Integer, nullable = False)

    def __init__(self, recette_id, step_text, step_order):
        self.recette_id = recette_id
        self.step_text = step_text
        self.step_order = step_order
    
    def to_dict(self):
         return {
              'id': self.id,
              'step_text': self.step_text,
              'step_order': self.step_order
         }

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

            my_data = Recettes(titre, étapes)
            database.session.add(my_data)
            database.session.commit()

            return redirect(url_for('recipes'))

@app.route("/addingredient", methods = ['POST', 'GET'],)
def addingredient():
    if request.method == 'POST':
            quantité = request.form['quantité']
            unité = request.form['unité']
            ingrédient = request.form['ingrédient']

            my_list_of_ingredients= Ingrédients(quantité, unité, ingrédient)
            database.session.add(my_list_of_ingredients)
            database.session.commit()

            return redirect(url_for('enternewrecipe'))
    
@app.route("/viewingredients")
def viewingredients():
     data_ingredients = Ingrédients.query.all()
     data_ingredients_list = [ingredient.to_dict() for ingredient in data_ingredients]
     return jsonify(data_ingredients_list)

@app.route("/addstep", methods = ['POST', 'GET'], )
def addstep():
    recette_id = request.form.get('recette_id', type=int)
    step_text = request.form.get('step_text')
    if step_text:
        last_step = Steps.query.filter_by(recette_id=recette_id).order_by(Steps.step_order.desc()).first()
        new_step_order = last_step.step_order + 1 if last_step else 1
        
        new_step = Steps(recette_id=recette_id, step_text=step_text, step_order=new_step_order)
        database.session.add(new_step)
        database.session.commit()
        flash('Step added successfully!', 'success')
    else:
        flash('Step text is required.', 'error')
    return redirect(url_for('enternewrecipe'))
    
@app.route("/viewsteps")
def viewsteps():
     data_steps = Steps.query.all()
     data_steps_list = [step.to_dict() for step in data_steps]
     return jsonify(data_steps_list)

@app.route("/recipes")
def recipes():
    all_data = Recettes.query.all()
    return render_template('recipes.html', recipes = all_data)

@app.route("/login")
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
