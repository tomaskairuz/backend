# Importamos el framework Flask
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
# Importamos el módulo que permite conectarnos a la base de datos MySQL
from flask_mysqldb import MySQL
# Importamos las funciones relativas a fecha y hora
from datetime import datetime
# Importamos paquetes de interfaz con el sistema operativo.
import os

# Creamos la aplicación
app = Flask(__name__)
app.secret_key = "mysecretkey"

# Configuramos la conexión con la base de datos:
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'sistema'

# Creamos la instancia de MySQL
mysql = MySQL(app)

# Guardamos la ruta de la carpeta "uploads" en nuestra app
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

# Ruta principal para mostrar la página de inicio
@app.route('/')
def index():
    # Creamos una variable que va a contener la consulta sql:
    sql = "SELECT * FROM empleados;"
    # Nos conectamos a la base de datos
    conn = mysql.connection
    # Sobre el cursor vamos a realizar las operaciones
    cursor = conn.cursor()
    # Ejecutamos la sentencia SQL sobre el cursor
    cursor.execute(sql)
    # Copiamos el contenido del cursor a una variable
    db_empleados = cursor.fetchall()
    # y mostramos las tuplas por la terminal
    print("-" * 60)
    for empleado in db_empleados:
        print(empleado)
    print("-" * 60)
    # "Commiteamos" (Cerramos la conexión)
    conn.commit()
    # Devolvemos código HTML para ser renderizado
    return render_template('empleados/index.html', empleados=db_empleados)

# Función para eliminar un registro
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    return redirect('/')

# Función para editar un registro
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id,))
    empleado = cursor.fetchone()
    conn.commit()
    cursor.close()
    return render_template('empleados/edit.html', empleado=empleado)

# Función para actualizar los datos de un registro
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files.get('txtFoto')  # Utiliza get en lugar de []
    id = request.form['txtID']
    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;"
    datos = (_nombre, _correo, id)
    conn = mysql.connection
    cursor = conn.cursor()

    # Guardamos en now los datos de fecha y hora
    now = datetime.now()
    # Y en tiempo almacenamos una cadena con esos datos
    tiempo = now.strftime("%Y%H%M%S")

    # Si el nombre de la foto ha sido proporcionado en el form...
    if _foto and _foto.filename != '':
        # Creamos el nombre de la foto y la guardamos.
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

        # Buscamos el registro y buscamos el nombre de la foto vieja:
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
        fila = cursor.fetchone()
        
        # Aseguramos que exista una foto previa y la borramos de la carpeta:
        if fila and fila[0]:
            os.remove(os.path.join(app.config['CARPETA'], fila[0]))

        # Finalmente, actualizamos la DB con el nuevo nombre del archivo:
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s;", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()
    cursor.close()
    return redirect('/')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Obtener datos del formulario
        _nombre = request.form['txtNombre']
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']

        # Guardamos en now los datos de fecha y hora
        now = datetime.now()

        # Y en tiempo almacenamos una cadena con esos datos
        tiempo = now.strftime("%Y%H%M%S")

        # Si el nombre de la foto ha sido proporcionado en el form...
        if _foto.filename != '':
            # ...le cambiamos el nombre.
            nuevoNombreFoto = tiempo + _foto.filename
            # Guardamos la foto en la carpeta uploads.
            _foto.save("uploads/" + nuevoNombreFoto)
        else:
            nuevoNombreFoto = ''

        # Consulta SQL para insertar los datos
        sql = "INSERT INTO empleados (nombre, correo, foto) VALUES (%s, %s, %s);"
        datos = (_nombre, _correo, nuevoNombreFoto)

        # Conectamos a la base de datos
        conn = mysql.connection
        cursor = conn.cursor()

        # Ejecutamos la sentencia SQL con los datos
        cursor.execute(sql, datos)
        conn.commit()

        # Cerramos el cursor
        cursor.close()

        # Redirigimos a la página de inicio
        return redirect('/')
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    # Validación de los datos
    if not _nombre or not _correo or not _foto:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('create'))

    # Guardamos en now los datos de fecha y hora
    now = datetime.now()

    # Y en tiempo almacenamos una cadena con esos datos
    tiempo = now.strftime("%Y%H%M%S")

    # Si el nombre de la foto ha sido proporcionado en el form...
    if _foto.filename != '':
        # ...le cambiamos el nombre.
        nuevoNombreFoto = tiempo + _foto.filename
        # Guardamos la foto en la carpeta uploads.
        _foto.save("uploads/" + nuevoNombreFoto)
    else:
        nuevoNombreFoto = ''

    # Y armamos una tupla con esos valores:
    datos = (_nombre, _correo, nuevoNombreFoto)

    # Armamos la sentencia SQL que va a almacenar estos datos en la DB:
    sql = "INSERT INTO empleados (nombre, correo, foto) VALUES (%s, %s, %s);"
    conn = mysql.connection
    cursor = conn.cursor() # En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos) # Ejecutamos la sentencia SQL en el cursor
    conn.commit() # Hacemos el commit

    # Cerramos el cursor
    cursor.close()

    # Redirigimos a la página de inicio
    return redirect('/')

# Generamos el acceso a la carpeta uploads.
# El método uploads que creamos nos dirige a la carpeta (variable CARPETA)
# y nos muestra la foto guardada en la variable nombreFoto.
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

# Esta línea de código es requerida por Python para iniciar la aplicación
if __name__ == '__main__':
    # Corremos la aplicación en modo debug
    app.run(debug=True)
