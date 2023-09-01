from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Ruta del archivo Excel que contiene los datos de la tienda
archivo_excel = "tiendav2.xlsx"


# Función para cargar los datos desde el archivo Excel
def cargar_datos():
    try:
        return pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return pd.DataFrame(columns=["id", "nombre", "articulo", "cantidad", "precio"])


# Función para guardar los datos en el archivo Excel
def guardar_datos(datos):
    datos.to_excel(archivo_excel, index=False)


# Ruta para agregar un nuevo producto
@app.route("/productos", methods=["POST"])
def agregar_producto():
    datos = cargar_datos()
    nuevo_producto = request.json

    # Verificar si el campo "precio" es numérico (int o float)
    if "precio" in nuevo_producto and (
        isinstance(nuevo_producto["precio"], int)
        or isinstance(nuevo_producto["precio"], float)
    ):
        # El campo "precio" es válido como entero o flotante
        nuevo_id = datos["id"].max() + 1 if not datos.empty else 1
        nuevo_producto["id"] = int(nuevo_id)  # Convertir a int
        datos = pd.concat([datos, pd.DataFrame([nuevo_producto])], ignore_index=True)
        guardar_datos(datos)
        return (
            jsonify({"mensaje": "Producto agregado con éxito", "id": int(nuevo_id)}),
            201,
        )
    else:
        return (
            jsonify({"error": 'El campo "precio" debe ser un número (int o float)'}),
            400,
        )  # Código 400 para Bad Request

@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    datos = cargar_datos()
    producto_existente = datos[datos["id"] == id]
    if producto_existente.empty:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
    
    datos_actualizados = request.json
    
    for campo, valor in datos_actualizados.items():
        datos.at[producto_existente.index[0], campo] = valor
    
    guardar_datos(datos)
    
    return jsonify({"mensaje": "Producto actualizado con éxito"})

"""
 Desordena ID  pero e suna forma de hacerlo 
 # Ruta para actualizar un producto
@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    datos = cargar_datos()
    producto_existente = datos[datos["id"] == id]
    if producto_existente.empty:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
    
    datos_actualizados = request.json
    datos_actualizados["id"] = id
    
    # Elimina el producto existente con el ID dado
    datos = datos[datos["id"] != id]
    
    # Agrega los datos actualizados al DataFrame
    datos = pd.concat([datos, pd.DataFrame([datos_actualizados])], ignore_index=True)
    
    guardar_datos(datos)
    return jsonify({"mensaje": "Producto actualizado con éxito"}) """

# Ruta para obtener todos los productos
@app.route("/productos", methods=["GET"])
def obtener_productos():
    datos = cargar_datos()
    return jsonify(datos.to_dict(orient="records"))


# Ruta para obtener un producto por ID
@app.route("/productos/<int:id>", methods=["GET"])
def obtener_producto(id):
    datos = cargar_datos()
    producto = datos[datos["id"] == id].to_dict(orient="records")
    if producto:
        return jsonify(producto[0])
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404


# Ruta para eliminar un producto por ID
@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    datos = cargar_datos()
    producto_existente = datos[datos["id"] == id]
    if producto_existente.empty:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
    datos = datos[datos["id"] != id]
    guardar_datos(datos)
    return jsonify({"mensaje": "Producto eliminado con éxito"})



#filtros 

# Ruta para obtener el precio máximo de los productos
@app.route("/productos/max", methods=["GET"])
def max_productos():
    datos = cargar_datos()
    max_precio = datos["precio"].max()
    productos_mas_caros = datos[datos["precio"] == max_precio]
    
    if productos_mas_caros.empty:
        return jsonify({"mensaje": "No se encontraron productos más caros"}), 404
    
    # Accedemos a los nombres, ids y precios de todos los productos con precio máximo
    nombres_productos_mas_caros = productos_mas_caros["nombre"].tolist()
    ids_productos_mas_caros = productos_mas_caros["id"].tolist()
    precios_productos_mas_caros = productos_mas_caros["precio"].tolist()
    
    respuesta = {
        "max_precio": float(max_precio),
        "productos": []
    }
    
    for i in range(len(nombres_productos_mas_caros)):
        producto = {
            "id": int(ids_productos_mas_caros[i]),
            "nombre": nombres_productos_mas_caros[i],
            "precio": float(precios_productos_mas_caros[i])
        }
        respuesta["productos"].append(producto)
    
    return jsonify(respuesta)


# Ruta para obtener el precio mínimo de los productos y toda la fila correspondiente
@app.route("/productos/min", methods=["GET"])
def min_producto():
    datos = cargar_datos()
    min_precio = datos["precio"].min()
    producto_menos_caro = datos[datos["precio"] == min_precio]
    
    if producto_menos_caro.empty:
        return jsonify({"mensaje": "No se encontró el producto más barato"}), 404
    
    # Accedemos a la fila completa del primer producto con precio mínimo
    producto_minimo_info = producto_menos_caro.to_dict(orient="records")
    
    return jsonify({
        "min_precio": float(min_precio),
        "producto": producto_minimo_info
    })


# Ruta para obtener un producto por nombre
@app.route("/productos/nombre/<string:nombre>", methods=["GET"])
def obtener_productos_por_nombre(nombre):
    datos = cargar_datos()
    productos = datos[datos["nombre"] == nombre].to_dict(orient="records")
    
    if productos:
        return jsonify(productos)
    else:
        return jsonify({"mensaje": "Productos no encontrados"}), 404


# Ruta para obtener los productos con el precio promedio
@app.route("/productos/promedio", methods=["GET"])
def promedio_productos():
    datos = cargar_datos()
    precio_promedio = datos["precio"].mean()
    productos_con_precio_promedio = datos[datos["precio"] == precio_promedio]
    
    if productos_con_precio_promedio.empty:
        return jsonify({"mensaje": "No se encontraron productos con precio promedio"}), 404
    
    # Accedemos a los nombres de todos los productos con precio promedio
    nombres_productos_con_precio_promedio = productos_con_precio_promedio["nombre"].tolist()
    
    return jsonify({
        "precio_promedio": float(precio_promedio),
        "productos": nombres_productos_con_precio_promedio
    })


# Ruta para obtener productos por artículo
@app.route("/productos/articulo/<string:articulo>", methods=["GET"])
def obtener_productos_por_articulo(articulo):
    datos = cargar_datos()
    productos = datos[datos["articulo"] == articulo].to_dict(orient="records")
    
    if productos:
        return jsonify(productos)
    else:
        return jsonify({"mensaje": "Productos no encontrados"}), 404

# Ruta para obtener el conteo de productos por artículo
@app.route("/productos/articulo/<string:articulo>/conteo", methods=["GET"])
def contar_productos_por_articulo(articulo):
    datos = cargar_datos()
    cantidad_productos = datos[datos["articulo"] == articulo].shape[0]
    
    if cantidad_productos > 0:
        return jsonify({"articulo": articulo, "conteo": cantidad_productos})
    else:
        return jsonify({"mensaje": "No se encontraron productos con este artículo"}), 404



# Ruta para obtener los productos con el precio mínimo y un nombre específico
@app.route("/productos/min/<string:nombre>", methods=["GET"])
def min_productos_con_nombre(nombre):
    datos = cargar_datos()
    min_precio = datos["precio"].min()
    productos_minimos_con_nombre = datos[(datos["precio"] == min_precio) & (datos["nombre"] == nombre)]

    if productos_minimos_con_nombre.empty:
        return jsonify({"mensaje": f"No se encontraron productos con el nombre '{nombre}' y precio mínimo"}), 404
    
    # Accedemos a la lista de nombres y IDs de productos que cumplen ambas condiciones
    nombres_productos_minimos = productos_minimos_con_nombre["nombre"].tolist()
    ids_productos_minimos = productos_minimos_con_nombre["id"].tolist()

    return jsonify({
        "min_precio": float(min_precio),
        "nombres": nombres_productos_minimos,
        "id": ids_productos_minimos
    })





if __name__ == "__main__":
    app.run(debug=True)
