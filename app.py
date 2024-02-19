from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/recettes")
def recettes():
    return render_template('recettes.html')

@app.route("/login")
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
