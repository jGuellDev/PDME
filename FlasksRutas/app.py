from flask import Flask, render_template, request
from formulario import formEstudiante
import os


app = Flask(__name__)
app.secret_key= os.urandom(24)


@app.route("/", methods = ["get"])
def home():
    return "Hola"


@app.route("/estudiantes")
def estudiante():
    formulario = formEstudiante()
    return render_template("estudiantes.html", formulario=formulario)



######
if __name__ == '__main__':
    app.run(port=8000, debug=True)