from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, flash
import os
import time
print(os.urandom(24))  # Esto generará 24 bytes aleatorios

app = Flask(__name__)

# Looking to send emails in production? Check out our Email API/SMTP product!
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '4224b45ce97355'
app.config['MAIL_PASSWORD'] = 'ad8f41f138bbbd'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'porta'

app.config['SECRET_KEY'] = os.urandom(24)
# Inicializar extensiones
mysql = MySQL(app)
mail = Mail(app)  # Inicializa Mail aquí

# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('sitio/index.html')

#ruta sobre mi
@app.route('/sobre_mi')
def sobre_mi():
    return render_template('sitio/sobremi.html')

#ruta portafolio
@app.route('/portafolio')
def portafolio():
    return render_template('sitio/portafolio.html')

#ruta mapa 
@app.route('/mapa')
def mapa():
    return render_template('sitio/mapa.html')

# Límite de intentos fallidos
MAX_INTENTOS = 3
BLOQUEO_TIEMPO = 300  # 5 minutos (300 segundos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    tiempo_restante = 0  # Inicializa el tiempo restante
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']

        # Inicializar intentos fallidos en sesión si no existe
        if 'intentos_fallidos' not in session:
            session['intentos_fallidos'] = {}

        # Si el usuario ha fallado demasiadas veces, verificar si está bloqueado
        if email in session['intentos_fallidos']:
            intentos, tiempo_bloqueo = session['intentos_fallidos'][email]

            if intentos >= MAX_INTENTOS:
                tiempo_restante = BLOQUEO_TIEMPO - (time.time() - tiempo_bloqueo)
                if tiempo_restante > 0:
                    flash("Demasiados intentos fallidos. Inténtalo de nuevo en unos momentos.", 'danger')
                    return render_template('login/login.html', tiempo_restante=int(tiempo_restante))

        # Verificar credenciales en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, contrasena FROM usuarios WHERE email = %s", [email])
        usuario = cur.fetchone()
        cur.close()

        if usuario and check_password_hash(usuario[2], contrasena):  # La contraseña está en la posición 2
            session['usuario_id'] = usuario[0]  # Guardar ID del usuario en sesión
            session.pop('intentos_fallidos', None)  # Reiniciar intentos al loguearse correctamente
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos.", 'danger')

            # Registrar intento fallido
            if email in session['intentos_fallidos']:
                session['intentos_fallidos'][email] = (session['intentos_fallidos'][email][0] + 1, time.time())
            else:
                session['intentos_fallidos'][email] = (1, time.time())

            # Bloquear si excede los intentos permitidos
            if session['intentos_fallidos'][email][0] >= MAX_INTENTOS:
                tiempo_restante = BLOQUEO_TIEMPO
                session['intentos_fallidos'][email] = (MAX_INTENTOS, time.time())
                flash("Has excedido el número de intentos. Espera unos momentos para intentarlo de nuevo.", 'danger')

    return render_template('login/login.html', tiempo_restante=int(tiempo_restante))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Cerrar sesión
    return redirect(url_for('index'))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contrasena = request.form['contrasena']

        # Validar si los campos están vacíos
        if not all([nombre, email, contrasena]):
            mensaje = "Por favor, completa todos los campos."
            return render_template('login/login.html', mensaje=mensaje)

        # Verificar si el correo ya está registrado
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", [email])
        usuario = cur.fetchone()

        if usuario:
            mensaje = "El correo electrónico ya está registrado."
            return render_template('login/login.html', mensaje=mensaje)

        # Insertar el nuevo usuario en la base de datos
        contrasena_hash = generate_password_hash(contrasena)  # Encriptar la contraseña
        cur.execute("INSERT INTO usuarios (nombre, email, contrasena) VALUES (%s, %s, %s)", 
                    (nombre, email, contrasena_hash))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))  # Redirigir al login después del registro

    return render_template('login/login.html')


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    mensaje = None
    exito = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje_texto = request.form['mensaje']

        if not all([nombre, email, mensaje_texto]):
            mensaje = "Por favor completa todos los campos."
            exito = False
        else:
            try:
                # 1. Enviar correo
                msg = Message(
                    subject=f"Nuevo mensaje de {nombre}",
                    recipients=["vasquez.jcesar@gmail.com"],  # Email donde quieres recibir
                    sender=app.config['MAIL_USERNAME'],
                    body=f"""
                    Nombre: {nombre}
                    Email: {email}
                    Mensaje: {mensaje_texto}
                    """
                )
                mail.send(msg)  # Enviar correo

                # 2. Guardar en base de datos si el correo se envió correctamente
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO contactos (nombre, correo_electronico, mensaje) VALUES (%s, %s, %s)", 
                            (nombre, email, mensaje_texto))
                mysql.connection.commit()
                cur.close()

                mensaje = "¡Mensaje enviado con éxito!"
                exito = True

            except Exception as e:
                app.logger.error(f"Error al enviar correo: {str(e)}")
                mensaje = f"Error al enviar: {str(e)}"
                exito = False

    return render_template('sitio/contacto.html', mensaje=mensaje, exito=exito)


if __name__ == '__main__':
    app.run(debug=True)