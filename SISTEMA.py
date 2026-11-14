# REGLAS DEL INVENTARIO Y LOS PEDIDOS
# Conserva registro, edición y eliminación de los retos anteriores, cambiando
# el almacenamiento e incorporando atención FIFO e historial mediante una pila.

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext

from ESTRUCTURAS import ListaEnlazada, Pila, Cola


ZONA_HORARIA = timezone(timedelta(hours=-5))
PRECIO_MAXIMO = Decimal('999999999.99')


def validar_texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f'{campo} no puede estar vacío')
    return ' '.join(valor.split())


def validar_cantidad(valor, minimo=0):
    if type(valor) is not int or valor < minimo:
        raise ValueError(f'La cantidad debe ser un entero mayor o igual que {minimo}')
    return valor


# Decimal recibe texto para evitar aproximaciones de float al trabajar con
# dinero. Se permiten comas, pero no precios no finitos ni fracciones de centavo.
def validar_precio(valor):
    if type(valor) not in (str, int, Decimal):
        raise ValueError('Escriba el precio como texto, entero o Decimal')
    try:
        precio = Decimal(valor.replace(',', '.') if isinstance(valor, str) else valor)
    except (InvalidOperation, ValueError):
        raise ValueError('El precio debe ser numérico') from None
    if not precio.is_finite() or not 0 < precio <= PRECIO_MAXIMO:
        raise ValueError(f'El precio debe ser positivo y no superar {PRECIO_MAXIMO}')
    with localcontext() as contexto:
        contexto.prec = 28
        centavos = precio.quantize(Decimal('0.01'))
    if centavos != precio:
        raise ValueError('El precio admite como máximo dos decimales')
    return centavos


# Multiplica la cantidad por el precio acordado. La precisión se ajusta para
# conservar centavos incluso con cantidades grandes, sin usar float para dinero.
def calcular_total(pedido):
    with localcontext() as contexto:
        contexto.prec = max(28, len(str(pedido['cantidad'])) + 14)
        return pedido['precio_unitario'] * pedido['cantidad']


# La lista organiza productos, la cola conserva turnos y la pila guarda atenciones.
# Cada estructura se utiliza según el orden que necesita esa parte del sistema.
class Floristeria:
    def __init__(self):
        self.inventario = ListaEnlazada()
        self.pendientes = Cola()
        self.atendidos = Pila()
        self._siguiente_id = 1

    def _buscar_producto(self, codigo):
        codigo = validar_texto(codigo, 'El código').upper()
        for posicion, producto in enumerate(self.inventario):
            if producto['codigo'] == codigo:
                return posicion, producto
        raise ValueError('El producto no existe')

    def _buscar_pedido(self, identificador):
        validar_cantidad(identificador, 1)
        for posicion, pedido in enumerate(self.pendientes):
            if pedido['id'] == identificador:
                return posicion, pedido
        raise ValueError('El pedido no está pendiente')

    def _validar_nombre_unico(self, nombre, codigo=None):
        for producto in self.inventario:
            if producto['codigo'] != codigo and producto['nombre'].casefold() == nombre.casefold():
                raise ValueError('La flor ya está registrada con otro código')

    # Las consultas devuelven copias para que la interfaz no modifique el stock
    # directamente, saltándose las validaciones del sistema.
    def productos(self):
        return [dict(producto) for producto in self.inventario]

    def pedidos_pendientes(self):
        return [dict(pedido) for pedido in self.pendientes]

    def pedidos_atendidos(self):
        return [dict(pedido) for pedido in self.atendidos.en_orden()]

    # Valida los datos y comprueba código y nombre antes de añadir el nodo.
    # Rechazar duplicados evita repartir el stock de una flor en varios registros.
    def registrar_producto(self, codigo, nombre, stock, precio):
        codigo = validar_texto(codigo, 'El código').upper()
        nombre = validar_texto(nombre, 'La flor')
        stock = validar_cantidad(stock)
        precio = validar_precio(precio)
        for producto in self.inventario:
            if producto['codigo'] == codigo:
                raise ValueError('Código repetido; use editar para reponer existencias')
        self._validar_nombre_unico(nombre)
        nuevo = dict(codigo=codigo, nombre=nombre, stock=stock, precio=precio)
        self.inventario.agregar(nuevo)
        return dict(nuevo)

    # Todos los campos se validan antes de escribir los cambios para que un
    # precio inválido no deje aplicado únicamente el nuevo stock.
    def editar_producto(self, codigo, nombre, stock, precio):
        _, producto = self._buscar_producto(codigo)
        nombre = validar_texto(nombre, 'La flor')
        stock = validar_cantidad(stock)
        precio = validar_precio(precio)
        self._validar_nombre_unico(nombre, producto['codigo'])
        producto.update(nombre=nombre, stock=stock, precio=precio)
        return dict(producto)

    # Un pedido pendiente necesita su producto para devolver unidades al cancelar.
    # Por eso se bloquea la eliminación mientras existan reservas de esa flor.
    def eliminar_producto(self, codigo):
        posicion, producto = self._buscar_producto(codigo)
        for pedido in self.pendientes:
            if pedido['codigo'] == producto['codigo']:
                raise ValueError('Cancele los pedidos pendientes de esta flor antes de eliminarla')
        eliminado = self.inventario.eliminar(posicion)
        return dict(eliminado)

    # Reservar antes de atender evita ofrecer las mismas unidades a otro cliente.
    # El pedido se añade al final para respetar el orden de llegada.
    def registrar_pedido(self, cliente, codigo, cantidad):
        cliente = validar_texto(cliente, 'El cliente')
        cantidad = validar_cantidad(cantidad, 1)
        _, producto = self._buscar_producto(codigo)
        if cantidad > producto['stock']:
            raise ValueError('No hay stock suficiente')
        momento = datetime.now(ZONA_HORARIA)
        # Guarda nombre y precio acordados para que editar el catálogo no cambie
        # los datos de una compra que ya fue registrada.
        pedido = dict(id=self._siguiente_id, cliente=cliente, codigo=producto['codigo'],
                      flor=producto['nombre'], cantidad=cantidad,
                      precio_unitario=producto['precio'], creado_en=momento,
                      actualizado_en=momento)
        producto['stock'] -= cantidad
        self.pendientes.enqueue(pedido)
        self._siguiente_id += 1
        return dict(pedido)

    # Cuenta la reserva propia al comprobar la nueva cantidad, evitando rechazar
    # unidades que ya pertenecen al pedido. Su posición en la cola se conserva.
    def editar_pedido(self, identificador, cliente, codigo, cantidad):
        _, pedido = self._buscar_pedido(identificador)
        cliente = validar_texto(cliente, 'El cliente')
        cantidad = validar_cantidad(cantidad, 1)
        _, anterior = self._buscar_producto(pedido['codigo'])
        _, nuevo = self._buscar_producto(codigo)
        disponibles = nuevo['stock'] + (pedido['cantidad'] if anterior is nuevo else 0)
        if cantidad > disponibles:
            raise ValueError('No hay stock suficiente para editar el pedido')
        precio = pedido['precio_unitario'] if anterior is nuevo else nuevo['precio']
        # Ajusta ambas reservas sólo después de validar, para que un rechazo
        # no deje cantidades descontadas ni devueltas parcialmente.
        anterior['stock'] += pedido['cantidad']
        nuevo['stock'] -= cantidad
        pedido.update(cliente=cliente, codigo=nuevo['codigo'], flor=nuevo['nombre'],
                      cantidad=cantidad, precio_unitario=precio,
                      actualizado_en=datetime.now(ZONA_HORARIA))
        return dict(pedido)

    # Cancela por ID y devuelve las unidades reservadas para poder venderlas otra vez.
    # Los demás pedidos conservan su orden aunque se retire uno intermedio.
    def cancelar_pedido(self, identificador):
        posicion, pedido = self._buscar_pedido(identificador)
        _, producto = self._buscar_producto(pedido['codigo'])
        self.pendientes.eliminar(posicion)
        producto['stock'] += pedido['cantidad']
        return dict(pedido)

    # Retira el primero y lo apila como la atención más reciente: FIFO al atender
    # y LIFO en el historial. No descuenta stock porque ya estaba reservado.
    def atender_siguiente(self):
        pedido = self.pendientes.dequeue()
        self.atendidos.push(dict(pedido))
        return dict(pedido)

    # Consulta el tope sin retirar la atención. Devuelve una copia para que
    # la interfaz no pueda cambiar el pedido guardado al mostrar su información.
    def ultimo_atendido(self):
        return dict(self.atendidos.peek())
