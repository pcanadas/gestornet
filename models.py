from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import db


class User(db.Base, UserMixin):
    __tablename__ = "usuarios"
    __table_args__ = {'sqlite_autoincrement': True}  # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    surname = Column(String(80), nullable=False)
    email = Column(String(256), nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    def __repr__(self):
        return f'<User {self.email}>'
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Proveedor(db.Base):

    __tablename__ = "proveedores"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # nullable hace que el campo nombre NO pueda estar vacío.
    telefono = Column(Integer, nullable=False)
    direccion = Column(String(500))
    cif = Column(String(16), nullable=False)
    iva = Column(Integer, nullable=False)
    descuento = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)

    def __repr__(self):
        return f'<Proveedor {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Almacen(db.Base):

    __tablename__ = "almacenes"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # nullable hace que el campo nombre NO pueda estar vacío.

    def __repr__(self):
        return f'<Almacen {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Producto(db.Base):

    __tablename__ = "productos"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # nullable hace que el campo nombre NO pueda estar vacío.
    referencia = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    proveedor = Column(String(100), nullable=False)
    preciocoste = Column(Integer, nullable=False)
    pvp = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
    almacen = Column(String(64)) #Quiero poner una lista desplegable
    ubicacion = Column(String(24))
    descatalogado = Column(Boolean) # True si el producto está descatalogado y ya no se puede vender

    def __repr__(self):
        return f'<Producto {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Pedido(db.Base):

    __tablename__ = "pedidos"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    nombre = Column(String(128), nullable=False)
    referencia = Column(String(24), nullable=False)
    cantidad = Column(Integer, nullable=False)
    total = Column(Integer)
    mes = Column(Integer)
    year = Column(Integer)
    mes_year = Column(Integer)

    def __repr__(self):
        return f'<Pedido {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Facturacion(db.Base):

    __tablename__ = "facturacion"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, nullable=False) # Número de pedido de la tabla 'pedidos', corresponde con Pedido.id
    proveedor = Column(Integer, nullable=False) # Número que corresponde con Proveedor.id
    referencia = Column(String(24), nullable=False) # Referencia del producto pedido
    cantidad = Column(Integer, nullable=False) # Cantidad de productos pedidos
    total = Column(Integer) # Total del pedido

    def __repr__(self):
        return f'<Facturacion {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class PedidoProveedor(db.Base):

    __tablename__ = "pedidos_proveedor"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    proveedor = Column(Integer, nullable=False)  # Número que corresponde con Proveedor.id
    referencia = Column(String(24), nullable=False)
    nombre = Column(String(128), nullable=False)
    preciocoste = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    total_precio = Column(Integer, nullable=False)  # Total del producto
    descuento = Column(Integer, nullable=False)
    iva = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False) # Total del pedido

    def __repr__(self):
        return f'<Pedido a proveedor {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
