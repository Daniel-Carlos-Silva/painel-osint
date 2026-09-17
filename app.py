from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# O visual simples da página web (HTML)
HTML_PAGINA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Meu Painel OSINT Online</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 8px; border: 1px solid #475569; width: 400px; text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; background: #0f172a; border: 1px solid #475569; color: #fff; border-radius: 4px; }
        button { background: #38bdf8; color: #0f172a; border: none; padding: 10px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; width: 100%; }
        pre { background: #030712; padding: 10px; text-align: left; margin-top: 15px; color: #a5f3fc; max-height: 150px; overflow-y: auto; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ Meu Painel OSINT</h2>
        <p style="color: #94a3b8; font-size: 0.9rem;">Digite um CPF ou Dado para Consulta</p>
        <input type="text" id="termo" placeholder="Digite aqui...">
        <button onclick="consultar()">Consultar Online</button>
        <pre id="resultado">Aguardando consulta...</pre>
    </div>

    <script>
        async function consultar() {
            let val = document.getElementById('termo').value;
            let resBox = document.getElementById('resultado');
            resBox.innerText = "Consultando...";

            let resposta = await fetch('/api/consultar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({termo: val})
            });
            let dados = await resposta.json();
            resBox.innerText = JSON.stringify(dados, null, 2);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGINA)

@app.route("/api/consultar", methods=["POST"])
def api_consultar():
    dados = request.json
    termo_buscado = dados.get("termo", "")
    
    # Aqui é onde entram as regras das suas ferramentas de OSINT
    resultado_simulado = {
        "status": "Sucesso",
        "termo_informado": termo_buscado,
        "mensagem": "Este é o seu motor OSINT rodando na nuvem!",
        "dorks_sugeridas": [
            f"https://www.google.com/search?q=site:jusbrasil.com.br+{termo_buscado}",
            f"https://www.google.com/search?q=filetype:pdf+{termo_buscado}"
        ]
    }
    return jsonify(resultado_simulado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)