from sys import maxunicode
from flask import Flask
from flask import Flask
from flask import render_template, request, redirect
from flask import send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
from random import seed
from random import randint

import os

from pymysql import cursors

app=Flask(__name__)

mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_Db']='qfc'
mysql.init_app(app)

CARPETA=os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/')
def index():
    sql="SELECT * FROM `qcf`.`datos`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    datos=cursor.fetchall()
    #print (datos)
    conn.commit()
    return render_template('qcf/index.html', datos=datos)
@app.route('/about')
def about():
    return render_template('qcf/about.html')

@app.route('/create')
def create():
    return render_template('qcf/create.html')
@app.route('/store', methods=['POST'])
def store():
    _nombre=request.form['txtNombre']
    _info=request.form['txtInfo']
    _foto=request.files['txtFoto']
    _enlace=request.form['txtEnlace']

    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    if _foto.filename != '':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    
    sql="INSERT INTO `qcf`.`datos` (`id`,`nombre`,`imagen`,`info`,`link`) VALUES (NULL, %s, %s,%s,%s);"
    datos=(_nombre, nuevoNombreFoto, _info,_enlace)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')
#Averiguar bien para que y como
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

# Pagina del listado completo
@app.route('/listado')
def listado():
    sql="SELECT * FROM `qcf`.`datos`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    datos=cursor.fetchall()
    conn.commit()
    return render_template ('qcf/listado.html', datos=datos)

# Pagina de editar + update
@app.route('/editar/<int:id>')
def edit(id):
    sql="SELECT * FROM `qcf`.`datos` WHERE id=%s;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, (id))
    datos=cursor.fetchall()
    conn.commit()
    print(datos)
    return render_template ('qcf/editar.html', datos=datos)
@app.route ('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _info=request.form['txtInfo']
    _foto=request.files['txtFoto']
    _enlace=request.form['txtEnlace']
    id=request.form['txtId']
    sql="UPDATE `qcf`.`datos` SET `nombre`=%s, `info`=%s, `link`=%$ WHERE id=%s"
    datos=(_nombre,_info,_enlace,id)
    conn=mysql.connect()
    cursor=conn.cursor()
    #Cargamos la foto con nombre unico
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    if _foto.filename !='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        cursor.execute("SELECT imagen FROM `qcf`.`datos` WHERE id=%s;", id)
        fila=cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE `qcf`.`datos` SET imagen=%s WHERE id=%s;", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')
#Eliminamos entrada
@app.route('/destroy/<int:id>')
def destroy(id):
    sql="DELETE FROM `qcf`.`datos` WHERE id=%s;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute ("SELECT foto FROM `datos`.`empleados`WHERE id=%s;", (id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila [0][0]))
    cursor.execute(sql, (id))
    conn.commit()
    return redirect('/listado')

#Intentaremos hacer que cada uno de los links nos lleve a donde corresponda
@app.route('/detalle/<int:id>')
def detalle(id):
    sql="SELECT * FROM `qcf`.`datos` WHERE id=%s;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, (id))
    datos=cursor.fetchall()
    conn.commit()
    return render_template('qcf/detalle.html', datos=datos)

@app.route('/azar')
def azar(): #Terminar de hacer que muestre un elemento al azar en el index
    maximo="SELECT MAX(id) FROM `qcf`.`datos`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(maximo)
    maxid=cursor.fetchall()
    conn.commit()
    id=maxid[0][0]  #Extraemos el valor entero de la tupla
    
    #Generamos una semilla aleatoria usando lo mismo que usamos para generar un nombre unico para las fotos
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    seed(tiempo)
    value = randint(0, id)
    sql="SELECT * FROM `qcf`.`datos` WHERE id=%s;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, value)
    datos=cursor.fetchall()
    conn.commit()
    return render_template('qcf/detalle.html', datos=datos)

#Idea para autenticar usuario, aun no funciona.
'''
@app.route('/edit/')
def edit():
    return render_template('qcf/edit.html')

@app.route('/validar', methods=['POST'])
def validar():
    _contra=request.form['contra']
    sql="SELECT pass FROM `qcf`.`usuarios`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    datos=cursor.fetchall()
    conn.commit()
    for dato in datos:
        #dat="123456"
        if str(dato)==("('"+str(_contra)+"'),"):
            print (dato,_contra, "Correcto")
        else:
            print(dato,_contra, "Incorrecto")    
    print (datos)
    return redirect('/')
'''

if __name__=='__main__':
    app.run(debug=True)