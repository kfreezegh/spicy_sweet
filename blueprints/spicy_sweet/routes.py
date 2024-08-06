from datetime import datetime, timedelta
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import func
from blueprints.spicy_sweet.models import db, almacen, historial, vista_productos, vista_ingredientes, vista_varios

spicy_sweet = Blueprint('spicy_sweet', 
                __name__,
                template_folder='templates',
                static_folder='static',
                static_url_path='/static/spicy_sweet')

users = {'admin': 'admin'}

@spicy_sweet.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('spicy_sweet.home'))
    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('spicy_sweet.home'))
        else:
            return render_template('spicy_sweet/login.html')
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            return redirect(url_for('spicy_sweet.home'))
        else:
            error = 'Usuario o contraseña incorrectos'
            return render_template('spicy_sweet/login.html', error=error)


@spicy_sweet.route('/home')
def home():
    if session.get('logged_in'):
        # OBTENER TABLA
        if request.method == 'GET':
            # TOTAL DE VENTAS
            totalVentas = db.session.query(func.round(func.sum(historial.monto), 2)).filter(historial.tipo == 'venta', historial.fecha >= datetime.now() - timedelta(days=30)).scalar()
            totalVentas = totalVentas if totalVentas is not None else 0.0
            # TOTAL DE INVERSIÓN
            totalInversion = db.session.query(func.round(func.sum(historial.monto), 2)).filter(historial.tipo == 'inversion', historial.fecha >= datetime.now() - timedelta(days=30)).scalar()
            totalInversion = totalInversion if totalInversion is not None else 0.0
            # TOTAL DE GANANCIAS
            totalGanancias = round(totalVentas - totalInversion, 2)
            # MÁS VENDIDOS
            masVendidos = db.session.query(
                 almacen.nombre.label('nombre_almacen'),
                    func.sum(historial.cantidad).label('cantidad_vendida'),
                    func.round(func.sum(historial.monto), 2).label('monto_total')
                ).join(
                    historial, historial.id_almacen == almacen.id_almacen
                ).filter(
                    historial.tipo == 'venta',
                    historial.fecha >= datetime.now() - timedelta(days=30)
                ).group_by(almacen.nombre).order_by(func.sum(historial.cantidad).desc()).limit(5).all()

            # ÚLTIMAS VENTAS
            ultimasVentas = db.session.query(
                historial.fecha,
                almacen.nombre.label('nombre_producto'),
                historial.cantidad,
                func.round(historial.monto, 2).label('venta_total')
            ).join(
                almacen, historial.id_almacen == almacen.id_almacen
            ).filter(
                historial.tipo == 'venta',
                historial.fecha <= datetime.now().date()
            ).order_by(historial.fecha.desc()).limit(5).all()

            return render_template('spicy_sweet/home.html',
                                   totalVentas=totalVentas,
                                   totalInversion=totalInversion,
                                   totalGanancias=totalGanancias,
                                   masVendidos=masVendidos,
                                   ultimasVentas=ultimasVentas)
    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/productos', methods=['GET', 'POST', 'PUT', 'DELETE'])
def productos():
    if session.get('logged_in'):
        
        if request.method == 'GET':
            # OBTENER TABLA
            registros = vista_productos.query.all()
            stock_bajo = db.session.query(vista_productos).filter(vista_productos.existencias < 3).all()
            return render_template('spicy_sweet/producto.html', registros=registros, stock_bajo=stock_bajo)
        
        if request.method == 'POST':   
            # CREAR REGISTRO
            nuevo_almacen = almacen(
                nombre = request.form.get('nombre'),
                costo = request.form.get('precio'),
                descripcion = request.form.get('descripcion'),
                tipo = 'producto'
            )
            db.session.add(nuevo_almacen)
            db.session.commit()
            return render_template('spicy_sweet/producto.html')
        
        if request.method == 'PUT':
            data = request.form
            tipo_operacion = data.get('tipo_operacion')
            # ACTUALIZAR EXISTENCIAS
            if tipo_operacion == 'actualizar_existencias':
                nombreProducto = request.form.get('nombreProducto')
                entradas = int(request.form.get('entradas') or 0)
                salidas = int(request.form.get('salidas') or 0)
                id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar() or None
                # CALCULAR CANTIDAD NUEVA
                cantidad_nueva = db.session.query(almacen.cantidad).filter_by(id_almacen=id_almacen).scalar() + entradas - salidas
                # VERIFICAR SI LA CANTIDAD NUEVA ES MAYOR O IGUAL A 0
                if cantidad_nueva >= 0:
                    # ACTUALIZAR CANTIDAD DE EXISTENCIAS EN ALMACEN (SUMA ENTRADAS Y RESTA SALIDAS)
                    db.session.query(almacen).filter_by(id_almacen=id_almacen).update({'cantidad': cantidad_nueva})
                    db.session.commit()
                    # AGREGAR SALIDAS (VENTAS) A HISTORIAL
                    if salidas:
                        nuevo_historial = historial(
                            id_almacen=id_almacen,
                            fecha=datetime.now(),
                            tipo='venta',
                            cantidad=salidas
                        )
                        db.session.add(nuevo_historial)
                        db.session.commit()
                    return jsonify({'message': 'Registro guardado correctamente'}), 200
                else:
                    return jsonify({'error': 'El número de salidas no puede ser mayor al número de existencias actuales.'}), 400
            
            # EDITAR INFORMACIÓN
            elif tipo_operacion == 'editar_informacion':
                nombreProducto = request.form.get('nombreProducto')
                nuevoNombre = request.form.get('newNombre')
                nuevoPrecio = request.form.get('newPrecio')
                nuevaDescripcion = request.form.get('newDescripcion')
                producto = almacen.query.filter_by(nombre=nombreProducto).first()
                if producto:
                    producto.nombre = nuevoNombre
                    producto.costo = nuevoPrecio
                    producto.descripcion = nuevaDescripcion
                    db.session.commit()
                else:
                    flash("El producto no se encontró en la base de datos.")
            return render_template('spicy_sweet/producto.html')

        # ELIMINAR REGISTRO
        if request.method == 'DELETE':
            nombreProducto = request.form.get('nombreProducto')
            id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar()
            db.session.query(almacen).filter_by(id_almacen=id_almacen).delete()
            db.session.commit()
            return render_template('spicy_sweet/producto.html')
    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/ingredientes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ingredientes():
    if session.get('logged_in'):

        if request.method == 'GET':
            # OBTENER TABLA
            registros = vista_ingredientes.query.all()
            stock_bajo = db.session.query(vista_ingredientes).filter(vista_ingredientes.existencias < 3).all()
            return render_template('spicy_sweet/ingrediente.html', registros=registros, stock_bajo=stock_bajo)

        if request.method == 'POST':   
            # CREAR REGISTRO
            nuevo_almacen = almacen(
                nombre = request.form.get('nombre'),
                costo = request.form.get('precio'),
                descripcion = request.form.get('descripcion'),
                tipo = 'ingrediente'
            )
            db.session.add(nuevo_almacen)
            db.session.commit()
            return render_template('spicy_sweet/ingrediente.html')
        
        if request.method == 'PUT':
            data = request.form
            tipo_operacion = data.get('tipo_operacion')
            # ACTUALIZAR EXISTENCIAS
            if tipo_operacion == 'actualizar_existencias':
                nombreProducto = request.form.get('nombreProducto')
                entradas = int(request.form.get('entradas') or 0)
                salidas = int(request.form.get('salidas') or 0)
                id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar() or None
                # CALCULAR CANTIDAD NUEVA
                cantidad_nueva = db.session.query(almacen.cantidad).filter_by(id_almacen=id_almacen).scalar() + entradas - salidas
                # VERIFICAR SI LA CANTIDAD NUEVA ES MAYOR O IGUAL A 0
                if cantidad_nueva >= 0:
                    # ACTUALIZAR CANTIDAD DE EXISTENCIAS EN ALMACEN (SUMA ENTRADAS Y RESTA SALIDAS)
                    db.session.query(almacen).filter_by(id_almacen=id_almacen).update({'cantidad': cantidad_nueva})
                    db.session.commit()
                    # AGREGAR ENTRADAS (INVERSIÓN) A HISTORIAL
                    if entradas:
                        nuevo_historial = historial(
                            id_almacen=id_almacen,
                            fecha=datetime.now(),
                            tipo='inversion',
                            cantidad=entradas
                        )
                        db.session.add(nuevo_historial)
                        db.session.commit()
                    return jsonify({'message': 'Registro guardado correctamente'}), 200
                else:
                    return jsonify({'error': 'El número de salidas no puede ser mayor al número de existencias actuales.'}), 400
            
            # EDITAR INFORMACIÓN
            elif tipo_operacion == 'editar_informacion':
                nombreProducto = request.form.get('nombreProducto')
                nuevoNombre = request.form.get('newNombre')
                nuevoPrecio = request.form.get('newPrecio')
                nuevaDescripcion = request.form.get('newDescripcion')
                producto = almacen.query.filter_by(nombre=nombreProducto).first()
                if producto:
                    producto.nombre = nuevoNombre
                    producto.costo = nuevoPrecio
                    producto.descripcion = nuevaDescripcion
                    db.session.commit()
                else:
                    flash("El producto no se encontró en la base de datos.")
            return render_template('spicy_sweet/producto.html')

        # ELIMINAR REGISTRO
        if request.method == 'DELETE':
            nombreProducto = request.form.get('nombreProducto')
            id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar()
            db.session.query(almacen).filter_by(id_almacen=id_almacen).delete()
            db.session.commit()

    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/varios', methods=['GET', 'POST', 'PUT', 'DELETE'])
def varios():
    if session.get('logged_in'):
        
        if request.method == 'GET':
            # OBTENER TABLA
            registros = vista_varios.query.all()
            stock_bajo = db.session.query(vista_varios).filter(vista_varios.existencias < 3).all()
            return render_template('spicy_sweet/varios.html', registros=registros, stock_bajo=stock_bajo)

        if request.method == 'POST':   
            # CREAR REGISTRO
            nuevo_almacen = almacen(
                nombre = request.form.get('nombre'),
                costo = request.form.get('precio'),
                descripcion = request.form.get('descripcion'),
                tipo = 'varios'
            )
            db.session.add(nuevo_almacen)
            db.session.commit()
            return render_template('spicy_sweet/varios.html')
        
        if request.method == 'PUT':
            data = request.form
            tipo_operacion = data.get('tipo_operacion')
            
            # ACTUALIZAR EXISTENCIAS
            if tipo_operacion == 'actualizar_existencias':
                nombreProducto = request.form.get('nombreProducto')
                entradas = int(request.form.get('entradas') or 0)
                salidas = int(request.form.get('salidas') or 0)
                id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar() or None
                # CALCULAR CANTIDAD NUEVA
                cantidad_nueva = db.session.query(almacen.cantidad).filter_by(id_almacen=id_almacen).scalar() + entradas - salidas
                # VERIFICAR SI LA CANTIDAD NUEVA ES MAYOR O IGUAL A 0
                if cantidad_nueva >= 0:
                    # ACTUALIZAR CANTIDAD DE EXISTENCIAS EN ALMACEN (SUMA ENTRADAS Y RESTA SALIDAS)
                    db.session.query(almacen).filter_by(id_almacen=id_almacen).update({'cantidad': cantidad_nueva})
                    db.session.commit()
                    # AGREGAR ENTRADAS (INVERSION) A HISTORIAL
                    if entradas:
                        nuevo_historial = historial(
                            id_almacen=id_almacen,
                            fecha=datetime.now(),
                            tipo='inversion',
                            cantidad=entradas
                        )
                        db.session.add(nuevo_historial)
                        db.session.commit()
                    return jsonify({'message': 'Registro guardado correctamente'}), 200
                else:
                    return jsonify({'error': 'El número de salidas no puede ser mayor al número de existencias actuales.'}), 400
            
            # EDITAR INFORMACIÓN
            elif tipo_operacion == 'editar_informacion':
                nombreProducto = request.form.get('nombreProducto')
                nuevoNombre = request.form.get('newNombre')
                nuevoPrecio = request.form.get('newPrecio')
                nuevaDescripcion = request.form.get('newDescripcion')
                producto = almacen.query.filter_by(nombre=nombreProducto).first()
                if producto:
                    producto.nombre = nuevoNombre
                    producto.costo = nuevoPrecio
                    producto.descripcion = nuevaDescripcion
                    db.session.commit()
                else:
                    flash("El producto no se encontró en la base de datos.")
            return render_template('spicy_sweet/producto.html')

        # ELIMINAR REGISTRO
        if request.method == 'DELETE':
            nombreProducto = request.form.get('nombreProducto')
            id_almacen = db.session.query(almacen.id_almacen).filter_by(nombre=nombreProducto).scalar()
            db.session.query(almacen).filter_by(id_almacen=id_almacen).delete()
            db.session.commit()
    
    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/settings')
def settings():
    if session.get('logged_in'):
        return render_template('spicy_sweet/settings.html')
    else:
        return redirect(url_for('spicy_sweet.login'))


@spicy_sweet.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('spicy_sweet.login'))