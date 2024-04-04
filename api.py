from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/send_data', methods=['POST'])
def receive_data():
    """
    Recibe datos (por ejemplo, una fila de un archivo CSV) y los almacena.
    """
    data = request.json  # Asume que los datos se envían en formato JSON
    data_store.append(data)
    return jsonify({"message": "Data received successfully"}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    """
    Devuelve los datos almacenados, que podrían ser utilizados por un dashboard.
    """
    return jsonify(data_store), 200

if __name__ == '__main__':
    app.run(debug=True)