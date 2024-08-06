from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class almacen(db.Model):
    id_almacen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    costo = db.Column(db.DECIMAL(10, 2), nullable=False)
    descripcion = db.Column(db.String(255))
    tipo = db.Column(db.Enum('producto', 'ingrediente', 'varios'), nullable=False)
    
    # Relación con historial y eliminación en cascada
    historial = db.relationship('historial', backref='almacen', cascade='all, delete-orphan')

class historial(db.Model):
    id_historial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_almacen = db.Column(db.Integer, db.ForeignKey('almacen.id_almacen'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum('venta', 'inversion', 'perdida'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    monto = db.Column(db.DECIMAL(10, 2), nullable=False)


class vista_productos(db.Model):
    __tablename__ = 'vista_productos'
    
    nombre = db.Column(db.String(100), primary_key=True)
    existencias = db.Column(db.Integer)
    costo = db.Column(db.DECIMAL(10, 2))
    descripcion = db.Column(db.String(255))

class vista_ingredientes(db.Model):
    __tablename__ = 'vista_ingredientes'
    
    nombre = db.Column(db.String(100), primary_key=True)
    existencias = db.Column(db.Integer)
    costo = db.Column(db.DECIMAL(10, 2))
    descripcion = db.Column(db.String(255))

class vista_varios(db.Model):
    __tablename__ = 'vista_varios'
    
    nombre = db.Column(db.String(100), primary_key=True)
    existencias = db.Column(db.Integer)
    costo = db.Column(db.DECIMAL(10, 2))
    descripcion = db.Column(db.String(255))

class vista_venta(db.Model):
    __tablename__ = 'vista_venta'
    
    nombre = db.Column(db.String(100), primary_key=True)
    ingreso = db.Column(db.DECIMAL(10, 2))
    fecha = db.Column(db.Date)

class vista_inversion(db.Model):
    __tablename__ = 'vista_inversion'
    
    nombre = db.Column(db.String(100), primary_key=True)
    egreso = db.Column(db.DECIMAL(10, 2))
    fecha = db.Column(db.Date)

class vista_perdida(db.Model):
    __tablename__ = 'vista_perdida'
    
    nombre = db.Column(db.String(100), primary_key=True)
    egreso = db.Column(db.DECIMAL(10, 2))
    fecha = db.Column(db.Date)
