from flask import Flask
from routes.invoice_route import invoice_bp
import os

app = Flask(__name__)
app.register_blueprint(invoice_bp)

# Criar pastas necessárias
def create_folders():
    folders = [
        'uploads',
        'classificadas',
        'classificadas/dinheiro',
        'classificadas/outros'
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Pasta criada: {folder}")

if __name__ == "__main__":
    create_folders()
    app.run(debug=True, host='0.0.0.0', port=5000)