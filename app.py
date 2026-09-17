from flask import Flask, render_template_string, request, jsonify
import requests
import re

app = Flask(__name__)

# Visual expandido do painel com 3 abas
HTML_PAGINA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Meu Painel OSINT Online</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --accent: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #475569;
        }
        body { background: var(--bg-dark); color: var(--text-main); font-family: sans-serif; display: flex; height: 100vh; margin: 0; overflow: hidden; }
        
        aside { width: 250px; background: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        .logo { padding: 20px; font-weight: bold; color: var(--accent); border-bottom: 1px solid var(--border); }
        .nav-btn { width: 100%; padding: 15px 20px; background: transparent; border: none; color: var(--text-muted); text-align: left; cursor: pointer; font-size: 0.95rem; }
        .nav-btn:hover { background: #334155; color: #fff; }
        .nav-btn.active { background: var(--accent); color: var(--bg-dark); font-weight: bold; }
        
        main { flex: 1; padding: 40px; overflow-y: auto; }
        .tab-content { display: none; max-width: 700px; }
        .tab-content.active { display: block; }
        
        .card { background: var(--panel-bg); border: 1px solid var(--border); padding: 25px; border-radius: 8px; margin-bottom: 20px; }
        input { width: 100%; padding: 10px; margin: 10px 0; background: #0f172a; border: 1px solid var(--border); color: #fff; border-radius: 4px; }
        button { background: var(--accent); color: #0f172a; border: none; padding: 10px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; width: 100%; }
        pre { background: #030712; padding: 15px; text-align: left; margin-top: 15px; color: #a5f3fc; max-height: 250px; overflow-y: auto; font-size: 0.85rem; border-radius: 4px; }
    </style>
</head>
<body>
    <aside>
        <div class="logo">🛡️ OSINT Online</div>
        <button class="nav-btn active" onclick="mudarAba('aba-geral', this)">🔍 Consulta Geral</button>
        <button class="nav-btn" onclick="mudarAba('aba-cnpj', this)">🏢 Consulta CNPJ</button>
        <button class="nav-btn" onclick="mudarAba('aba-cep', this)">📍 Consulta CEP</button>
    </aside>

    <main>
        <!-- ABA 1: CONSULTA GERAL -->
        <div id="aba-geral" class="tab-content active">
            <h2>Consulta de Texto / Alvo</h2>
            <p style="color: var(--text-muted);">Gera diretrizes e dorks de pesquisa para qualquer termo.</p>
            <div class="card">
                <label>Termo ou Nome:</label>
                <input type="text" id="termo-geral" placeholder="Ex: Nome da pessoa...">
                <button onclick="consultarGeral()">Executar Consulta</button>
                <pre id="res-geral">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 2: CONSULTA CNPJ -->
        <div id="aba-cnpj" class="tab-content">
            <h2>Consulta de CNPJ (Receita Federal)</h2>
            <p style="color: var(--text-muted);">Busca dados cadastrais e sócios diretamente na base pública.</p>
            <div class="card">
                <label>Número do CNPJ:</label>
                <input type="text" id="termo-cnpj" placeholder="Ex: 00000000000191">
                <button onclick="consultarCNPJ()">Consultar CNPJ</button>
                <pre id="res-cnpj">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 3: CONSULTA CEP -->
        <div id="aba-cep" class="tab-content">
            <h2>Consulta de CEP (ViaCEP)</h2>
            <p style="color: var(--text-muted);">Mapeia logradouro, bairro, município e UF através do código postal.</p>
            <div class="card">
                <label>Número do CEP:</label>
                <input type="text" id="termo-cep" placeholder="Ex: 38400100">
                <button onclick="consultarCEP()">Consultar CEP</button>
                <pre id="res-cep">Aguardando dados...</pre>
            </div>
        </div>
    </main>

    <script>
        function mudarAba(abaId, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(abaId).classList.add('active');
            btn.classList.add('active');
        }

        async function consultarGeral() {
            let val = document.getElementById('termo-geral').value;
            let box = document.getElementById('res-geral');
            box.innerText = "Consultando...";
            let resp = await fetch('/api/geral', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({termo: val})
            });
            let data = await resp.json();
            box.innerText = JSON.stringify(data, null, 2);
        }

        async function consultarCNPJ() {
            let val = document.getElementById('termo-cnpj').value;
            let box = document.getElementById('res-cnpj');
            box.innerText = "Consultando Receita Federal...";
            let resp = await fetch('/api/cnpj', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cnpj: val})
            });
            let data = await resp.json();
            box.innerText = JSON.stringify(data, null, 2);
        }

        async function consultarCEP() {
            let val = document.getElementById('termo-cep').value;
            let box = document.getElementById('res-cep');
            box.innerText = "Consultando CEP...";
            let resp = await fetch('/api/cep', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cep: val})
            });
            let data = await resp.json();
            box.innerText = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGINA)

@app.route("/api/geral", methods=["POST"])
def api_geral():
    termo = request.json.get("termo", "")
    return jsonify({
        "status": "Sucesso",
        "alvo": termo,
        "dicas": ["Verificar redes sociais", "Pesquisar em diários oficiais"]
    })

@app.route("/api/cnpj", methods=["POST"])
def api_cnpj():
    cnpj_raw = request.json.get("cnpj", "")
    cnpj_limpo = re.sub(r"\D", "", cnpj_raw)
    
    if len(cnpj_limpo) != 14:
        return jsonify({"erro": "O CNPJ deve conter exatamente 14 dígitos."})
    
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({"erro": "CNPJ não encontrado na base pública."})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route("/api/cep", methods=["POST"])
def api_cep():
    cep_raw = request.json.get("cep", "")
    cep_limpo = re.sub(r"\D", "", cep_raw)
    
    if len(cep_limpo) != 8:
        return jsonify({"erro": "O CEP deve conter exatamente 8 dígitos."})
    
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            dados = r.json()
            if "erro" in dados:
                return jsonify({"erro": "CEP não encontrado."})
            return jsonify(dados)
        else:
            return jsonify({"erro": "Falha na consulta ao ViaCEP."})
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)