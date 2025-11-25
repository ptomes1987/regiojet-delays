from flask import Flask, jsonify
import sys
import os
import subprocess
import json

app = Flask(__name__)

# Cesta k tvému funkčnímu skriptu (nebo jeho logice)
# Pro jednoduchost a robustnost zavoláme tvůj existující python skript, 
# pokud je napsaný jako modul, nebo si půjčíme jeho logiku.
# Zde použijeme přímou integraci pro rychlost.

@app.route('/')
def home():
    return "🚄 RegioJet Delays API is running! Go to /api/delays"

@app.route('/api/delays')
def get_delays():
    try:
        # Zde voláme logiku, kterou jsme včera vyladili.
        # Spustíme regiojet_api.py jako subprocess a odchytíme výstup,
        # NEBO (lépe) ho naimportujeme, pokud je to možné.
        # Pro maximální spolehlivost teď použijeme subprocess tvého funkčního kódu.
        
        # Poznámka: Na serveru musí být regiojet_api.py přítomen.
        result = subprocess.run(['python3', 'regiojet_api.py'], capture_output=True, text=True)
        
        # Pokud tvůj skript vypisuje JSON na stdout, vrátíme ho.
        # Pokud vypisuje text, vrátíme text.
        
        if result.returncode == 0:
            # Pokus o parsování JSONu, pokud je výstup JSON
            try:
                data = json.loads(result.stdout)
                return jsonify(data)
            except:
                return jsonify({"status": "success", "raw_output": result.stdout})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
