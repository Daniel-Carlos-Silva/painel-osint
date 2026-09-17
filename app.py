from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import re
import hashlib
import os

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

app = Flask(__name__)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

HTML_PAGINA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Painel OSINT Master Online</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --accent: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #475569;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: var(--bg-dark); color: var(--text-main); font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; }
        
        aside { width: 280px; background: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow-y: auto; }
        .logo { padding: 20px; font-weight: bold; color: var(--accent); border-bottom: 1px solid var(--border); font-size: 1.1rem; }
        .nav-btn { width: 100%; padding: 12px 20px; background: transparent; border: none; color: var(--text-muted); text-align: left; cursor: pointer; font-size: 0.9rem; transition: 0.2s; }
        .nav-btn:hover { background: #334155; color: #fff; }
        .nav-btn.active { background: var(--accent); color: var(--bg-dark); font-weight: bold; }
        
        main { flex: 1; padding: 30px; overflow-y: auto; }
        .tab-content { display: none; max-width: 850px; margin: 0 auto; }
        .tab-content.active { display: block; }
        
        h2 { color: var(--accent); margin-bottom: 8px; }
        p.desc { color: var(--text-muted); margin-bottom: 20px; font-size: 0.9rem; }
        
        .card { background: var(--panel-bg); border: 1px solid var(--border); padding: 25px; border-radius: 8px; margin-bottom: 20px; }
        label { display: block; font-size: 0.85rem; font-weight: bold; color: var(--text-muted); margin-bottom: 6px; }
        input[type="text"], input[type="file"], select { width: 100%; padding: 10px; margin-bottom: 15px; background: #0f172a; border: 1px solid var(--border); color: #fff; border-radius: 4px; }
        button { background: var(--accent); color: #0f172a; border: none; padding: 11px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; width: 100%; transition: 0.2s; }
        button:hover { background: #0ea5e9; }
        pre { background: #030712; padding: 15px; text-align: left; margin-top: 15px; color: #a5f3fc; max-height: 250px; overflow-y: auto; font-size: 0.85rem; border-radius: 4px; }
        
        .link-grid { display: grid; grid-template-columns: 1fr; gap: 8px; margin-top: 15px; }
        .link-item { background: #0f172a; padding: 10px 14px; border-radius: 4px; text-decoration: none; color: var(--accent); font-size: 0.85rem; display: flex; justify-content: space-between; border: 1px solid var(--border); }
        .link-item:hover { border-color: var(--accent); color: #fff; }
    </style>
</head>
<body>
    <aside>
        <div class="logo">🛡️ OSINT Master Suite</div>
        <button class="nav-btn active" onclick="mudarAba('aba-geral', this)">🔍 Dorking & Pessoas</button>
        <button class="nav-btn" onclick="mudarAba('aba-cnpj', this)">🏢 Receita Federal (CNPJ)</button>
        <button class="nav-btn" onclick="mudarAba('aba-cep', this)">📍 Geointeligência (CEP)</button>
        <button class="nav-btn" onclick="mudarAba('aba-tel', this)">📞 Telefonia (TELINT)</button>
        <button class="nav-btn" onclick="mudarAba('aba-email', this)">✉️ E-mail & Leaks</button>
        <button class="nav-btn" onclick="mudarAba('aba-veiculo', this)">🚗 Veículos & Placas</button>
    </aside>

    <main>
        <!-- ABA 1: DORKING -->
        <div id="aba-geral" class="tab-content active">
            <h2>Busca Combinatória de Pessoas (Google Dorks)</h2>
            <p class="desc">Gera matrizes booleanas avançadas cruzando nome, local e cargo.</p>
            <div class="card">
                <label>Nome Completo do Alvo:</label>
                <input type="text" id="dk-nome" placeholder="Ex: Nome Completo">
                <div class="grid-2" style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><label>Cidade:</label><input type="text" id="dk-cidade" placeholder="Ex: Uberlândia"></div>
                    <div><label>UF:</label><input type="text" id="dk-uf" placeholder="Ex: MG"></div>
                </div>
                <button onclick="execDorking()">Gerar Links de Pesquisa</button>
                <div id="dk-links" class="link-grid" style="display:none;"></div>
            </div>
        </div>

        <!-- ABA 2: CNPJ -->
        <div id="aba-cnpj" class="tab-content">
            <h2>Consulta de CNPJ (Receita Federal)</h2>
            <p class="desc">Obtém situação cadastral, atividade principal e sócios.</p>
            <div class="card">
                <label>CNPJ da Empresa:</label>
                <input type="text" id="termo-cnpj" placeholder="Ex: 00000000000191">
                <button onclick="consultarAPI('/api/cnpj', {cnpj: val('termo-cnpj')}, 'res-cnpj')">Consultar CNPJ</button>
                <pre id="res-cnpj">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 3: CEP -->
        <div id="aba-cep" class="tab-content">
            <h2>Consulta de CEP (ViaCEP)</h2>
            <p class="desc">Mapeia logradouro, bairro e município por código postal.</p>
            <div class="card">
                <label>Número do CEP:</label>
                <input type="text" id="termo-cep" placeholder="Ex: 38400100">
                <button onclick="consultarAPI('/api/cep', {cep: val('termo-cep')}, 'res-cep')">Consultar CEP</button>
                <pre id="res-cep">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 4: TELEFONE -->
        <div id="aba-tel" class="tab-content">
            <h2>Inteligência Telefônica (TELINT)</h2>
            <p class="desc">Validação de linha, região e geração de links diretos de mensageria.</p>
            <div class="card">
                <label>Número de Telefone (com DDD):</label>
                <input type="text" id="termo-tel" placeholder="Ex: 34999998888">
                <button onclick="consultarAPI('/api/telefone', {phone: val('termo-tel')}, 'res-tel')">Analisar Linha</button>
                <pre id="res-tel">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 5: EMAIL -->
        <div id="aba-email" class="tab-content">
            <h2>E-mail & Breach Recon</h2>
            <p class="desc">Verificação sintática, servidores MX e hash Gravatar.</p>
            <div class="card">
                <label>Endereço de E-mail:</label>
                <input type="text" id="termo-email" placeholder="Ex: alvo@empresa.com.br">
                <button onclick="consultarAPI('/api/email', {email: val('termo-email')}, 'res-email')">Auditar E-mail</button>
                <pre id="res-email">Aguardando dados...</pre>
            </div>
        </div>

        <!-- ABA 6: VEÍCULOS -->
        <div id="aba-veiculo" class="tab-content">
            <h2>Identificador Veicular (Placas & Chassi)</h2>
            <p class="desc">Classificação de placas Mercosul/Cinza e dorks de leilão.</p>
            <div class="card">
                <label>Placa (7 caracteres):</label>
                <input type="text" id="termo-veiculo" placeholder="Ex: ABC1D23">
                <button onclick="consultarAPI('/api/veiculo', {id: val('termo-veiculo')}, 'res-veiculo')">Analisar Veículo</button>
                <pre id="res-veiculo">Aguardando dados...</pre>
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

        function val(id) { return document.getElementById(id).value.trim(); }

        async function consultarAPI(endpoint, payload, resId) {
            let box = document.getElementById(resId);
            box.innerText = "Processando requisição...";
            try {
                let resp = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                let data = await resp.json();
                box.innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                box.innerText = "Erro na requisição: " + err;
            }
        }

        async function execDorking() {
            let nome = val('dk-nome');
            let cidade = val('dk-cidade');
            let uf = val('dk-uf');
            let container = document.getElementById('dk-links');
            container.style.display = 'none';
            container.innerHTML = '';

            let resp = await fetch('/api/dorking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({nome, cidade, uf})
            });
            let data = await resp.json();
            if (data.links) {
                data.links.forEach(item => {
                    let a = document.createElement('a');
                    a.className = 'link-item';
                    a.href = item.url;
                    a.target = '_blank';
                    a.innerHTML = `<span>${item.titulo}</span> <span>🔗</span>`;
                    container.appendChild(a);
                });
                container.style.display = 'grid';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGINA)

@app.route("/api/dorking", methods=["POST"])
def api_dorking():
    data = request.json
    nome = data.get("nome", "").strip()
    cidade = data.get("cidade", "").strip()
    uf = data.get("uf", "").strip().upper()
    
    if not nome:
        return jsonify({"erro": "Informe o nome do alvo."})

    loc = f'("{cidade}" OR "{uf}")' if (cidade or uf) else ""
    n_ex = f'"{nome}"'
    
    links = [
        {"titulo": "Identificação Geral (CPF / RG)", "url": f"https://www.google.com/search?q={quote(n_ex + ' (\"CPF\" OR \"RG\")' + loc)}"},
        {"titulo": "Processos Judiciais (Jusbrasil)", "url": f"https://www.google.com/search?q={quote('site:jusbrasil.com.br/processos ' + n_ex + loc)}"},
        {"titulo": "Diários Oficiais & Portarias", "url": f"https://www.google.com/search?q={quote(n_ex + ' (\"nomeação\" OR \"exoneração\" OR \"portaria\")' + loc)}"},
        {"titulo": "Documentos PDF Vazados", "url": f"https://www.google.com/search?q={quote('filetype:pdf ' + n_ex + ' \"cpf\"' + loc)}"}
    ]
    return jsonify({"alvo": nome, "links": links})

@app.route("/api/cnpj", methods=["POST"])
def api_cnpj():
    cnpj_limpo = re.sub(r"\D", "", request.json.get("cnpj", ""))
    if len(cnpj_limpo) != 14:
        return jsonify({"erro": "CNPJ deve conter 14 dígitos."})
    try:
        r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=8)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"erro": "CNPJ não encontrado."})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route("/api/cep", methods=["POST"])
def api_cep():
    cep_limpo = re.sub(r"\D", "", request.json.get("cep", ""))
    if len(cep_limpo) != 8:
        return jsonify({"erro": "CEP deve conter 8 dígitos."})
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=8)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"erro": "CEP não encontrado."})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route("/api/telefone", methods=["POST"])
def api_telefone():
    raw = request.json.get("phone", "").strip()
    digits = re.sub(r"\D", "", raw)
    return jsonify({
        "telefone_original": raw,
        "somente_digitos": digits,
        "whatsapp_direct": f"https://wa.me/55{digits}" if not digits.startswith("55") else f"https://wa.me/{digits}",
        "truecaller_search": f"https://www.truecaller.com/search/br/{digits[-10:] if len(digits)>=10 else digits}"
    })

@app.route("/api/email", methods=["POST"])
def api_email():
    email = request.json.get("email", "").strip().lower()
    if "@" not in email:
        return jsonify({"erro": "E-mail inválido."})
    md5 = hashlib.md5(email.encode("utf-8")).hexdigest()
    return jsonify({
        "email": email,
        "hash_md5": md5,
        "gravatar": f"https://www.gravatar.com/avatar/{md5}?d=404",
        "haveibeenpwned": f"https://haveibeenpwned.com/account/{email}"
    })

@app.route("/api/veiculo", methods=["POST"])
def api_veiculo():
    raw = re.sub(r"[^A-Za-z0-9]", "", request.json.get("id", "")).upper()
    if len(raw) == 7:
        return jsonify({
            "identificador": raw,
            "tipo": "Placa Brasileira",
            "dorks_pesquisa": [
                f"https://www.google.com/search?q=\"{raw}\"+leilão+OR+multa",
                f"https://www.google.com/search?q=site:detran.*.gov.br+\"{raw}\""
            ]
        })
    return jsonify({"erro": "Informe uma placa válida com 7 caracteres."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)