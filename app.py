from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ibA_pX2V5Z-#3:4Tcs'
app.config['MYSQL_DB'] = 'imagenes'
conexion = MySQL(app)


class Controlador_pag:
    def __init__(self):
        self.pag_actual = 1
        self.sql = f"SELECT * FROM producto order by nombre_producto;"

    def ordenar_catalogo(self):
        try:
            self.conexion1 = mysql.connector.connect(
                host="localhost", user="root", password="ibA_pX2V5Z-#3:4Tcs", database="imagenes")
            self.cursor = self.conexion1.cursor()
            self.cursor.execute(self.sql)
            tabla = self.cursor.fetchall()
            self.cursor.close()
        except Exception as e:
            print("Error MySQL:", str(e))
        contador = 0
        db = []
        columna = []
        for x in tabla:
            if contador < 6:
                columna.append(x)
                contador += 1
            else:
                db.append(columna)
                columna = []
                columna.append(x)
                contador = 1
        if columna:
            db.append(columna)
        diccionario = {}
        contador = 1
        for x in db:
            diccionario[contador] = x
            contador += 1
        self.paginas = diccionario
        self.cantidad_paginas = len(diccionario)

    def avanzar(self):
        limite = len(self.paginas)
        paginado.ordenar_catalogo()
        if self.pag_actual < limite:
            self.pag_actual += 1

    def retroceder(self):
        paginado.ordenar_catalogo()
        if self.pag_actual > 1:
            self.pag_actual -= 1

    def buscar(self, numero):
        paginado.ordenar_catalogo()
        numero = int(numero)
        if numero > 0 and numero <= self.cantidad_paginas:
            self.pag_actual = numero
        else:
            self.pag_actual = 1


paginado = Controlador_pag()
paginado.ordenar_catalogo()


@app.context_processor
def variables_jinja():
    datos = {}
    datos['can_paginas'] = paginado.cantidad_paginas
    datos['actual'] = paginado.pag_actual
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM categoria"
        cursor.execute(sql)
        tabla = cursor.fetchall()
        datos["categorias"] = tabla
    except Exception as e:
        print("Error MySQL:", str(e))
    return datos


@app.route('/buscar', methods=['GET'])
def buscar():
    # capta lo que se ponga en el formulario
    buscar = request.args.get("buscar")
    query = f"SELECT * FROM producto where nombre_producto like '%{buscar}%';"
    paginado.sql = query
    paginado.ordenar_catalogo()
    catalogo = paginado.paginas
    # revisar el paginado cuando tengamos 200 productos
    return render_template('index.html', tabla=catalogo[1])


@app.route('/cargar')
def productos():
    return render_template('formulario.html')


@app.route('/siguiente')
def siguiente():
    paginado.avanzar()
    return redirect(f'/pagina/{paginado.pag_actual}')


@app.route('/anterior')
def anterior():
    paginado.retroceder()
    return redirect(f'/pagina/{paginado.pag_actual}')


@app.route('/subir', methods=['POST'])
def subir_archivo():
    if 'archivo' not in request.files:
        return 'ningún archivo'
    imagen = request.files['archivo']
    if imagen.filename == '':
        return 'ningún archivo'
    if imagen:
        producto = request.form.get('producto')
        producto = producto.title()
        precio = request.form.get('precio')
        descripcion = request.form.get('descripcion')
        descripcion = descripcion.capitalize()
        cantidad = request.form.get('cantidad')
        categoria = request.form.get('categoria')
        nombre_archivo = secure_filename(imagen.filename)
        tipo_archivo = nombre_archivo.rsplit('.', 1)[1]
        nombre_archivo = nombre_archivo.rsplit('.', 1)[0]
        nombre_modificado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{tipo_archivo}"
        nombre_final = nombre_archivo+nombre_modificado
        imagen.save('static/'+nombre_final)
        try:
            cursor = conexion.connection.cursor()
            sql = f"INSERT INTO `producto` (`nombre_producto`, `precio_producto`, `descripcion_producto`, `cantidad_producto`, `categoria_producto`, `imagen_producto`) VALUES ('{producto}', '{precio}', '{descripcion}', '{cantidad}', '{categoria}','{nombre_final}');"
            cursor.execute(sql)
            conexion.connection.commit()
        except Exception as e:
            print("Error MySQL:", str(e))
        return redirect('/')


@app.route('/modificar', methods=['GET', 'POST'])
def modificar():
    id_producto = request.args.get('id_producto')
    tabla = {}
    try:
        cursor = conexion.connection.cursor()
        sql = f"SELECT * FROM producto where idproducto = {id_producto}"
        cursor.execute(sql)
        tabla['producto'] = cursor.fetchone()
        sql = f"SELECT * FROM categoria where id_categoria = {tabla['producto'][5]}"
        cursor.execute(sql)
        tabla['categoria'] = cursor.fetchone()
    except Exception as e:
        print("Error MySQL:", str(e))
    return render_template('modificar.html', tabla=tabla)


@app.route('/confirmar', methods=['POST'])
def confirmar():
    id = request.form.get('id_producto')
    imagen = request.files['archivo']
    if imagen.filename == '':
        nombre_final = request.form.get('imagen_actual')
    else:
        nombre_archivo = secure_filename(imagen.filename)
        tipo_archivo = nombre_archivo.rsplit('.', 1)[1]
        nombre_archivo = nombre_archivo.rsplit('.', 1)[0]
        nombre_modificado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{tipo_archivo}"
        nombre_final = nombre_archivo+nombre_modificado
        imagen_vieja = request.form.get('imagen_actual')
        ubicacionvieja = os.path.join("static", imagen_vieja)
        os.remove(ubicacionvieja)
        imagen.save('static/'+nombre_final)
    producto = request.form.get('producto')
    producto = producto.title()
    precio = request.form.get('precio')
    descripcion = request.form.get('descripcion')
    descripcion = descripcion.capitalize()
    cantidad = request.form.get('cantidad')
    categoria = request.form.get('categoria')
    try:
        cursor = conexion.connection.cursor()
        sql = f"UPDATE `imagenes`.`producto` SET `precio_producto` = '{precio}', `nombre_producto` = '{producto}', `descripcion_producto` = '{descripcion}',  `cantidad_producto` = '{cantidad}', `imagen_producto` = '{nombre_final}', `categoria_producto` = '{categoria}' WHERE (`idproducto` = '{id}');"
        cursor.execute(sql)
        conexion.connection.commit()
    except Exception as e:
        print("Error MySQL:", str(e))
    return redirect('/')


@app.route("/")
@app.route("/pagina/<int:numero_pagina>")
def home(numero_pagina=1):
    query = f"SELECT * FROM producto order by nombre_producto;"
    paginado.sql = query
    paginado.ordenar_catalogo()
    paginado.buscar(numero_pagina)
    catalogo = paginado.paginas
    if numero_pagina in catalogo:
        return render_template('index.html', tabla=catalogo[numero_pagina])
    else:
        return render_template('index.html', tabla=catalogo[1])


@app.route("/eliminar", methods=['GET', 'POST'])
def eliminar():
    id_producto = request.args.get('id_producto')
    cursor = conexion.connection.cursor()
    sql = f"SELECT imagen_producto FROM producto WHERE idproducto = {id_producto}"
    cursor.execute(sql)
    resultado = cursor.fetchone()
    nombre_imagen = resultado[0]
    sql = f"DELETE FROM producto WHERE idproducto = {id_producto}"
    cursor.execute(sql)
    conexion.connection.commit()
    os.remove(os.path.join('static', nombre_imagen))
    paginado.ordenar_catalogo()
    return redirect('/')


@app.route('/categorias', methods=['GET', 'POST'])
def categorias():
    categorias = request.args.get('id')
    query = f"SELECT * FROM producto WHERE categoria_producto = {categorias}"
    paginado.sql = query
    paginado.ordenar_catalogo()
    catalogo = paginado.paginas

    return render_template('index.html', tabla=catalogo[1])
    # revisar cuando tengamos 200 productos


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
