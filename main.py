import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from werkzeug.urls import url_parse
from forms import SignupForm, LoginForm, NewProductForm, NewSupplierForm, get_choices, get_choices2, NewOrderForm, \
    NewSupplierOrderForm
import db
import json
from models import User, Producto, Proveedor, Almacen, Pedido, Facturacion, PedidoProveedor

# Creación objetos Flask
app = Flask(__name__) # En app se encuentra nuestro servidor web de Flask

# App.config:
app.config['SECRET_KEY'] = 'e_zc*u1so0sz38bx4+q&_$!2^5cgjy-w339qols-n@#osk=o!a' # Clave random para formularios de Flask-WTF.

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Ingrese en su cuenta para poder acceder al sistema.'
login_manager.login_message_category = 'info'

# Funciones:
@app.route('/')
def home():
    """ Función que lleva inicialmente a login_form.html """
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST']) # Página de ingreso en cuenta de usuario
def login():
    """ Función que lleva a index.html """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    error = None
    if form.validate_on_submit():
        email = request.form.get('email')
        # Comprobamos que hay un usuario con ese email
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.check_password(form.password.data): # Verificamos que la contraseña es correcta
            login_user(user, remember=form.remember_me.data) # Asignamos a login_user los datos verificados del formulario
            flash('Login correcto', 'success')

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            error = f'El nombre de usuario o contraseña no son correctos'
    return render_template('login_form.html', form=form, error=error)

@app.route('/logout') # Logout de usuario
@login_required
def logout():
    logout_user()
    flash("Ha salido de la aplicación, vuelva pronto!", 'success')
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

@login_manager.request_loader
def load_user(request):

    api_key = request.args.get('api_key')
    if api_key:
        user_load = User.query.filter_by(api_key=api_key).first()
        if user_load:
            return user_load

    return None

@login_manager.unauthorized_handler
def unauthorized():
    flash('No está autorizado a visitar esta página', 'error')
    return redirect(url_for('login'))

@app.route("/index/") # Página principal del programa
@login_required
def index():
    """ Función que lleva a index.html """
    # Consulta para saber el número de pedidos
    npedidos = db.session.query(Pedido).count()
    # Consulta para saber el número de clientes
    nusers = db.session.query(User).count()
    # Consulta para saber el número de proveedores
    nproveedores = db.session.query(Proveedor).count()
    # Consulta para saber el número de productos
    nproductos = db.session.query(Producto).count()

    # Grafica orders -> Pedidos por meses
    orders = db.session.query(db.func.sum(Pedido.total), (Pedido.mes_year)).group_by(Pedido.mes_year).order_by(
        Pedido.fecha).all()
    fechas = db.session.query(Pedido.mes_year).distinct().order_by(Pedido.fecha)
    orders_list = []
    fecha_list = []
    for registro, _ in orders:  # Generamos lista de datos para dashboard 'orders'
        orders_list.append(registro)
    for fecha in fechas:  # Generamos eje para dashboard 'orders'
        fecha_list.append(fecha[0])

    # Grafica ventas_proveedor -> Ventas por proveedor
    total = db.session.query(db.func.sum(Facturacion.total), (Facturacion.proveedor)).group_by(Facturacion.proveedor).\
        order_by(Facturacion.proveedor).all()
    proveedores = db.session.query(Proveedor.nombre, Facturacion.proveedor).filter(
        Facturacion.proveedor == Proveedor.id).order_by(Facturacion.proveedor).distinct()

    total_list = []
    proveedores_list = []
    for registro, _ in total:  # Generamos lista de datos para dashboard 'ventas_proveedor'
        total_list.append(registro)
    for proveedor in proveedores:  # Generamos eje para dashboard 'ventas_proveedor'
        proveedores_list.append(proveedor[0])
    print(total_list)
    print(proveedores_list)

    productoss = db.session.query(Producto).all()
    # Consulta para indicar el nombre del producto en vez de la id del producto
    proveedorid = db.session.query(Producto.id, Proveedor.nombre).filter(Proveedor.id == Producto.proveedor).all()
    # Consulta para indicar el nombre del almacén en vez de la id del almacén
    almacenid = db.session.query(Producto.id, Almacen.nombre).filter(Almacen.id == Producto.almacen).all()
    # Consulta que suma el número de pedidos de un mismo producto
    producto_pedido = db.session.query(Producto.referencia, Producto.nombre, db.func.sum(Pedido.cantidad)).group_by(
        Producto.referencia).filter(Pedido.referencia == Producto.referencia).order_by(db.func.sum(
        Pedido.cantidad).desc()).limit(5).all()
    producto_facturas = db.session.query(Producto.referencia, Producto.nombre, db.func.sum(Pedido.total)).group_by(
        Producto.referencia).filter(Pedido.referencia == Producto.referencia).order_by(
        db.func.sum(Pedido.total).desc()).all()
    # Consulta que suma el importe total de pedidos de un mismo producto
    producto_factura = db.session.query(Producto.referencia, Producto.nombre, db.func.sum(Pedido.total)).group_by(
        Producto.referencia).filter(Pedido.referencia == Producto.referencia).order_by(db.func.sum(Pedido.total).desc(
        )).limit(5).all()
    producto_pedidos = db.session.query(Producto.referencia, Producto.nombre, db.func.sum(Pedido.cantidad)).group_by(
        Producto.referencia).filter(Pedido.referencia == Producto.referencia).order_by(db.func.sum(
        Pedido.cantidad).desc()).all()

    return render_template("index.html", npedidos=npedidos, nusers=nusers, nproveedores=nproveedores,
                           nproductos=nproductos, orders_data=json.dumps(orders_list), fechas_data=json.dumps(fecha_list),
                           total_data=json.dumps(total_list), proveedores_data=json.dumps(proveedores_list),
                           productoss=productoss, proveedorid=proveedorid, almacenid=almacenid,
                           producto_pedido=producto_pedido, producto_facturas=producto_facturas,
                           producto_factura=producto_factura, producto_pedidos=producto_pedidos)

@app.route("/signup/", methods=["GET", "POST"]) # Darse de alta como cliente
def show_signup_form():
    """ Función que lleva a signup_form.html """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, surname=surname, email=email)
            user.set_password(password)
            user.save()
            flash('Usuario creado', 'success')
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)

@app.route("/crear-producto", methods=['GET', 'POST']) # Alta de nuevo producto
@login_required
def crear_producto():
    """ Función que lleva a new_product.html """
    form = NewProductForm()
    error = None
    form.proveedor.choices = get_choices(Proveedor) #Establecemos los elementos del menú Proveedores
    form.almacen.choices = get_choices(Almacen) #Establecemos los elementos del menú Almacenes

    if form.validate_on_submit():
        nombre = form.nombre.data
        referencia = form.referencia.data
        descripcion = form.descripcion.data
        proveedor = form.proveedor.data
        preciocoste = form.preciocoste.data
        pvp = form.pvp.data
        stock = form.stock.data
        almacen = form.almacen.data
        ubicacion = form.ubicacion.data
        descatalogado = form.descatalogado.data

        # Comprobamos que no hay ya un producto con esa referencia
        producto = db.session.query(Producto).filter_by(referencia=referencia).first()
        if producto is not None:
            error = f'El producto con referencia {referencia} ya está introducido en el sistema'
        else:
            # Creamos el producto y lo guardamos
            producto = Producto(nombre=nombre, referencia=referencia, descripcion=descripcion, proveedor=proveedor,
                                preciocoste=preciocoste, pvp=pvp, stock=stock, almacen=almacen, ubicacion=ubicacion,
                                descatalogado=descatalogado)
            producto.save()
            flash('Producto creado', 'success')
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("new_product.html", form=form, error=error)

@app.route("/crear-proveedor", methods=['GET', 'POST']) # Alta de nuevo proveedor
@login_required
def crear_proveedor():
    """ Función que lleva a new_supplier.html """
    form = NewSupplierForm()
    error = None
    if form.validate_on_submit():
        nombre=form.nombre.data
        telefono=form.telefono.data
        direccion=form.direccion.data
        cif=form.cif.data
        iva=form.iva.data
        descuento=form.descuento.data
        email=form.email.data

        # Comprobamos que no hay ya un proveedor con esa referencia
        proveedor = db.session.query(Proveedor).filter_by(cif=cif).first()
        if proveedor is not None:
            error = f'El proveedor {nombre} ya está dado de alta en el sistema'
        else:
            # Creamos el proveedor y lo guardamos
            proveedor = Proveedor(nombre=nombre, telefono=telefono, direccion=direccion, cif=cif, iva=iva,
                                  descuento=descuento, email=email)
            proveedor.save()
            flash('Proveedor creado', 'success')
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("new_supplier.html", form=form, error=error)

@app.route("/crear-pedido", methods=['GET', 'POST']) # Creación de nuevo pedido de cliente
@login_required
def crear_pedido():
    """ Función que lleva a new_order.html """
    form = NewOrderForm()
    error = None
    if form.validate_on_submit():
        item = db.session.query(Producto).filter_by(referencia=form.referencia.data).first()
        totalcalculado = item.pvp * form.cantidad.data

        fecha = form.fecha.data
        nombre = form.nombre.data
        referencia = form.referencia.data
        cantidad = form.cantidad.data
        total = totalcalculado
        mes = fecha.strftime("%m")
        year = fecha.strftime("%Y")
        mes_year = fecha.strftime("%m/%Y")

        # Comprobamos que existe la referencia en la base de datos, y si es así, si hay stock suficiente
        # o no está descatalogado
        producto = db.session.query(Producto).filter_by(referencia=referencia).first()
        if producto is None:
            error = f'El producto con referencia {referencia} no está dado de alta en el sistema'
        elif producto.stock < cantidad:
            error = f'No hay suficientes unidades en stock para realizar la venta'
        elif producto.descatalogado:
            error = f'El producto está descatalogado'
        else:
            # Creamos el pedido y lo guardamos
            pedido = Pedido(fecha=fecha, nombre=nombre, referencia=referencia, cantidad=cantidad, total=total, mes=mes,
                            year=year, mes_year=mes_year)
            pedido.save()
            # Reducimos stock de la tabla del producto
            producto.stock = producto.stock - cantidad
            producto.save()
            # Actualizamos la tabla facturacion
            facturacion = Facturacion(id_pedido=pedido.id, proveedor=producto.proveedor, referencia=referencia,
                                      cantidad=cantidad, total=total)
            facturacion.save()
            flash('Pedido creado', 'success')
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("new_order.html", form=form, error=error)

@app.route('/get_data', methods=['POST'])
def get_data():
    """ Función que devuelve los datos en la hoja de pedidos a proveedor """
    selected_item = request.form.get('selected_item')
    selected_nombre = request.form.get('selected_nombre')
    selected_cantidad = request.form.get('selected_cantidad')
    item_precio = request.form.get('item_precio')
    item_descuento = request.form.get('item_descuento')
    item_iva = request.form.get('item_iva')
    if selected_item:
        productoselect = db.session.query(Producto).filter(Producto.proveedor == selected_item).all()
        referencia_choices = get_choices2(productoselect)
        lista_referencias = []
        for referencia in referencia_choices:
            lista_referencias.append(referencia[1])
            data = {"items": lista_referencias}  # Lista de referencias por proveedor
        return jsonify(data)
    elif selected_nombre:
        nombreselect = db.session.query(Producto).filter(Producto.referencia == selected_nombre).all()
        for item in nombreselect:
            itemproveedor = item.proveedor
            data1 = (item.nombre, item.preciocoste)
        proveedorselect = db.session.query(Proveedor).filter(Proveedor.id == itemproveedor).all()
        for item in proveedorselect:
            data2 = (item.iva, item.descuento)
        data = data1 + data2
        return jsonify(data)
    elif selected_cantidad:
        data1 = int(item_precio) * int(selected_cantidad)
        descuento = round((data1 * (int(item_descuento)/100)), 2)
        data2 = round((data1 + ((data1 - descuento) * (int(item_iva) / 100))), 2)
        data = (data1, data2)
        return jsonify(data)

@app.route("/proveedor_order", methods=['GET', 'POST']) # Creación de nuevo pedido a proveedor
@login_required
def proveedor_order():
    """ Función que lleva a supplier_order.html """
    form = NewSupplierOrderForm()
    error = None
    form.proveedor.choices = get_choices(Proveedor)  # Establecemos los elementos del menú Proveedores

    if request.method == 'POST':
        fecha = form.fecha.data
        proveedor = request.form['proveedor_select']
        referencia = request.form['referencia_select']
        nombre = request.form['item_nombre']
        preciocoste = request.form['item_precio']
        cantidad = request.form['cantidad_select']
        total_precio = request.form['total_precio']
        descuento = request.form['item_descuento']
        iva = request.form['item_iva']
        total = request.form['total_pedido']

        # Comprobamos que el producto no está descatalogado
        producto = db.session.query(Producto).filter_by(referencia=referencia).first()
        if producto.descatalogado:
            error = f'El producto está descatalogado'
        else:
            # Creamos el pedido y lo guardamos
            pedido = PedidoProveedor(fecha=fecha, proveedor=proveedor, referencia=referencia,
                                     nombre=nombre, preciocoste=preciocoste, cantidad=cantidad, total_precio=total_precio,
                                     descuento=descuento, iva=iva, total=total)
            pedido.save()
            # Añadimos stock de la tabla del producto
            producto.stock = int(producto.stock) + int(cantidad)
            producto.save()
            flash('Pedido a proveedor creado', 'success')
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("supplier_order.html", form=form, error=error)

@app.route("/pedidos_proveedor") # Listado de pedidos
@login_required
def pedidos_proveedor():
    """ Función que lleva a sorder_history.html """
    entradas = db.session.query(PedidoProveedor).order_by(PedidoProveedor.fecha.desc()).all()
    return render_template("sorder_history.html", entradas=entradas)

@app.route("/historial") # Listado de pedidos
@login_required
def historial():
    """ Función que lleva a order_history.html """
    entradas = db.session.query(Pedido).order_by(Pedido.fecha.desc()).all()
    return render_template("order_history.html", entradas=entradas)

@app.route('/almacenes/<int:almacen_id>', methods=['GET', 'POST']) # Listado de contenido en almacenes
@login_required
def almacen(almacen_id):
    """ Función que lleva a store.html """
    nalmacen = db.session.query(Almacen.nombre).filter_by(id=almacen_id).scalar()
    # Consulta para indicar el nombre del proveedor en vez de la id del proveedor
    proveedorr = db.session.query(Producto.id, Proveedor.nombre).filter(Proveedor.id == Producto.proveedor).all()
    elementos = db.session.query(Producto).filter_by(almacen=almacen_id).all()
    return render_template("store.html", elementos=elementos, proveedorr=proveedorr, nalmacen=nalmacen)

@app.route("/productos") # Listado de productos
@login_required
def productos():
    """ Función que lleva a productos.html """
    entradas = db.session.query(Producto).all()
    # Consulta para indicar el nombre del producto en vez de la id del producto
    proveedorid = db.session.query(Producto.id, Proveedor.nombre).filter(Proveedor.id == Producto.proveedor).all()
    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template("products.html", entradas=entradas, sortparams=sortparams, proveedorid=proveedorid)

@app.route("/proveedores") # Listado de proveedores
@login_required
def proveedores():
    """ Función que lleva a supplier.html """
    entradas = db.session.query(Proveedor).all()
    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template("supplier.html", entradas=entradas, sortparams=sortparams)

@app.route("/usuarios") # Listado de usuarios
@login_required
def usuarios():
    """ Función que lleva a users.html """
    users = db.session.query(User).all()
    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template("users.html", users=users, sortparams=sortparams)

@app.route('/view/<int:entrada_id>', methods=['GET']) # Visualización de producto
@login_required
def view_product(entrada_id):
    """ Función que lleva a show_item.html """
    form = NewProductForm()
    view_item = 'ver_producto' # Variable para seleccionar que datos mostrar
    product = db.session.query(Producto).filter_by(id=entrada_id)
    # Consulta para indicar el nombre del producto en vez de la id del producto
    proveedorid = db.session.query(Producto.id, Proveedor.nombre).filter(Proveedor.id == Producto.proveedor).all()
    # Consulta para indicar el nombre del almacén en vez de la id del almacén
    almacenid = db.session.query(Producto.id, Almacen.nombre).filter(Almacen.id == Producto.almacen).all()
    return render_template('show_item.html', view_item=view_item, product=product, proveedorid=proveedorid,
                           almacenid=almacenid, form=form)

@app.route('/viewu/<int:entrada_id>', methods=['GET']) # Visualización de usuario
@login_required
def view_user(entrada_id):
    """ Función que lleva a show_item.html """
    form = SignupForm()
    view_item = 'ver_cliente' # Variable para seleccionar que datos mostrar
    users = db.session.query(User).filter_by(id=entrada_id)
    return render_template('show_item.html', view_item=view_item, users=users, form=form)

@app.route('/views/<int:entrada_id>', methods=['GET']) # Visualización de proveedor
@login_required
def view_supplier(entrada_id):
    """ Función que lleva a show_item.html """
    form = NewSupplierForm()
    view_item = 'ver_proveedor' # Variable para seleccionar que datos mostrar
    supplier = db.session.query(Proveedor).filter_by(id=entrada_id)
    return render_template('show_item.html', view_item=view_item, supplier=supplier, form=form)

@app.route('/edits/<int:entrada_id>', methods=['GET', 'POST']) # Edición de proveedor
@login_required
def edits(entrada_id):
    """ Función que lleva a edit.html """
    form = NewSupplierForm()
    edit_item = 'editar_proveedor'  # Variable para seleccionar que datos mostrar
    supplier = db.session.query(Proveedor).filter_by(id=entrada_id).first()

    if request.method == 'POST' and form.validate_on_submit():
        supplier.id = request.form['id']
        # Modificamos los registros del proveedor y lo guardamos
        supplier.nombre = form.nombre.data
        supplier.telefono = form.telefono.data
        supplier.direccion = form.direccion.data
        supplier.cif = form.cif.data
        supplier.iva = form.iva.data
        supplier.descuento = form.descuento.data
        supplier.email = form.email.data
        db.session.commit()
        flash('Proveedor editado con éxito', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('proveedores')
        return redirect(next_page)
    return render_template('edit.html', edit_item=edit_item, supplier=supplier, form=form, entrada_id=entrada_id)

@app.route("/editp/<int:entrada_id>", methods=['GET', 'POST']) # Edición de producto
@login_required
def editp(entrada_id):
    """ Función que lleva a edit.html """
    form = NewProductForm()
    edit_item = 'editar_producto'  # Variable para seleccionar que datos mostrar
    choices = get_choices(Proveedor)  # Establecemos los elementos del menú Proveedores
    choices2 = get_choices(Almacen)  # Establecemos los elementos del menú Almacenes
    form.proveedor.choices = choices
    form.almacen.choices = choices2
    product = db.session.query(Producto).filter_by(id=entrada_id).first()
    if request.method == 'POST' and form.validate_on_submit():
        product.id = request.form['id']
        # Modificamos los registros del proveedor y lo guardamos
        product.nombre = form.nombre.data
        product.referencia = form.referencia.data
        product.descripcion = form.descripcion.data
        product.proveedor = form.proveedor.data
        product.preciocoste = form.preciocoste.data
        product.pvp = form.pvp.data
        product.stock = form.stock.data
        product.almacen = form.almacen.data
        product.ubicacion = form.ubicacion.data
        product.descatalogado = form.descatalogado.data
        db.session.commit()
        flash('Producto editado con éxito', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('productos')
        return redirect(next_page)
    return render_template('edit.html', edit_item=edit_item, product=product, form=form, entrada_id=entrada_id)

@app.route('/editu/<int:entrada_id>', methods=['GET', 'POST']) # Edición de usuario
@login_required
def editu(entrada_id):
    """ Función que lleva a edit.html """
    form = SignupForm()
    edit_item = 'editar_cliente'  # Variable para seleccionar que datos mostrar
    users = db.session.query(User).filter_by(id=entrada_id).first()
    print(users.id)
    if request.method == 'POST' and form.validate_on_submit():
        users.id = request.form['id']
        # Modificamos los registros del usuario y lo guardamos
        users.name = form.name.data
        users.surname = form.surname.data
        users.email = form.email.data
        users.password = request.form['password']
        users.is_admin = form.is_admin.data
        db.session.commit()
        flash('Cliente editado con éxito', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('usuarios')
        return redirect(next_page)
    return render_template('edit.html', edit_item=edit_item, users=users, form=form, entrada_id=entrada_id)

@app.route("/delete/<int:entrada_id>") # Borrar pedido
@login_required
def delete(entrada_id):
    """ Función que borra un pedido """
    pedido = db.session.query(Pedido).filter_by(id=entrada_id).first()
    producto = db.session.query(Producto).filter_by(referencia=pedido.referencia).first()
    # Añadimos el stock de la tabla del producto
    producto.stock = producto.stock + pedido.cantidad
    print(producto.stock)
    producto.save()
    # Actualizamos la tabla facturacion
    factura = db.session.query(Facturacion).filter_by(id_pedido=entrada_id).first()
    print(factura)
    db.session.delete(factura)
    db.session.delete(pedido)
    db.session.commit()
    flash('Pedido borrado con éxito', 'success')
    return redirect(url_for('historial'))

@app.route("/dashboard/") # Página de informes
@login_required
def dashboard():
    """ Función que lleva a dashboard.html """
    # Consulta para saber el número de pedidos
    numpedidos = db.session.query(Pedido).count()
    # Consulta para saber el número de productos
    numproductos = db.session.query(Producto).count()
    # Grafica orders -> Facturación por meses
    orders = db.session.query(db.func.sum(Pedido.total), (Pedido.mes_year)).group_by(Pedido.mes_year).order_by(
        Pedido.fecha).all()
    fechas = db.session.query(Pedido.mes_year).distinct().order_by(Pedido.fecha)
    orders_list = []
    fecha_list = []
    for registro, _ in orders: # Generamos lista de datos para dashboard 'orders'
        orders_list.append(registro)
    for fecha in fechas: #Generamos eje para dashboard 'orders'
        fecha_list.append(fecha[0])
    # Grafica num_products -> Nº de productos vendidos por meses
    nproducts = db.session.query(db.func.sum(Pedido.cantidad), (Pedido.mes_year)).group_by(Pedido.mes_year).order_by(
        Pedido.fecha).all()
    nproducts_list = []
    for registro, _ in nproducts:  # Generamos lista de datos para dashboard 'orders'
        nproducts_list.append(registro)

    # Grafica stock -> Stock de productos
    productos = db.session.query(Producto.referencia).order_by(Producto.referencia)
    stock = db.session.query(Producto.stock).order_by(Producto.referencia)
    productos_list = []
    stock_list = []
    for producto in productos:  # Generamos lista de datos para dashboard 'stock'
        productos_list.append(producto[0])
    for item in stock:  # Generamos eje para dashboard 'stock'
        stock_list.append(item[0])
    # Grafica ventas_proveedor -> Facturación por proveedor
    total = db.session.query(db.func.sum(Facturacion.total), (Facturacion.proveedor)).group_by(Facturacion.proveedor).\
        order_by(Facturacion.proveedor).all()
    proveedores = db.session.query(Proveedor.nombre, Facturacion.proveedor).filter(
        Facturacion.proveedor == Proveedor.id).order_by(Facturacion.proveedor).distinct()

    total_list = []
    proveedores_list = []
    for registro, _ in total:  # Generamos lista de datos para dashboard 'ventas_proveedor'
        total_list.append(registro)
    for proveedor in proveedores:  # Generamos eje para dashboard 'ventas_proveedor'
        proveedores_list.append(proveedor[0])
    # Gráfica factura_proveedor -> Beneficio por proveedor
    bproducts = db.session.query(Producto.referencia, Producto.pvp, Producto.preciocoste).group_by(
        Producto.referencia).order_by(Producto.referencia).all()
    bproducts_list = []
    for f in bproducts:
        beneficio = f[1] - f[2]
        bproducts_list.append((f[0], beneficio))
    proveedoresf = db.session.query(Proveedor.nombre, Facturacion.referencia, Facturacion.cantidad).filter(
        Facturacion.proveedor == Proveedor.id).group_by(Facturacion.referencia).order_by(Facturacion.referencia).all()
    beneficios_list = []
    for i in proveedoresf:
        for j in bproducts_list:
            if i[1] == j[0]:
                beneficio = j[1] * i[2]
                beneficios_list.append((i[0], beneficio))
    totalb = []
    for provee in proveedores_list:
        totalp = 0
        for beneficiopedido in beneficios_list:
            if provee == beneficiopedido[0]:
                totalp += beneficiopedido[1]
        totalb.append(totalp)

    #Porcentaje de beneficio por proveedor
    porcentaje_beneficio = []
    for bene, factu in zip(totalb, total_list):
        beneficioproveedor = round(((bene*100)/factu), 2)
        porcentaje_beneficio.append(beneficioproveedor)

    # Consulta para saber la facturación total
    totfactura = db.session.query(db.func.sum(Facturacion.total)).scalar()
    tfactura='{:,}'.format(totfactura).replace(',', '.')
    # Consulta para saber el beneficio total
    tbeneficio = round(((sum(totalb)*100)/sum(total_list)), 2)


    print(totalb)
    print(proveedores_list)
    print(total_list)
    print(porcentaje_beneficio)
    return render_template("dashboard.html", orders_data=json.dumps(orders_list), fechas_data=json.dumps(fecha_list),
                           nproducts_data=json.dumps(nproducts_list), beneficios_data=json.dumps(totalb),
                           productos_data=json.dumps(productos_list), stock_data=json.dumps(stock_list),
                           total_data=json.dumps(total_list), proveedores_data=json.dumps(proveedores_list),
                           pbeneficio_data=json.dumps(porcentaje_beneficio), numpedidos=numpedidos,
                           numproductos=numproductos, tbeneficio=tbeneficio, tfactura=tfactura)

@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('home'))

@app.errorhandler(404)
def status_404(error):
    return '<h1>Página no encontrada YO</h1>', 404

if __name__ == '__main__':
    # En la siguiente línea estamos indicando a SQLAlchemy que cree, si no existe, las tablas
    # de todos los modelos que encuentre en models.py
    db.Base.metadata.create_all(db.engine)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True) # El debug=True hace que cada vez que reiniciemos el servidor, o modifiquemos el código, el
    #servidor de Flask se reinicie solo. Es un modo de producción que nos va a dar más datos.
    # Al terminar habrá que quitarlo.

