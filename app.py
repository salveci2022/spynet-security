import os
import datetime
import secrets
from io import BytesIO
from flask import (
    Flask, render_template, request, jsonify, redirect, 
    url_for, session, send_file
)
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
import sqlite3  # Adicionar para persistência
import hashlib  # Adicionar para segurança de senhas

load_dotenv()

app = Flask(__name__)

# ✅ CORREÇÃO: Secret key forte e obrigatória
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise ValueError("SECRET_KEY must be set in environment variables")

# ✅ CORREÇÃO: Credenciais mais seguras
CENTRAL_USER = os.getenv("CENTRAL_USER")
CENTRAL_PASS_HASH = os.getenv("CENTRAL_PASS_HASH")  # Senha como hash

if not CENTRAL_USER or not CENTRAL_PASS_HASH:
    raise ValueError("CENTRAL_USER and CENTRAL_PASS_HASH must be set")

# ✅ CORREÇÃO: Inicialização do banco de dados
def init_db():
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         teacher TEXT,
         room TEXT NOT NULL,
         description TEXT NOT NULL,
         ts TEXT NOT NULL,
         resolved BOOLEAN DEFAULT FALSE)
    ''')
    conn.commit()
    conn.close()

init_db()

# ✅ CORREÇÃO: Função auxiliar de autenticação
def require_auth():
    if not session.get("central_logged"):
        return jsonify({"error": "Unauthorized"}), 401
    return None

# ✅ CORREÇÃO: Endpoints protegidos
@app.route("/api/alert", methods=["POST"])
def api_alert():
    # Validação básica de rate limiting
    if len(get_alerts()) > 100:  # Limite razoável
        return jsonify({"ok": False, "error": "System busy"}), 429
        
    data = request.get_json(silent=True) or {}
    teacher = (data.get("teacher") or "").strip()
    room = (data.get("room") or "").strip()
    description = (data.get("description") or "").strip()
    
    if not room or not description:
        return jsonify({"ok": False}), 400
        
    # Validação de comprimento
    if len(description) > 500:
        return jsonify({"ok": False, "error": "Description too long"}), 400
        
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # ✅ CORREÇÃO: Salvar no banco
    save_alert(teacher, room, description, ts)
    
    return jsonify({"ok": True})

@app.route("/api/siren", methods=["POST"])
def api_siren():
    # ✅ CORREÇÃO: Proteger endpoint crítico
    auth_error = require_auth()
    if auth_error:
        return auth_error
        
    # ... resto do código igual
