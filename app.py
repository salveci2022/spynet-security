from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)

# Rota principal
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SPYNET Security</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin: 50px;
                background: #1a1a1a;
                color: white;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .btn {
                display: block;
                width: 200px;
                margin: 20px auto;
                padding: 15px;
                font-size: 18px;
                text-decoration: none;
                color: white;
                background: #007bff;
                border-radius: 8px;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #0056b3;
            }
            .alarme-btn {
                background: #dc3545;
            }
            .alarme-btn:hover {
                background: #c82333;
            }
            h1 {
                color: #00ff00;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ SPYNET Security System</h1>
            <p>Sistema de monitoramento e segurança</p>
            
            <a href="/alarme" class="btn alarme-btn">🚨 Painel de Alarme</a>
            <a href="/play-alarm" class="btn">🔊 Tocar Alarme Direto</a>
            <a href="/status" class="btn">📊 Status do Sistema</a>
        </div>
    </body>
    </html>
    '''

# Rota para tocar o áudio diretamente
@app.route('/play-alarm')
def play_alarm():
    try:
        return send_file('static/siren.mp3')
    except FileNotFoundError:
        return "Arquivo de áudio não encontrado", 404

# Rota para página com botão de alarme
@app.route('/alarme')
def alarme_page():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Painel de Alarme - SPYNET</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(0, 0, 0, 0.7);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 0 30px rgba(255, 0, 0, 0.3);
                border: 2px solid #ff4444;
            }
            .alarme-btn {
                padding: 25px 50px;
                font-size: 28px;
                font-weight: bold;
                background: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                cursor: pointer;
                margin: 20px;
                transition: all 0.3s;
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
            }
            .alarme-btn:hover {
                background: #cc0000;
                transform: scale(1.05);
                box-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
            }
            .stop-btn {
                background: #4444ff;
                box-shadow: 0 0 20px rgba(0, 0, 255, 0.5);
            }
            .stop-btn:hover {
                background: #0000cc;
                box-shadow: 0 0 30px rgba(0, 0, 255, 0.7);
            }
            .back-btn {
                padding: 10px 20px;
                background: #666;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                display: inline-block;
            }
            h1 {
                color: #ff4444;
                font-size: 36px;
                margin-bottom: 30px;
                text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
            }
            .status {
                margin: 20px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 PAINEL DE ALARME</h1>
            
            <div class="status">
                <p>🔴 Sistema de Alarme - PRONTO</p>
                <p>📡 Status: <span style="color: #00ff00;">ATIVO</span></p>
            </div>

            <button class="alarme-btn" onclick="tocarAlarme()">
                🔊 ATIVAR ALARME
            </button>
            
            <button class="alarme-btn stop-btn" onclick="pararAlarme()">
                ⏹️ PARAR ALARME
            </button>
            
            <audio id="alarmeAudio" loop>
                <source src="/play-alarm" type="audio/mp3">
                Seu navegador não suporta o elemento de áudio.
            </audio>

            <div style="margin-top: 30px;">
                <a href="/" class="back-btn">← Voltar ao Início</a>
            </div>
        </div>

        <script>
            function tocarAlarme() {
                var audio = document.getElementById('alarmeAudio');
                audio.play().then(() => {
                    console.log('Alarme ativado!');
                }).catch(error => {
                    console.log('Erro ao tocar alarme:', error);
                    alert('Clique em "Tocar Alarme Direto" primeiro para permitir o áudio!');
                });
            }
            
            function pararAlarme() {
                var audio = document.getElementById('alarmeAudio');
                audio.pause();
                audio.currentTime = 0;
            }
            
            // Permitir áudio no clique em qualquer lugar da página
            document.addEventListener('click', function() {
                var audio = document.getElementById('alarmeAudio');
                audio.volume = 0.1; // Volume reduzido para teste
            });
        </script>
    </body>
    </html>
    ''')

# Rota de status do sistema
@app.route('/status')
def status():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Status do Sistema - SPYNET</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin: 50px;
                background: #1a1a1a;
                color: white;
            }
            .status-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                margin: 10px;
                border-radius: 8px;
                display: inline-block;
                min-width: 200px;
            }
            .online { color: #00ff00; }
            .offline { color: #ff4444; }
            .back-btn {
                padding: 10px 20px;
                background: #666;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>📊 Status do Sistema</h1>
        
        <div class="status-item">
            <h3>Servidor Web</h3>
            <p class="online">● ONLINE</p>
        </div>
        
        <div class="status-item">
            <h3>Sistema de Áudio</h3>
            <p class="online">● OPERACIONAL</p>
        </div>
        
        <div class="status-item">
            <h3>Banco de Dados</h3>
            <p class="online">● CONECTADO</p>
        </div>
        
        <div class="status-item">
            <h3>Segurança</h3>
            <p class="online">● ATIVA</p>
        </div>
        
        <br>
        <a href="/" class="back-btn">← Voltar ao Início</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
