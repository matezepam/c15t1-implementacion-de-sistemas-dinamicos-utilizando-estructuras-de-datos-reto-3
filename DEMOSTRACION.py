# EJEMPLO REPRODUCIBLE SIN INGRESAR DATOS POR TECLADO
# Usa las funciones del menú con datos definidos para comprobar las reservas,
# el orden de atención y el historial sin introducir cada dato por teclado.

from SISTEMA import Floristeria, calcular_total


def mostrar_estado(sistema):
    print('Stock:', [(p['codigo'], p['stock']) for p in sistema.productos()])
    print('Pendientes:', [(p['id'], p['cliente']) for p in sistema.pedidos_pendientes()])


def demostracion():
    sistema = Floristeria()
    print('1. INVENTARIO CON LISTA ENLAZADA')
    sistema.registrar_producto('R01', 'Rosas', 20, '1.50')
    sistema.registrar_producto('T01', 'Tulipanes', 12, '2.00')
    sistema.editar_producto('T01', 'Tulipanes', 15, '2.25')
    mostrar_estado(sistema)

    print('\n2. REGISTRO DE PEDIDOS CON COLA FIFO')
    sistema.registrar_pedido('Paulo', 'R01', 4)
    sistema.registrar_pedido('Mateo', 'T01', 3)
    sistema.registrar_pedido('Sofía', 'R01', 2)
    for pedido in sistema.pedidos_pendientes():
        print(f"Pedido {pedido['id']} de {pedido['cliente']} | USD {calcular_total(pedido):.2f}")
    mostrar_estado(sistema)
    try:
        sistema.registrar_pedido('Pedro', 'R01', 100)
    except ValueError as error:
        print('Pedido rechazado:', error)
    try:
        sistema.eliminar_producto('R01')
    except ValueError as error:
        print('Eliminación rechazada:', error)

    print('\n3. EDICIÓN Y CANCELACIÓN DE PEDIDOS')
    sistema.editar_pedido(2, 'Mateo', 'T01', 2)
    print('Mateo cambia su cantidad de 3 a 2; conserva su posición:')
    mostrar_estado(sistema)
    sistema.cancelar_pedido(3)
    print('Sofía cancela y se devuelven sus 2 rosas:')
    mostrar_estado(sistema)

    print('\n4. ATENCIÓN FIFO E HISTORIAL CON PILA')
    while not sistema.pendientes.is_empty():
        print('Atendido:', sistema.atender_siguiente()['cliente'])
    print('Último atendido sin extraer:', sistema.ultimo_atendido()['cliente'])
    print('Historial del más reciente al más antiguo:',
          [p['cliente'] for p in sistema.pedidos_atendidos()])
    mostrar_estado(sistema)
    try:
        sistema.atender_siguiente()
    except IndexError as error:
        print('Cola vacía:', error)

    print('\n5. ELIMINACIÓN DE UNA FLOR SIN PENDIENTES')
    sistema.eliminar_producto('T01')
    print('Flores conservadas:', [p['codigo'] for p in sistema.productos()])
    print('El historial conserva el pedido de Mateo y su precio original.')


if __name__ == '__main__':
    demostracion()
