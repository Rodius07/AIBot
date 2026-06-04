from flask import Flask, request

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def get_data():
    data = request.json
    print("Получено:", round((1024 - data['moisture'])/1024*100),'%')
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
