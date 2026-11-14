# C15T1 · Implementación de sistemas dinámicos utilizando estructuras de datos

## Reto 3: inventario de flores y pedidos

El programa continúa el sistema de la floristería de los retos anteriores. Permite registrar, consultar, editar y eliminar flores, además de registrar, editar, cancelar y atender pedidos.

La mejora principal es atender los pedidos por orden de llegada sin desplazar los demás registros al retirar el primero. Se utiliza una lista enlazada para el inventario, una cola FIFO para los pendientes y una pila para consultar el historial de atenciones desde la más reciente.

## Instalación

Instala Python.

## Ejecución

Clona el repositorio y entra a su carpeta:

```bash
git clone https://github.com/matezepam/c15t1-implementacion-de-sistemas-dinamicos-utilizando-estructuras-de-datos-reto-3.git
cd c15t1-implementacion-de-sistemas-dinamicos-utilizando-estructuras-de-datos-reto-3
```

Para ingresar tus propios datos:

```bash
python PRINCIPAL.py
```

Para ver un ejemplo completo con datos ya definidos:

```bash
python DEMOSTRACION.py
```

Para ejecutar las pruebas:

```bash
python PRUEBAS.py
```

Los archivos se ejecutan directamente, sin compilación manual. Conserva todos los archivos en la misma carpeta.

```text
ESTRUCTURAS.py      Nodo, lista enlazada, pila y cola
SISTEMA.py          Validaciones y operaciones de la floristería
PRINCIPAL.py        Menús e ingreso de datos
DEMOSTRACION.py     Ejemplo de funcionamiento
PRUEBAS.py          Pruebas automáticas
IMAGENES/           Capturas de la ejecución desde el menú
README.MD          Instrucciones y explicación
```

Los datos duran la sesión y se pierden al cerrar el programa.

## Cómo funciona

En **Inventario** puedes registrar una flor con código, nombre, cantidad disponible y precio. También puedes mostrar, editar o eliminar productos. Para reponer una flor existente, edita su cantidad disponible; no registres otra con el mismo nombre o código. Al editar se solicitan todos sus datos, excepto cambiar el código.

En **Pedidos** puedes registrar un pedido de una flor, mostrar pendientes, editar o cancelar un pendiente, atender al siguiente y mostrar el historial. El ID se genera automáticamente y no se reutiliza al cancelar. Editar mantiene el turno original; atender siempre retira el primero.

El menú principal también permite consultar la última atención. La pila se usa como historial, sin implementar deshacer cambios generales del sistema. Para confirmar una eliminación o cancelación escribe `s`; para volver o salir selecciona `0`.

### Reglas del stock

- Registrar un pedido reserva sus unidades disponibles.
- Atenderlo no vuelve a descontar existencias.
- Cancelarlo devuelve las unidades reservadas.
- Editarlo ajusta la reserva después de verificar el nuevo stock. Si cambia de flor, devuelve la reserva anterior y utiliza el precio de la nueva flor.
- No se elimina un producto con pedidos pendientes. El historial de atendidos conserva los datos comerciales aunque después cambie el catálogo.

Las cantidades deben ser enteras, el pedido debe solicitar al menos una unidad y el precio debe ser positivo y finito, con un máximo de dos decimales. Se rechazan nombres vacíos, códigos o nombres duplicados y pedidos sin stock suficiente. Si la cola o el historial están vacíos, se muestra un aviso. Las letras en cantidades provocan una nueva lectura.

Se mantienen `Decimal` para el dinero y fechas completas con zona UTC-5, siguiendo las correcciones de los trabajos anteriores.

## Estructuras utilizadas y justificación

| Estructura | Uso | Por qué se eligió |
| --- | --- | --- |
| Lista enlazada | Inventario de flores | Permite agregar y eliminar nodos según cambian los productos |
| Cola FIFO | Pedidos pendientes | Atiende primero al cliente que registró su pedido antes |
| Pila LIFO | Historial de pedidos atendidos | Deja la atención más reciente en el tope para consultarla directamente |

Cada nodo guarda un dato y una referencia al siguiente. La lista mantiene cabeza y final; la cola reutiliza esas operaciones mediante `Cola(ListaEnlazada)`. `enqueue()` añade al final y `dequeue()` retira del inicio. La pila utiliza `push()` al atender y `peek()` para consultar el último atendido sin borrarlo; también implementa `pop()` como operación básica LIFO.

Los registros son diccionarios dentro de los nodos. Las listas normales que devuelve el sistema sirven para presentar copias de los datos; el inventario y los pendientes se almacenan realmente en nodos enlazados.

## Ejemplo de ejecución

`DEMOSTRACION.py` registra 20 rosas a USD 1.50 y 12 tulipanes a USD 2.00. Después actualiza los tulipanes a 15 unidades y USD 2.25, y registra tres pedidos:

```text
Pedido 1 de Paulo | USD 6.00
Pedido 2 de Mateo | USD 6.75
Pedido 3 de Sofía | USD 3.00
Stock: [('R01', 14), ('T01', 12)]
Pendientes: [(1, 'Paulo'), (2, 'Mateo'), (3, 'Sofía')]
```

Mateo reduce su pedido de 3 a 2 tulipanes y Sofía cancela sus 2 rosas. El stock queda en 16 rosas y 13 tulipanes, manteniendo a Paulo antes que Mateo. La atención produce:

```text
Atendido: Paulo
Atendido: Mateo
Último atendido sin extraer: Mateo
Historial del más reciente al más antiguo: ['Mateo', 'Paulo']
Stock: [('R01', 16), ('T01', 13)]
Pendientes: []
Cola vacía: No hay pedidos pendientes
```

La demostración también rechaza un pedido excesivo, impide eliminar una flor con pendientes y elimina una flor cuando ya no tiene reservas.

## Ejecución desde el menú

Las capturas muestran una sesión realizada con `PRINCIPAL.py`.

### 1 - Registro de flores

Se registran rosas y tulipanes con su código, cantidad disponible y precio. Cada producto se añade a la lista enlazada del inventario.

![Registro de rosas](IMAGENES/1.%20REGISTRAR%20UNA%20FLOR.png)

![Registro de tulipanes](IMAGENES/1.1%20REGISTRAR%20OTRA%20FLOR.png)

Asignar un código único permite identificar cada flor al pedirla o editarla, evitando confundir nombres o crear registros duplicados. La lista enlazada permite añadir productos conforme cambia el inventario.

### 2 - Consulta del inventario

El inventario inicial muestra 20 rosas a USD 1.50 y 15 tulipanes a USD 2.25. La consulta recorre los productos sin modificar sus existencias.

![Inventario inicial de rosas y tulipanes](IMAGENES/2.%20MOSTRAR%20INVENTARIO.png)

Consultar las existencias antes de tomar un pedido ayuda a conocer lo que se puede ofrecer. Mantener la consulta separada de la modificación evita alterar el stock sólo por mostrarlo.

### 3 - Registro de pedidos

Paulo solicita cuatro rosas, Mateo tres tulipanes y Sofía dos rosas. Al registrar cada pedido se reservan sus unidades y se agrega al final de la cola.

![Registro del pedido de Paulo](IMAGENES/3.%20REGISTRAR%20PEDIDO%201.png)

![Registro de los pedidos de Mateo y Sofía](IMAGENES/3.1%20REGISTRAR%20OTROS%20PEDIDOS.png)

Reservar al registrar evita ofrecer las mismas unidades a otro cliente. Añadir cada pedido al final de la cola conserva su turno desde el momento en que fue aceptado.

### 4 - Pedidos pendientes

La cola conserva el orden de llegada: Paulo, Mateo y Sofía. Sus totales son USD 6.00, USD 6.75 y USD 3.00, respectivamente.

![Tres pedidos pendientes en orden FIFO](IMAGENES/4.%20MOSTRAR%20PENDIENTES.png)

Mostrar el orden y el importe de cada pendiente permite revisar qué falta atender y comprobar los datos antes de procesarlo. Los IDs permiten localizar un pedido sin depender de su posición actual.

### 5 - Edición de un pedido

Mateo reduce su pedido de tres a dos tulipanes. El total pasa a USD 4.50, se libera una unidad y el pedido conserva su posición en la cola.

![Edición del pedido de Mateo](IMAGENES/5.%20EDITAR%20PEDIDO.png)

![Pedido editado sin cambiar el orden FIFO](IMAGENES/5.1%20MOSTRAR%20PEDIDO%20EDITADO.png)

Ajustar únicamente la reserva que cambia mantiene el stock disponible correcto. Conservar la posición evita que una edición adelante o retrase injustificadamente al cliente.

### 6 - Cancelación de un pedido

Se cancela el pedido 3 de Sofía y se devuelven sus dos rosas al inventario. Quedan pendientes Paulo y Mateo, manteniendo su orden.

![Confirmación de la cancelación del pedido 3](IMAGENES/6.%20CANCELAR%20PEDIDO.png)

![Cola de pendientes después de la cancelación](IMAGENES/6.1%20MOSTRAR%20PEDIDO%20CANCELADO.png)

Solicitar confirmación reduce las cancelaciones accidentales. Devolver la reserva permite ofrecer esas flores de nuevo, sin modificar los turnos de los demás clientes.

### 7 - Stock actualizado

Después de la edición y la cancelación quedan 16 rosas y 13 tulipanes. La consulta confirma que las unidades devueltas se sumaron correctamente.

![Inventario actualizado con 16 rosas y 13 tulipanes](IMAGENES/7.%20MOSTRAR%20DEVOLUCION%20DE%20INVENTARIO.png)

Esta revisión permite comprobar que las reservas siguen coincidiendo con los pendientes. El stock disponible es lo que queda para nuevos pedidos, no la cantidad inicial recibida.

### 8 - Atención FIFO

Se atiende primero a Paulo y después a Mateo. Ambos pedidos salen del frente de la cola, que queda vacía; no se descuenta stock otra vez porque ya estaba reservado.

![Atención del primer pedido de Paulo](IMAGENES/8.%20ATENCION%20FIFO.png)

![Atención de Mateo y comprobación de cola vacía](IMAGENES/8.1%20PENDIENTES%20POR%20ATENCION.png)

Retirar siempre del frente respeta el orden de llegada y evita elegir clientes arbitrariamente. Comprobar que la cola queda vacía confirma que no se conserva un pedido pendiente después de atenderlo.

### 9 - Historial LIFO

El historial muestra a Mateo antes que Paulo porque fue el último atendido. Recorrer la pila permite consultar las atenciones recientes sin eliminarlas.

![Historial de atendidos desde el tope de la pila](IMAGENES/9.%20MOSTRAR%20ATENDIDOS.png)

La pila facilita consultar primero la atención más reciente. Conservar los datos y el precio del pedido permite revisar lo vendido aunque después cambie el catálogo.

## Eficiencia

Para `P` productos, `Q` pendientes y `A` atendidos:

| Operación | Tiempo |
| --- | --- |
| Añadir un nodo al final | O(1) |
| Buscar, registrar validando duplicados o editar producto | O(P) |
| Eliminar producto comprobando reservas | O(P + Q) |
| Encolar, desencolar y consultar el frente | O(1) |
| Registrar pedido incluyendo búsqueda de producto | O(P) |
| Editar o cancelar pedido por ID | O(P + Q) |
| Atender siguiente y apilarlo en el historial | O(1) |
| Consultar última atención | O(1) |
| Mostrar inventario, pendientes o historial | O(P), O(Q) u O(A) |

La memoria es O(P + Q + A), más las copias temporales para mostrar datos. El historial crece con las atenciones de la sesión.

Respecto a las listas de Python usadas antes, la cola elimina el desplazamiento de pedidos al retirar el primero. Buscar por código o ID sigue siendo lineal y los nodos necesitan espacio adicional para sus referencias. Separar estructuras, reglas y menú facilita modificar una parte sin repetir las otras.

## Pruebas

`PRUEBAS.py` comprueba FIFO, LIFO, inserciones y eliminaciones de nodos, reutilización de estructuras vacías, duplicados, cantidades y precios inválidos, reservas, ediciones, cancelaciones e historial. También verifica que el menú maneje letras y que las consultas no modifiquen los registros.

La ejecución correcta termina con:

```text
Ran 21 tests in ...s

OK
```
