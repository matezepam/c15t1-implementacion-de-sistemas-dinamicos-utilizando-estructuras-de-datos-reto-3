# Las tres estructuras comparten nodos, pero limitan sus operaciones de forma
# diferente: la lista permite posiciones, la pila usa LIFO y la cola usa FIFO.


class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.final = None
        self.cantidad = 0

    def size(self):
        return self.cantidad

    # Guardar el último nodo permite añadir productos sin recorrer el inventario.
    # Si es el primero, también se establece como cabeza de la lista.
    def agregar(self, dato):
        nuevo = Nodo(dato)
        if self.final is None:
            self.cabeza = nuevo
        else:
            self.final.siguiente = nuevo
        self.final = nuevo
        self.cantidad += 1

    def obtener(self, posicion):
        self._validar_posicion(posicion)
        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        return actual.dato

    def _validar_posicion(self, posicion, permitir_final=False):
        limite = self.cantidad if permitir_final else self.cantidad - 1
        if type(posicion) is not int or not 0 <= posicion <= limite:
            raise IndexError('Posición fuera de la lista')

    # Reconecta los enlaces para insertar sin desplazar otros registros.
    # Localizar una posición intermedia requiere recorrer los nodos anteriores.
    def insertar(self, posicion, dato):
        self._validar_posicion(posicion, permitir_final=True)
        if posicion == self.cantidad:
            self.agregar(dato)
            return
        nuevo = Nodo(dato)
        if posicion == 0:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        else:
            anterior = self.cabeza
            for _ in range(posicion - 1):
                anterior = anterior.siguiente
            nuevo.siguiente = anterior.siguiente
            anterior.siguiente = nuevo
        self.cantidad += 1

    # Retira la posición validada y devuelve su dato. Actualiza cabeza y final
    # cuando corresponde para poder reutilizar la lista después de vaciarla.
    def eliminar(self, posicion):
        self._validar_posicion(posicion)
        if posicion == 0:
            retirado = self.cabeza
            self.cabeza = retirado.siguiente
        else:
            anterior = self.cabeza
            for _ in range(posicion - 1):
                anterior = anterior.siguiente
            retirado = anterior.siguiente
            anterior.siguiente = retirado.siguiente
            if retirado is self.final:
                self.final = anterior
        self.cantidad -= 1
        if self.cantidad == 0:
            self.final = None
        retirado.siguiente = None
        return retirado.dato

    # Sigue los enlaces una sola vez para listar los datos. Buscar cada posición
    # desde la cabeza repetiría recorridos y haría más lento el listado.
    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente


class Pila:
    def __init__(self):
        self.tope = None
        self.cantidad = 0

    # Coloca el dato en el tope para consultar primero la atención más reciente.
    # Enlazarlo al tope anterior evita recorrer todo el historial.
    def push(self, dato):
        nuevo = Nodo(dato)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self.cantidad += 1

    def peek(self):
        if self.is_empty():
            raise IndexError('No hay pedidos atendidos')
        return self.tope.dato

    # Devuelve y retira el registro del tope, conservando el orden LIFO.
    # peek comprueba antes si está vacía para no acceder a un nodo inexistente.
    def pop(self):
        dato = self.peek()
        retirado = self.tope
        self.tope = retirado.siguiente
        retirado.siguiente = None
        self.cantidad -= 1
        return dato

    def is_empty(self):
        return self.tope is None

    def size(self):
        return self.cantidad

    # Recorre desde el tope para mostrar primero la atención más reciente.
    # No usa pop porque consultar el historial no debe borrar registros.
    def en_orden(self):
        pedidos = []
        actual = self.tope
        while actual is not None:
            pedidos.append(actual.dato)
            actual = actual.siguiente
        return pedidos


class Cola(ListaEnlazada):
    # Reutiliza los nodos de la lista: encolar añade al final y desencolar
    # retira del inicio. Así atiende por llegada sin desplazar los otros pedidos.
    def enqueue(self, dato):
        self.agregar(dato)

    # Comprueba el frente antes de retirarlo y devuelve el pedido que sigue.
    # No se elige un ID al atender, para conservar el orden de llegada.
    def dequeue(self):
        self.front()
        return self.eliminar(0)

    def front(self):
        if self.is_empty():
            raise IndexError('No hay pedidos pendientes')
        return self.cabeza.dato

    def is_empty(self):
        return self.cantidad == 0

    # Cancelar retira un pedido por posición; atender siempre retira el frente.
