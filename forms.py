from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, FloatField, SelectField, TextAreaField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import db

def get_choices(elemento):
    lista = []
    db_query = db.session.query(elemento).all()
    for item in db_query:
        tup = (item.id, item.nombre)
        lista.append(tup)
    return lista

def get_choices2(elemento):
    lista = []
    for item in elemento:
        tup = (item.id, item.referencia)
        lista.append(tup)
    return lista

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    surname = StringField('Apellido', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(message='Este campo es obligatorio.')])
    email = StringField('Email', validators=[DataRequired(message='Este campo es obligatorio.')])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Registrar')

class NewProductForm(FlaskForm):
    lista_proveedores = []
    lista_almacenes = []
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    referencia = StringField('Referencia', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    descripcion = StringField('Descripción', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=500)])
    proveedor = SelectField('Proveedor', choices=lista_proveedores)
    preciocoste = FloatField('Precio de coste', validators=[DataRequired(message='Este campo es obligatorio.')])
    pvp = FloatField('Precio de venta al público', validators=[DataRequired(message='Este campo es obligatorio.')])
    stock = IntegerField('Stock', validators=[DataRequired(message='Este campo es obligatorio.')])
    almacen = SelectField('Almacén', choices=lista_almacenes)
    ubicacion = StringField('Ubicación', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=24)])
    descatalogado = BooleanField('Descatalogado')
    submit = SubmitField('Guardar Producto')


class NewSupplierForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    telefono = StringField('Teléfono', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    direccion = StringField('Dirección', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=250)])
    cif = StringField('CIF', validators=[DataRequired(message='Este campo es obligatorio.')])
    iva = IntegerField('IVA', validators=[DataRequired(message='Este campo es obligatorio.')])
    descuento = IntegerField('Descuento', validators=[DataRequired(message='Este campo es obligatorio.')])
    email = StringField('Correo Electrónico', validators=[DataRequired(message='Este campo es obligatorio.')])
    submit = SubmitField('Guardar Proveedor')

class NewOrderForm(FlaskForm):
    fecha = DateTimeField('Fecha', format='%d-%m-%Y', default=datetime.today, validators=[DataRequired()])
    nombre = StringField('Nombre Cliente', validators=[DataRequired(), Length(max=128)])
    referencia = StringField('Referencia del Producto', validators=[DataRequired(), Length(max=24)])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    submit = SubmitField('Guardar Pedido')

class NewSupplierOrderForm(FlaskForm):
    lista_proveedores = []
    fecha = DateTimeField('Fecha', format='%d-%m-%Y', default=datetime.today, validators=[DataRequired()])
    proveedor = SelectField('Proveedor', choices=lista_proveedores)
    nombre = StringField('Nombre Producto')
    referencia = SelectField('Referencia')
    preciocoste = FloatField('Precio €')
    cantidad = IntegerField('Cantidad')
    total = FloatField('Total €')
    descuento = FloatField('% Descuento')
    iva = FloatField('% IVA')
    total_pedido = FloatField('Total €')
    submit = SubmitField('Guardar Pedido')
