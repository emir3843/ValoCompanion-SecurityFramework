# -*- coding: utf-8 -*-
"""
Basit validation sunucusu: /validate endpoint'i ile integrity ve behavior raporlarını alır.
Çalıştırma: python validation_server.py
"""
from flask import Flask, request, jsonify

app = Flask(__name__)
RECEIVED = []


@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json(force=True, silent=True) or {}
    RECEIVED.append(data)
    # Örnek doğrulama: integrity'de hash değişimi varsa uyarı
    if data.get("type") == "integrity":
        for e in data.get("entries", []):
            if e.get("status") == "ok" and e.get("hash"):
                pass  # İsteğe bağlı: baseline ile karşılaştır
    return jsonify({"status": "received", "count": len(RECEIVED)})


@app.route("/received", methods=["GET"])
def received():
    return jsonify(RECEIVED)


if __name__ == "__main__":
    print("Validation server http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
