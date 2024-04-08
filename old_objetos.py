from models import Almacen, Proveedor


almacen_1 = Almacen(
    id="1",
    nombre="Almacen 1",
)

almacen_2 = Almacen(
    id="2",
    nombre="Almacen 2",
)

almacen_3 = Almacen(
    id="3",
    nombre="Tienda",
)

proveedor_1 = Proveedor(
    id="1",
    nombre="ASUS",
    telefono="657356941",
    direccion="c/ Rios Rosas 23",
    cif="G-63482175",
    iva="21",
    descuento="5",
    facturacion="",
)

proveedor_2 = Proveedor(
    id="2",
    nombre="Samsung",
    telefono="632941756",
    direccion="Av. de la Industria 54",
    cif="G-862514783",
    iva="21",
    descuento="9",
    facturacion="",
)

proveedor_3 = Proveedor(
    id="3",
    nombre="HP",
    telefono="634759821",
    direccion="c/ Castellana 123",
    cif="G-32548752",
    iva="21",
    descuento="3",
    facturacion="",
)

'''
INSERT INTO proveedores (nombre, telefono, direccion, cif, iva, descuento, facturacion)
VALUES ('ASUS', '657356941', 'c/ Rios Rosas 23', 'G-63482175', '21', '5', '')

INSERT INTO proveedores (nombre, telefono, direccion, cif, iva, descuento, facturacion)
VALUES ('Samsung', '632941756', 'Av. de la Industria 54', 'G-862514783', '21', '9', '')

INSERT INTO proveedores (nombre, telefono, direccion, cif, iva, descuento, facturacion)
VALUES ('HP', '634759821', 'c/ Castellana 123', 'G-32548752', '21', '3', '')
    
'''