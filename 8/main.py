from flask import Flask, render_template, request
from flask_mail import Mail, Message
from celery import Celery
import redis

app = Flask(__name__)

r = redis.Redis(
    host = "localhost",
    port = 6379)
r.set("id", -1)

pa="palabra"
si="significado"

def existe(palabra):
    cantpalabras = r.llen(pa)
    existencia = False
    for i in range(cantpalabras):
        currentPalabra = r.lindex(pa, i).decode('utf-8')
        if(currentPalabra == palabra):
            existencia = True
        break
    return existencia 

def agregar_palabra(palabra, significado):
    r.incr("id")
    r.rpush(pa, palabra)
    r.rpush(si, significado)

def editar_palabra(Vpalabra, Npalabra, Nsignificado):
    palabras = r.llen(pa)
    for i in range(palabras):
        currentWord = r.lindex(pa, i).decode('utf-8')
        if(currentWord == Vpalabra):
            r.lset(pa, i, Npalabra)
            r.lset(si, i, Nsignificado)
            break

def eliminar_palabra(palabra):
    cantpalabras = r.llen(pa)
    for i in range(cantpalabras):
        actualPalabra = r.lindex(pa, i).decode('utf-8')
        actualSignificado = r.lindex(si, i).decode('utf-8')
        if(actualPalabra == palabra):
            r.lrem(pa, i, actualPalabra)
            r.lrem(si, i, actualSignificado)
            break

def obtener_palabras():
    cantpalabras = r.llen(pa)
    palabras = []
    for x in range(cantpalabras):
        palabras.append({"nombre": r.lindex(pa, x).decode("utf-8"), "significado": r.lindex(si, x).decode("utf-8")})
    return palabras

############################################################APPROUTE#######################################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    obtenerP = obtener_palabras()
    return render_template("index.html", palabras=obtenerP)

@app.route('/agregar_palabra', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        palabra = request.form['pa']
        significado = request.form['si']
        if existe(palabra):
            return render_template("agregar_palabra.html", message=False)
        else:
            agregar_palabra(palabra, significado)
            return render_template("agregar_palabra.html", message=True)

    return render_template("agregar_palabra.html")


@app.route('/editar_palabra', methods=['GET', 'POST'])
def editar():
    if request.method == 'POST':
        Vpalabra = request.form["vpa"]
        Npalabra = request.form["pa"]
        Nsignificado = request.form["si"]
        
        if existe(Vpalabra):
            editar_palabra(Vpalabra, Npalabra, Nsignificado)

            return render_template("editar_palabra.html", message=False)
        else:

            return render_template("editar_palabra.html", message=True)

    return render_template("editar_palabra.html")


@app.route('/eliminar_palabra', methods=['GET', 'POST'])
def eliminar():
    if request.method == 'POST':
        palabra = request.form['pa']
        if existe(palabra):
            eliminar_palabra(palabra)
            obtener_palabras()
            return render_template("eliminar_palabra.html", message=False)
        else:
            obtener_palabras()
            return render_template("eliminar_palabra.html", message=True)

    return render_template("eliminar_palabra.html")
    
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '57f2ff6b9a0188'
app.config['MAIL_PASSWORD'] = 'f82835a15c4057'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

celery = Celery(app.name, broker='redis://localhost:6379/0')
mail = Mail(app)


@Celery.task
def send_async_email(email_data):
    print(email_data + "hola")
    msg = Message(email_data['subject'],
                  sender='victor@vergara.com',
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    mail.send(msg)

@app.route('/email', methods=['GET', 'POST'])
def sendEmail():
    if request.method == 'GET':
        return render_template('email.html')

    email = request.form['email']
    message = request.form['message']

    email_data = {
        'subject': 'Hola esto es una prueba de email',
        'to': email,
        'body': message,
    }

    send_async_email(email_data)


if __name__ == '__main__':
    app.run( debug = True)
