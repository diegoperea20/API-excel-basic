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


if __name__ == "__main__":
    app.run(debug=True)
