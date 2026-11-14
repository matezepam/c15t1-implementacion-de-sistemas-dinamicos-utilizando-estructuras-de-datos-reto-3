# Las pruebas comprueban el resultado y los casos límite de las estructuras,
# además de verificar reservas, atención FIFO e historial de atenciones LIFO.

from collections import deque
from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
import random
import unittest

from ESTRUCTURAS import ListaEnlazada, Pila, Cola
from SISTEMA import Floristeria, calcular_total, validar_precio
from PRINCIPAL import principal


class Estructuras(unittest.TestCase):
    def test_lista_posiciones_y_final(self):
        lista = ListaEnlazada()
        lista.insertar(0, 'B')
        lista.insertar(0, 'A')
        lista.insertar(2, 'D')
        lista.insertar(2, 'C')
        self.assertEqual(list(lista), ['A', 'B', 'C', 'D'])
        self.assertEqual(lista.obtener(2), 'C')
        self.assertEqual(lista.eliminar(3), 'D')
        self.assertEqual(lista.final.dato, 'C')
        self.assertEqual(lista.eliminar(1), 'B')
        self.assertEqual(lista.eliminar(0), 'A')
        self.assertEqual(lista.eliminar(0), 'C')
        self.assertIsNone(lista.cabeza)
        self.assertIsNone(lista.final)
        lista.agregar('E')
        self.assertIs(lista.cabeza, lista.final)
        self.assertEqual(lista.size(), 1)

    def test_posiciones_invalidas(self):
        lista = ListaEnlazada()
        for indice in (-1, 1, True, '0'):
            with self.assertRaises(IndexError):
                lista.insertar(indice, 'A')
        with self.assertRaises(IndexError):
            lista.obtener(0)
        with self.assertRaises(IndexError):
            lista.eliminar(0)

    def test_lista_operaciones_intercaladas(self):
        azar = random.Random(15)
        lista = ListaEnlazada()
        referencia = []
        for numero in range(300):
            if not referencia or azar.random() < 0.6:
                posicion = azar.randrange(len(referencia) + 1)
                lista.insertar(posicion, numero)
                referencia.insert(posicion, numero)
            else:
                posicion = azar.randrange(len(referencia))
                self.assertEqual(lista.eliminar(posicion), referencia.pop(posicion))
            self.assertEqual(list(lista), referencia)
            self.assertEqual(lista.size(), len(referencia))
            self.assertEqual(lista.final.dato if lista.final else None,
                             referencia[-1] if referencia else None)

    def test_pila_lifo_y_vacia(self):
        pila = Pila()
        for valor in ('A', None, 'C'):
            pila.push(valor)
        self.assertEqual(pila.peek(), 'C')
        self.assertEqual(pila.size(), 3)
        self.assertEqual([pila.pop(), pila.pop(), pila.pop()], ['C', None, 'A'])
        self.assertTrue(pila.is_empty())
        for operacion in (pila.pop, pila.peek):
            with self.assertRaises(IndexError):
                operacion()

    def test_cola_fifo_consulta_y_reutilizacion(self):
        cola = Cola()
        for valor in ('A', 'B', 'C'):
            cola.enqueue(valor)
        self.assertEqual(cola.front(), 'A')
        self.assertEqual(cola.size(), 3)
        self.assertEqual([cola.dequeue() for _ in range(3)], ['A', 'B', 'C'])
        self.assertIsNone(cola.final)
        for operacion in (cola.front, cola.dequeue):
            with self.assertRaises(IndexError):
                operacion()
        cola.enqueue('D')
        self.assertEqual(cola.dequeue(), 'D')

    def test_cola_operaciones_intercaladas(self):
        cola = Cola()
        referencia = deque()
        azar = random.Random(16)
        for numero in range(300):
            if not referencia or azar.random() < 0.6:
                cola.enqueue(numero)
                referencia.append(numero)
            else:
                self.assertEqual(cola.dequeue(), referencia.popleft())
            self.assertEqual(list(cola), list(referencia))
            self.assertEqual(cola.size(), len(referencia))


class Sistema(unittest.TestCase):
    def setUp(self):
        self.sistema = Floristeria()
        self.sistema.registrar_producto('R', 'Rosas', 20, '1.50')
        self.sistema.registrar_producto('T', 'Tulipanes', 12, '2.00')

    def estado(self):
        return (self.sistema.productos(), self.sistema.pedidos_pendientes(),
                self.sistema.pedidos_atendidos())

    def stock(self, codigo):
        return next(p['stock'] for p in self.sistema.productos() if p['codigo'] == codigo)

    def test_decimales_y_validaciones(self):
        self.assertEqual(validar_precio('0,10'), Decimal('0.10'))
        for invalido in ('NaN', 'Infinity', '-1', '0', '1.001', 'abc', True, 1.5,
                         '1000000000.00'):
            with self.assertRaises(ValueError):
                validar_precio(invalido)

    def test_codigo_y_nombre_duplicados(self):
        anterior = self.estado()
        for codigo, nombre in [('r', 'Otra'), ('X', ' ROSAS ')]:
            with self.assertRaises(ValueError):
                self.sistema.registrar_producto(codigo, nombre, 1, '1')
        self.assertEqual(self.estado(), anterior)

    def test_datos_invalidos_no_cambian_estado(self):
        anterior = self.estado()
        operaciones = [
            lambda: self.sistema.registrar_producto('', 'Flor', 1, '1'),
            lambda: self.sistema.editar_producto('R', 'Rosas', -1, '1'),
            lambda: self.sistema.editar_producto('R', 'Tulipanes', 1, '1'),
            lambda: self.sistema.registrar_pedido('', 'R', 1),
            lambda: self.sistema.registrar_pedido('Paulo', 'R', True),
            lambda: self.sistema.registrar_pedido('Paulo', 'R', 0),
            lambda: self.sistema.registrar_pedido('Paulo', 'R', 21),
            lambda: self.sistema.registrar_pedido('Paulo', 'X', 1),
            lambda: self.sistema.cancelar_pedido(99),
        ]
        for operacion in operaciones:
            with self.assertRaises(ValueError):
                operacion()
            self.assertEqual(self.estado(), anterior)

    def test_reserva_y_atencion_fifo(self):
        self.sistema.registrar_pedido('Paulo', 'R', 4)
        self.sistema.registrar_pedido('Mateo', 'T', 3)
        self.sistema.registrar_pedido('Sofía', 'R', 2)
        self.assertEqual(self.stock('R'), 14)
        self.assertEqual(self.stock('T'), 9)
        orden = [self.sistema.atender_siguiente()['cliente'] for _ in range(3)]
        self.assertEqual(orden, ['Paulo', 'Mateo', 'Sofía'])
        self.assertEqual(self.stock('R'), 14)
        self.assertEqual(self.stock('T'), 9)
        with self.assertRaises(IndexError):
            self.sistema.atender_siguiente()

    def test_precio_nombre_fecha_y_copias(self):
        pedido = self.sistema.registrar_pedido('Paulo', 'r', 3)
        self.assertIsNotNone(pedido['creado_en'].tzinfo)
        self.sistema.editar_producto('R', 'Rosas rojas', 17, '2.00')
        self.assertEqual(calcular_total(pedido), Decimal('4.50'))
        self.assertEqual(self.sistema.pedidos_pendientes()[0]['flor'], 'Rosas')
        pedido['cantidad'] = 999
        self.sistema.productos()[0]['stock'] = -1
        self.assertEqual(self.sistema.pedidos_pendientes()[0]['cantidad'], 3)
        self.assertEqual(self.stock('R'), 17)

    def test_editar_misma_flor_con_reserva_propia(self):
        self.sistema.registrar_pedido('Paulo', 'R', 18)
        self.sistema.editar_pedido(1, 'Paulo', 'R', 20)
        self.assertEqual(self.stock('R'), 0)
        self.sistema.editar_pedido(1, 'Paulo', 'R', 5)
        self.assertEqual(self.stock('R'), 15)
        self.assertEqual(self.sistema.pedidos_pendientes()[0]['cantidad'], 5)

    def test_editar_otro_producto_sin_mover_posicion(self):
        self.sistema.registrar_pedido('Paulo', 'R', 4)
        self.sistema.registrar_pedido('Mateo', 'R', 2)
        self.sistema.registrar_pedido('Sofía', 'R', 1)
        editado = self.sistema.editar_pedido(2, 'Mateo', 'T', 5)
        self.assertEqual(self.stock('R'), 15)
        self.assertEqual(self.stock('T'), 7)
        self.assertEqual(calcular_total(editado), Decimal('10.00'))
        self.assertEqual([p['id'] for p in self.sistema.pedidos_pendientes()], [1, 2, 3])

    def test_edicion_rechazada_conserva_stock(self):
        self.sistema.registrar_pedido('Paulo', 'R', 4)
        anterior = self.estado()
        with self.assertRaises(ValueError):
            self.sistema.editar_pedido(1, 'Paulo', 'T', 13)
        self.assertEqual(self.estado(), anterior)




    def test_eliminar_producto_con_pendientes_se_rechaza(self):
        self.sistema.registrar_pedido('Paulo', 'R', 4)
        anterior = self.estado()
        with self.assertRaises(ValueError):
            self.sistema.eliminar_producto('R')
        self.assertEqual(self.estado(), anterior)

    def test_eliminar_producto_atendido_conserva_venta(self):
        self.sistema.registrar_pedido('Paulo', 'R', 4)
        self.sistema.atender_siguiente()
        self.sistema.eliminar_producto('R')
        self.assertEqual(self.sistema.pedidos_atendidos()[0]['flor'], 'Rosas')
        self.assertEqual(calcular_total(self.sistema.pedidos_atendidos()[0]), Decimal('6.00'))
        self.assertEqual(self.sistema.ultimo_atendido()['cliente'], 'Paulo')


    def test_identificadores_no_se_reutilizan(self):
        self.sistema.registrar_pedido('Paulo', 'R', 1)
        self.sistema.cancelar_pedido(1)
        pedido = self.sistema.registrar_pedido('Mateo', 'R', 1)
        self.assertEqual(pedido['id'], 2)


    def test_cancelacion_devuelve_stock_y_conserva_fifo(self):
        for nombre in ('Paulo', 'Mateo', 'Sofía'):
            self.sistema.registrar_pedido(nombre, 'R', 2)
        self.sistema.cancelar_pedido(2)
        self.assertEqual(self.stock('R'), 16)
        self.assertEqual([p['id'] for p in self.sistema.pedidos_pendientes()], [1, 3])
        self.assertEqual(self.sistema.atender_siguiente()['cliente'], 'Paulo')
        self.assertEqual(self.sistema.atender_siguiente()['cliente'], 'Sofía')

    def test_historial_lifo_y_consulta_sin_extraer(self):
        with self.assertRaises(IndexError):
            self.sistema.ultimo_atendido()
        for nombre in ('Paulo', 'Mateo', 'Sofía'):
            self.sistema.registrar_pedido(nombre, 'R', 1)
        for _ in range(3):
            self.sistema.atender_siguiente()
        self.assertEqual(self.sistema.ultimo_atendido()['cliente'], 'Sofía')
        self.assertEqual(self.sistema.atendidos.size(), 3)
        registros = self.sistema.pedidos_atendidos()
        self.assertEqual([p['cliente'] for p in registros], ['Sofía', 'Mateo', 'Paulo'])
        registros[0]['cantidad'] = 999
        self.assertEqual(self.sistema.ultimo_atendido()['cantidad'], 1)



class Interfaz(unittest.TestCase):
    def test_menu_no_se_cierra_por_letras(self):
        entradas = ['x', '1', '1', 'R', 'Rosas', 'letra', '-1', '10',
                    'NaN', '1.50', '2', '0', '2', '1', 'Paulo', 'R', '0', '2',
                    '2', '5', '6', '0', '3', '0']
        salida = StringIO()
        with patch('builtins.input', side_effect=entradas), redirect_stdout(salida):
            principal()
        texto = salida.getvalue()
        self.assertIn('Escriba un número entero', texto)
        self.assertIn('Flor registrada', texto)
        self.assertIn('Atendido: pedido 1 de Paulo', texto)
        self.assertIn('ÚLTIMO PEDIDO ATENDIDO', texto)
        self.assertIn('Sesión finalizada', texto)

    def test_interrupcion_controlada(self):
        with patch('builtins.input', side_effect=EOFError), redirect_stdout(StringIO()) as salida:
            principal()
        self.assertIn('Sesión interrumpida', salida.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
