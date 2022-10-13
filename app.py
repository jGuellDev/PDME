from __future__ import with_statement
from distutils.log import error
import email
import hashlib
from ssl import AlertDescription
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_login import login_required 
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import random
import os



app = Flask(__name__) #---> Objeto que se crea con el poder de flasshh
username = ""
app.secret_key = os.urandom(24) # ---> al objeto app, agregale el key


################################################
## LOGICA                                      #
################################################

# CREA ENPOINT DE GET, PARA OBTENER LA PAGINA PARA VISUALIZACION
# DENTRO DEL HTML, EN EL FORM, CREAR EL METODO POST Y EL NOMBRE DEL ENPOINT DEL BACKEND
# CREAR EL METODO DEL BACKEND PARA GESTION DEL FORMULARIO


################################################
## ENDPOINT PARA FORMULARIOS HTML GET          #
################################################


## End point para cargar Formulario Login
@app.route('/', methods=["get"])
def home():
    return render_template("index.html")

## End point para cargar Formulario Registro
@app.route('/reg', methods=["get"])
def registro():
    return render_template("registro.html")

## End point para cargar Formulario Menu
@app.route('/men', methods=["get"])
def menu():
    if 'usuario' in session:
        return render_template("menu.html")
    else:
        return render_template("index.html", error = ["Usuario No Autorizado!"])


## End point para cargar Formulario Cambio de contraseña desde Usuarios logueados
@app.route('/uss', methods=["get"])
def usuario():
    if 'usuario' in session:
        return render_template("usuarios.html")
    else:
        return render_template("index.html", error = ["Usuario No Autorizado!"])


## End point para cargar Formulario Cambio de contraseña desde correo enviado
@app.route('/uss/correo', methods=["get"])
def usuarioCorreo():
    return render_template("usuariosCorreo.html")


## End point para cargar Formulario Mensajes
@app.route('/msg', methods=["get"])
def msg():
    if 'usuario' in session:
        return render_template("mensajes.html")
    else:
        return render_template("index.html", error = ["Usuario No Autorizado!"])


################################################
## ENDPOINT PARA FORMULARIOS HTML POST         #
################################################


## End point para Procesar y Registrar Loguin
@app.route('/procesar/usuario', methods=["post"])
def procesar():


    if 'btnGuardar' in request.form:
        #Captura Los datos del estudiante desde el formulario enviado por el frontend
        email     = request.form["textEmail"]
        passw     = request.form["txtPassword"]
        direccion = request.form["textDireccion"]
        ciudad    = request.form["textCiudad"]
        tipuss    = request.form["textTipoUser"]

        if not email or not passw:
         return "Usuario / Contraseña son rerquerido"

        # clave = hashlib.sha256(passw.encode())
        # passw = clave.hexdigest()
        salt = hex(random.getrandbits(128))[2:]
        clave = generate_password_hash(passw + salt)       
        passw = clave
        

        #CONEXION A LA BASE DE DATOS
        with sqlite3.connect('pdme.db')  as con:
            #Crea un apuntador para manipular la BD
            cur = con.cursor()
            # Consultar si ya existe Usuario
            cur.execute("Select username FROM Login where username=?", [email])
            if cur.fetchone():
                return "Ya existe el Correo!"
            #Ejecuta la sentencia sql para guardar los datos
            cur.execute("Insert Into login (username, password, direccion, ciudad, tipoUsuario, salt) VALUES (?,?,?,?,?,?)", 
            [email, passw, direccion, ciudad, tipuss, salt])
            # Guardar en BD

            con.commit
        return  "Guardado!!"




## End point para Ingreso de Loguin
@app.route("/login", methods=["post"])
def login():
    error = []
    global username
    username = request.form["textEmail"]
    password = request.form["txtPassword"]

    # estado = 'ACT'
    # clave = hashlib.sha256(password.encode())
    # password = clave.hexdigest()

    with sqlite3.connect("pdme.db") as con:
        cur = con.cursor()
        # cur.execute("select 1 from usuario5784 where username = '"+ username + "' and password ='" + password + "'") ---> mala practica sql injection
        datos = cur.execute("select password, salt, username from login where username = ?", [username]).fetchone() #--> devuelve una tupla(valores de una lista que no se pueden modificar)
        #print(datos) ---> Imprime la tupla
        
        if datos:
            session["usuario"] = datos[2] ##---> esto indica que la variable usuario ya tiene una session y es el campo username de arriba
        
        else:
            datos = ['', '', '']

 
    passwordV = check_password_hash(datos[0], password + datos[1])
    # print(passwordV) True o False




        
    if len(username) > 40:
     error.append("Username excede longitud máxima")


    #  conexion db
    with sqlite3.connect("pdme.db") as con:
        cur = con.cursor()
        # cur.execute("select 1 from usuario5784 where username = '"+ username + "' and password ='" + password + "'") ---> mala practica sql injection
        cur.execute("select Estado from login where username = ?", [username])
        estado = cur.fetchone()
        if estado:
            jsonify(estado)  # esto es para consultar el estado de la base de datos y que me devuelva en formato json el estado
        

    
    #conexion db
    with sqlite3.connect("pdme.db") as con:
        cur = con.cursor()
        # cur.execute("select 1 from usuario5784 where username = '"+ username + "' and password ='" + password + "'") ---> mala practica sql injection
        cur.execute("select * from login where username = ?", [username])

        if cur.fetchone() and estado[0] != 'ACT' and passwordV:
            error.clear()
            error.append("Debe activar el usuario en el link enviado por correo al momento de la creacion")
        else: 
            # cur = con.cursor()
            # # Te toca volver a llamar la conexion a la db para hacer la validacion
            # cur.execute("select * from login where username = ? and password = ?", [username, password])
            # if  cur.fetchone() and estado[0] == 'ACT':  # esto indica que si encontro el registro y adiconal la         
            #     return render_template("menu.html")

            cur = con.cursor()
            # Te toca volver a llamar la conexion a la db para hacer la validacion
            cur.execute("select * from login where username = ?", [username])
            if  cur.fetchone() and estado[0] == 'ACT' and passwordV:  # passwordV: = True  # esto indica que si encontro el registro y adiconal la         
                return render_template("menu.html")

            else:
                if not username or not password:
                    error.clear()
                    error.append("Username/Password son requeridos")
                else:
                    error.clear()
                    error.append('Usuario o Contraseña Invalido')
            
            

    return render_template("index.html", error = error)



## End point Procesar Data Envio de correos
@app.route('/procesar/correo', methods=["post"])
def procesarCorreo():
    

    if 'btnGuardar' in request.form:
        #Captura Los datos del estudiante desde el formulario enviado por el frontend
        emisor    = username #ussLogin()
        receptor  = request.form["txtReceptor"]
        asunto    = request.form["txtAsunto"]
        mensaje   = request.form["txtArea"]


        if not receptor or not mensaje:
         return "Por Favor Agregue un Destino / Mensaje Del Correo"


        #CONEXION A LA BASE DE DATOS
        with sqlite3.connect('pdme.db')  as con:
            #Crea un apuntador para manipular la BD
            cur = con.cursor()
            #Ejecuta la sentencia sql para guardar los datos
            cur.execute("Insert Into correo (emisor, receptor, mensaje, asunto) VALUES (?,?,?,?)", 
            [emisor, receptor, mensaje, asunto])
            # Guardar en BD

            con.commit
        return  "Guardado!!"


## End point Update Usuarios
@app.route('/update/uss', methods=["post"])
def updateUss():
    
    if 'btnGuardar' in request.form:
        #Captura Los datos del estudiante desde el formulario enviado por el frontend
        correo     = request.form["textCorreo"]
        passw      = request.form["textPass"]
        confirma   = request.form["textCheck"]

        # if confirma != 'true':
        #     return  "Por favor confirma la solicitud!!"

   

        #CONEXION A LA BASE DE DATOS
        with sqlite3.connect('pdme.db')  as con:
            #Crea un apuntador para manipular la BD
            cur = con.cursor()
            #Ejecuta la sentencia sql para guardar los datos
            # cur.execute("Update login set password = VALUES (?) where username =  VALUES (?)", 
            # [passw, correo])
            # cur.execute("Update login set password = "+passw+" where username =  VALUES (?)", 
            # [correo])
            clave = hashlib.sha256(passw.encode())
            passw = clave.hexdigest()
            cur.execute(" Update login set password = ?  where username =?",[passw, correo])
            # Guardar en BD

            con.commit
        return  "Guardado!!"




## End point Update Usuarios Por Correo
@app.route('/update/uss/correo', methods=["post"])
def updateUssCorreo():
    
    if 'btnGuardar' in request.form:
        #Captura Los datos del estudiante desde el formulario enviado por el frontend
        correo     = request.form["textCorreo"]
        passw      = request.form["textPass"]
        confirma   = request.form["textCheck"]

        # if confirma != 'true':
        #     return  "Por favor confirma la solicitud!!"

   

        #CONEXION A LA BASE DE DATOS
        with sqlite3.connect('pdme.db')  as con:
            #Crea un apuntador para manipular la BD
            cur = con.cursor()
            #Ejecuta la sentencia sql para guardar los datos
            # cur.execute("Update login set password = VALUES (?) where username =  VALUES (?)", 
            # [passw, correo])
            # cur.execute("Update login set password = "+passw+" where username =  VALUES (?)", 
            # [correo])
            clave = hashlib.sha256(passw.encode())
            passw = clave.hexdigest()
            cur.execute(" Update login set password = ?  where username =?",[passw, correo])
            # Guardar en BD

            con.commit
        return  "Guardado!!"

@app.route("/logout")
def logout():
    #Boraa la key usuario de la lista session
    session.pop("usuario", None)
    return redirect("/")



app.run(debug=True)#Ojo esto corre el entorno virtual
