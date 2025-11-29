import os
import datetime
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from dotenv import load_dotenv
from reportlab.pdfgen import canvas

load_dotenv()

app = Flask(__name__)

# ✅ CONFIGURAÇÃO SEGURA PARA RENDER
app.secret_key = os.getenv("SECRET_KEY", "spynet-render-secret-key-2024")

# ✅ DADOS DA ESCOLA
ESCOLA_NOME = os.getenv("ESCOLA_NOME", "Colégio Estadual SpyNet")
ESCOLA_ENDERECO = os.getenv("ESCOLA_ENDERECO", "Av. Principal, 456 - Centro - São Paulo/SP")
ESCOLA_TELEFONE = os.getenv("ESCOLA_TELEFONE", "(11) 99999-9999")
ESCOLA_DIRETOR = os.getenv("ESCOLA_DIRETOR", "Maria Silva Oliveira")

# ✅ CREDENCIAIS SIMPLIFICADAS
CENTRAL_USER = os.getenv("CENTRAL_USER", "admin")
CENTRAL_PASS = os.getenv("CENTRAL_PASS", "1234")

# ✅ DADOS EM MEMÓRIA (simples e funcional)
alerts = []
siren_on = False
muted = False

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/professor")
def professor():
    return render_template("professor.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/login_central", methods=["GET", "POST"])
def login_central():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario","").strip()
        senha = request.form.get("senha","").strip()
        
        if usuario == CENTRAL_USER and senha == CENTRAL_PASS:
            session["central_logged"] = True
            return redirect(url_for("central"))
        else:
            error = "Usuário ou senha inválidos."
    return render_template("login_central.html", error=error)

@app.route("/central")
def central():
    if not session.get("central_logged"):
        return redirect(url_for("login_central"))
    return render_template("central.html")

@app.route("/logout_central")
def logout_central():
    session.pop("central_logged", None)
    return redirect(url_for("home"))

@app.route("/api/alert", methods=["POST"])
def api_alert():
    global alerts, siren_on, muted
    data = request.get_json(silent=True) or {}
    teacher = (data.get("teacher") or "").strip()
    room = (data.get("room") or "").strip()
    description = (data.get("description") or "").strip()
    
    if not room or not description:
        return jsonify({"ok": False}), 400
        
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    alerts.insert(0,{
        "teacher": teacher,
        "room": room,
        "description": description,
        "ts": ts,
        "resolved": False
    })
    siren_on = True
    muted = False
    return jsonify({"ok": True})

@app.route("/api/status")
def api_status():
    return jsonify({"ok": True, "alerts": alerts, "siren": siren_on, "muted": muted})

@app.route("/api/siren", methods=["POST"])
def api_siren():
    global siren_on, muted
    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").lower()
    if action == "on":
        siren_on = True; muted = False
    elif action == "off":
        siren_on = False; muted = False
    elif action == "mute":
        siren_on = True; muted = True
    else:
        return jsonify({"ok": False}), 400
    return jsonify({"ok": True})

@app.route("/api/resolve", methods=["POST"])
def api_resolve():
    global alerts
    for a in alerts:
        if not a["resolved"]:
            a["resolved"] = True
            break
    return jsonify({"ok": True})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    global alerts, siren_on, muted
    alerts = []
    siren_on = False
    muted = False
    return jsonify({"ok": True})

@app.route("/report.pdf")
def report_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Relatório SPYNET")
    
    # CABEÇALHO COM DADOS DA ESCOLA
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 800, "SPYNET - RELATÓRIO DE SEGURANÇA")
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, 780, f"Escola: {ESCOLA_NOME}")
    pdf.drawString(40, 765, f"Endereço: {ESCOLA_ENDERECO}")
    pdf.drawString(40, 750, f"Telefone: {ESCOLA_TELEFONE}")
    pdf.drawString(40, 735, f"Diretor(a): {ESCOLA_DIRETOR}")
    pdf.drawString(40, 720, f"Relatório gerado em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    
    pdf.line(40, 710, 550, 710)
    
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, 690, "REGISTRO DE ALERTAS E OCORRÊNCIAS")
    
    y = 670
    pdf.setFont("Helvetica", 9)
    
    if not alerts:
        pdf.drawString(40, y, "Nenhum alerta registrado no período.")
    else:
        for idx, a in enumerate(alerts, start=1):
            if y < 100:
                pdf.showPage()
                y = 800
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(40, y, "REGISTRO DE ALERTAS E OCORRÊNCIAS (continuação)")
                y = 780
                pdf.setFont("Helvetica", 9)
            
            pdf.drawString(40, y, f"{idx}. PROFESSOR: {a['teacher'] or 'Não informado'}") 
            y -= 12
            pdf.drawString(40, y, f"   SALA/TURMA: {a['room']} | DATA/HORA: {a['ts']}")
            y -= 12
            pdf.drawString(40, y, f"   STATUS: {'✅ RESOLVIDO' if a['resolved'] else '🚨 ATIVO'}")
            y -= 12
            pdf.drawString(40, y, f"   DESCRIÇÃO: {a['description']}")
            y -= 20
            
            if idx < len(alerts):
                pdf.line(40, y, 550, y)
                y -= 10
    
    pdf.showPage()
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(40, 50, "Sistema SPYNET - Desenvolvido para segurança escolar")
    
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=False, download_name=f"relatorio_spynet_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
