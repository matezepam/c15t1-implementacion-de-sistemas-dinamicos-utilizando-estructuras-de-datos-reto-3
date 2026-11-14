# INTERFAZ DE CONSOLA
# Las lecturas y la presentación se separan de las reglas para poder probar
# el sistema sin escribir datos por teclado ni repetir validaciones de negocio.

from SISTEMA import Floristeria, calcular_total, validar_texto, validar_precio


def leer_texto(mensaje):
    while True:
        try:
            return validar_texto(input(mensaje), 'El texto')
        except ValueError as error:
            print('Error:', error)


# Repetir la lectura evita que letras, decimales o valores negativos cierren el
# programa. El menú, en cambio, compara texto y no necesita convertir su opción.
def leer_entero(mensaje, minimo=0):
    while True:
        try:
            numero = int(input(mensaje))
        except ValueError:
            print('Escriba un número entero')
            continue
        if numero >= minimo:
            return numero
        print(f'El valor debe ser mayor o igual que {minimo}')


def leer_precio():
    while True:
        try:
            return validar_precio(input('Precio unitario USD: '))
        except ValueError as error:
            print('Error:', error)


def mostrar_inventario(sistema):
    print('\nINVENTARIO DISPONIBLE')
    productos = sistema.productos()
    if not productos:
        print('No hay flores registradas')
    for producto in productos:
        print(f"{producto['codigo']} | {producto['nombre']} | "
              f"Disponible: {producto['stock']} | USD {producto['precio']:.2f}")


# Muestra pendientes y atendidos con el mismo formato, sin reordenarlos.
# Así se puede comprobar el orden FIFO de la cola y el LIFO del historial.
def mostrar_pedidos(pedidos, titulo):
    print('\n' + titulo)
    if not pedidos:
        print('No hay pedidos')
    for pedido in pedidos:
        print(f"Pedido {pedido['id']} | {pedido['cliente']} | "
              f"{pedido['codigo']} {pedido['flor']} | Cantidad: {pedido['cantidad']} | "
              f"Total: USD {calcular_total(pedido):.2f}")
        print('Creado:', pedido['creado_en'].isoformat(timespec='seconds'),
              '| Actualizado:', pedido['actualizado_en'].isoformat(timespec='seconds'))


# El menú llama a las reglas del inventario sin repetir sus validaciones.
# Capturar los datos inválidos permite informar el error y continuar la sesión.
def menu_inventario(sistema):
    while True:
        print('\nINVENTARIO\n1. Registrar flor\n2. Mostrar inventario'
              '\n3. Editar flor\n4. Eliminar flor\n0. Volver')
        opcion = input('Opción: ').strip()
        try:
            if opcion == '0':
                return
            elif opcion == '1' or opcion == '3':
                codigo = leer_texto('Código: ')
                nombre = leer_texto('Nombre de la flor: ')
                stock = leer_entero('Unidades disponibles: ')
                precio = leer_precio()
                if opcion == '1':
                    sistema.registrar_producto(codigo, nombre, stock, precio)
                    print('Flor registrada')
                else:
                    # El stock introducido es el disponible, sin incluir las
                    # unidades que ya se reservaron para pedidos pendientes.
                    sistema.editar_producto(codigo, nombre, stock, precio)
                    print('Flor actualizada')
            elif opcion == '2':
                mostrar_inventario(sistema)
            elif opcion == '4':
                codigo = leer_texto('Código de la flor a eliminar: ')
                if input('¿Confirma la eliminación? [s/n]: ').strip().lower() == 's':
                    sistema.eliminar_producto(codigo)
                    print('Flor eliminada')
                else:
                    print('Eliminación cancelada')
            else:
                print('Seleccione una opción del menú')
        except ValueError as error:
            print('Error:', error)


# Registra y modifica pendientes, o atiende directamente al primero de la cola.
# Confirmar una cancelación evita devolver stock por una selección accidental.
def menu_pedidos(sistema):
    while True:
        print('\nPEDIDOS\n1. Registrar pedido\n2. Mostrar pendientes'
              '\n3. Editar pedido pendiente\n4. Cancelar pedido'
              '\n5. Atender siguiente\n6. Mostrar atendidos\n0. Volver')
        opcion = input('Opción: ').strip()
        try:
            if opcion == '0':
                return
            elif opcion in ('1', '3'):
                identificador = leer_entero('ID del pedido: ', 1) if opcion == '3' else None
                cliente = leer_texto('Cliente: ')
                codigo = leer_texto('Código de la flor: ')
                cantidad = leer_entero('Unidades solicitadas: ', 1)
                if opcion == '1':
                    pedido = sistema.registrar_pedido(cliente, codigo, cantidad)
                else:
                    pedido = sistema.editar_pedido(identificador, cliente, codigo, cantidad)
                print(f"Pedido {pedido['id']} pendiente | Total: USD {calcular_total(pedido):.2f}")
            elif opcion == '2':
                mostrar_pedidos(sistema.pedidos_pendientes(), 'PENDIENTES EN ORDEN FIFO')
            elif opcion == '4':
                identificador = leer_entero('ID del pedido a cancelar: ', 1)
                if input('¿Cancelar y devolver sus unidades? [s/n]: ').strip().lower() == 's':
                    sistema.cancelar_pedido(identificador)
                    print('Pedido cancelado y stock devuelto')
                else:
                    print('Cancelación no confirmada')
            elif opcion == '5':
                pedido = sistema.atender_siguiente()
                print(f"Atendido: pedido {pedido['id']} de {pedido['cliente']}")
            elif opcion == '6':
                mostrar_pedidos(sistema.pedidos_atendidos(), 'ATENDIDOS: DEL MÁS RECIENTE AL MÁS ANTIGUO')
            else:
                print('Seleccione una opción del menú')
        except (ValueError, IndexError) as error:
            print('Error:', error)


def principal():
    sistema = Floristeria()
    print('FLORISTERÍA · INVENTARIO Y PEDIDOS')
    print('Los pedidos reservan stock al registrarse. Los datos duran esta sesión.')
    try:
        while True:
            print('\nMENÚ PRINCIPAL\n1. Inventario\n2. Pedidos'
                  '\n3. Consultar última atención\n0. Salir')
            opcion = input('Opción: ').strip()
            if opcion == '0':
                print('Sesión finalizada. Los datos no se guardan en disco.')
                return
            elif opcion == '1':
                menu_inventario(sistema)
            elif opcion == '2':
                menu_pedidos(sistema)
            elif opcion == '3':
                try:
                    mostrar_pedidos([sistema.ultimo_atendido()], 'ÚLTIMO PEDIDO ATENDIDO')
                except IndexError as error:
                    print('Error:', error)
            else:
                print('Seleccione una opción del menú')
    except (EOFError, KeyboardInterrupt):
        print('\nSesión interrumpida. Los datos no se guardan en disco.')


if __name__ == '__main__':
    principal()
