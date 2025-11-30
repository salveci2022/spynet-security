from flask import Flask, render_template, send_file, jsonify, request
import os
import datetime
import logging

app = Flask(__name__)

# Configuração para Render
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Armazenamento em memória (Render reinicia periodicamente)
alertas = []
sistema_status = {
    'sirene_ativa': False,
    'mutado': False,
    'ultima_atualizacao': None
}

# ========== ROTAS PRINCIPAIS ==========
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/professor')
def professor():
    return render_template('professor.html')

@app.route('/central')
def central():
    return render_template('central.html', alertas=alertas)

@app.route('/painel_publico')
def painel_publico():
    return render_template('painel_publico.html', alertas=alertas)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login_central')
def login_central():
    return render_template('login_central.html')

# ========== SISTEMA DE ÁUDIO ==========
@app.route('/play-alarm')
def play_alarm():
    try:
        return send_file('static/siren.wav')
    except FileNotFoundError:
        return "Arquivo de áudio não encontrado", 404

@app.route('/tocar_sirene')
def tocar_sirene():
    try:
        return send_file('static/siren.wav')
    except Exception as e:
        app.logger.error(f"Erro na sirene: {str(e)}")
        return f"Erro ao carregar sirene: {str(e)}", 500

# ========== APIs DO SISTEMA ==========
@app.route('/api/alert', methods=['POST'])
def receber_alerta():
    try:
        data = request.get_json()
        
        novo_alerta = {
            'id': len(alertas) + 1,
            'teacher': data.get('teacher', 'Professor'),
            'room': data.get('room', 'Sala não informada'),
            'description': data.get('description', 'Sem descrição'),
            'timestamp': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'resolved': False,
            'ts': datetime.datetime.now().strftime('%H:%M:%S')
        }
        
        alertas.append(novo_alerta)
        sistema_status['sirene_ativa'] = True
        sistema_status['ultima_atualizacao'] = datetime.datetime.now().isoformat()
        
        # Log do alerta
        app.logger.info(f"Novo alerta: {novo_alerta}")
        
        # Manter apenas os últimos 20 alertas (otimização)
        if len(alertas) > 20:
            alertas.pop(0)
            
        return jsonify({'ok': True, 'message': 'Alerta recebido com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro no alerta: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/status')
def status_sistema():
    try:
        alertas_ativos = [a for a in alertas if not a['resolved']]
        
        return jsonify({
            'ok': True,
            'siren': sistema_status['sirene_ativa'],
            'muted': sistema_status['mutado'],
            'alerts': alertas,
            'active_alerts': len(alertas_ativos),
            'last_update': sistema_status['ultima_atualizacao']
        })
    except Exception as e:
        app.logger.error(f"Erro no status: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/siren', methods=['POST'])
def controlar_sirene():
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'on':
            sistema_status['sirene_ativa'] = True
            sistema_status['mutado'] = False
        elif action == 'off':
            sistema_status['sirene_ativa'] = False
            sistema_status['mutado'] = False
        elif action == 'mute':
            sistema_status['mutado'] = True
            
        sistema_status['ultima_atualizacao'] = datetime.datetime.now().isoformat()
        
        app.logger.info(f"Sirene: {action} - Status: {sistema_status['sirene_ativa']}")
        
        return jsonify({'ok': True, 'siren': sistema_status['sirene_ativa'], 'muted': sistema_status['mutado']})
        
    except Exception as e:
        app.logger.error(f"Erro na sirene: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/resolve', methods=['POST'])
def resolver_alerta():
    try:
        # Encontrar o primeiro alerta não resolvido
        for alerta in alertas:
            if not alerta['resolved']:
                alerta['resolved'] = True
                break
                
        # Se não há mais alertas ativos, desativar sirene
        alertas_ativos = [a for a in alertas if not a['resolved']]
        if not alertas_ativos:
            sistema_status['sirene_ativa'] = False
            
        sistema_status['ultima_atualizacao'] = datetime.datetime.now().isoformat()
        
        app.logger.info("Alerta resolvido")
        
        return jsonify({'ok': True})
        
    except Exception as e:
        app.logger.error(f"Erro ao resolver: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def limpar_alertas():
    try:
        alertas.clear()
        sistema_status['sirene_ativa'] = False
        sistema_status['ultima_atualizacao'] = datetime.datetime.now().isoformat()
        
        app.logger.info("Alertas limpos")
        
        return jsonify({'ok': True})
        
    except Exception as e:
        app.logger.error(f"Erro ao limpar: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/acionar_alerta', methods=['POST'])
def acionar_alerta():
    try:
        novo_alerta = {
            'id': len(alertas) + 1,
            'teacher': 'Professor',
            'room': 'Local não informado',
            'description': 'Alerta de pânico acionado',
            'timestamp': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'resolved': False,
            'ts': datetime.datetime.now().strftime('%H:%M:%S')
        }
        
        alertas.append(novo_alerta)
        sistema_status['sirene_ativa'] = True
        sistema_status['ultima_atualizacao'] = datetime.datetime.now().isoformat()
        
        app.logger.info("Alerta de pânico acionado")
        
        return jsonify({
            'success': True,
            'message': 'Alerta de pânico acionado! Sirene ativada.',
            'alerta': novo_alerta
        })
        
    except Exception as e:
        app.logger.error(f"Erro no pânico: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

# Health check para Render
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'alertas_ativos': len([a for a in alertas if not a['resolved']])
    })

# Rota de fallback
@app.route('/alarme')
def alarme_page():
    return render_template('home.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
