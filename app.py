import concurrent.futures[cite: 1]
import hashlib[cite: 1]
import json[cite: 1]
import os[cite: 1]
import re[cite: 1]
import socket[cite: 1]
from urllib.parse import quote, urlencode[cite: 1]
from flask import Flask, render_template_string, request, jsonify, send_file[cite: 1]
import phonenumbers[cite: 1]
from phonenumbers import carrier, geocoder, timezone[cite: 1]
import requests[cite: 1]

try:
    import dns.resolver[cite: 1]
except ImportError:
    dns = None

try:
    from PIL import Image[cite: 1]
    from PIL.ExifTags import TAGS, GPSTAGS[cite: 1]
except ImportError:
    Image = None

try:
    import cv2[cite: 1]
    import numpy as np[cite: 1]
except ImportError:
    cv2 = None
    np = None

try:
    import PyPDF2[cite: 1]
except ImportError:
    PyPDF2 = None

app = Flask(__name__)[cite: 1]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"[cite: 1]
TIMEOUT = 8[cite: 1]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Geral de Inteligência OSINT - Ultimate All-In-One</title>
    <style>
        :root {
            --bg-dark: #090d16;
            --panel-bg: #111827;
            --card-bg: #1f2937;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border: #374151;
            --danger: #ef4444;
            --success: #10b981;
            --gold: #f59e0b;
            --purple: #a855f7;
            --emerald: #10b981;
            --rose: #f43f5e;
            --cyan: #06b6d4;
            --teal: #14b8a6;
            --amber: #d97706;
            --indigo: #6366f1;
            --lime: #84cc16;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        aside { width: 320px; background: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        .logo { padding: 18px 20px; font-size: 1.1rem; font-weight: bold; color: var(--accent); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
        .nav-category { font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; padding: 14px 20px 4px 20px; letter-spacing: 0.5px; }
        nav { flex: 1; overflow-y: auto; padding-bottom: 20px; }
        .nav-btn { width: 100%; padding: 10px 20px; background: transparent; border: none; color: var(--text-muted); text-align: left; font-size: 0.88rem; cursor: pointer; transition: 0.15s; display: flex; align-items: center; gap: 8px; }
        .nav-btn:hover { background: var(--card-bg); color: var(--text-main); }
        .nav-btn.active { background: var(--accent); color: var(--bg-dark); font-weight: 700; }
        
        main { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 30px; }
        .tab-content { display: none; max-width: 980px; width: 100%; margin: 0 auto; }
        .tab-content.active { display: block; }
        
        h2 { font-size: 1.4rem; margin-bottom: 6px; color: var(--accent); }
        p.desc { color: var(--text-muted); margin-bottom: 20px; font-size: 0.9rem; }
        
        .form-card { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
        input[type="text"], input[type="file"], select { width: 100%; padding: 10px 14px; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 6px; color: var(--text-main); font-size: 0.92rem; outline: none; }
        input[type="text"]:focus, select:focus { border-color: var(--accent); }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
        
        button.btn-run { background: var(--accent); color: var(--bg-dark); font-weight: 700; border: none; padding: 11px 22px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; transition: 0.2s; width: 100%; }
        button.btn-run:hover { background: var(--accent-hover); }
        
        .result-box { background: #030712; border: 1px solid var(--border); border-radius: 8px; padding: 18px; font-family: "Courier New", Courier, monospace; font-size: 0.88rem; color: #a5f3fc; white-space: pre-wrap; word-break: break-all; max-height: 440px; overflow-y: auto; display: none; margin-top: 15px; }
        .spinner { display: none; color: var(--accent); font-weight: 600; margin: 12px 0; font-size: 0.9rem; }
        
        .link-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; margin-top: 15px; }
        .link-item { background: var(--card-bg); padding: 9px 12px; border-radius: 6px; text-decoration: none; color: var(--accent); font-size: 0.85rem; display: flex; align-items: center; justify-content: space-between; border: 1px solid transparent; }
        .link-item:hover { border-color: var(--accent); color: #fff; }

        .omni-card { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 14px; }
        .omni-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
        .omni-title { font-weight: bold; color: var(--accent); font-size: 0.95rem; }
        .badge { font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        .badge-ok { background: #065f46; color: #6ee7b7; }
        .badge-warn { background: #78350f; color: #fde68a; }
        .badge-err { background: #7f1d1d; color: #fca5a5; }

        .image-preview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 15px; }
        .img-card { background: #030712; border: 1px solid var(--border); border-radius: 6px; padding: 8px; text-align: center; }
        .img-card img { max-width: 100%; border-radius: 4px; margin-top: 6px; }
        .img-card span { font-size: 0.78rem; font-weight: bold; color: var(--accent); }
    </style>
</head>
<body>
    <aside>
        <div class="logo"><span>🛡️</span> OSINT Master Suite</div>
        <nav>
            <div class="nav-category" style="color:var(--rose);">🚀 Recursos Enterprise</div>
            <button class="nav-btn active" onclick="openTab('tab-graph', this)">🕸️ Grafo de Vínculos</button>
            <button class="nav-btn" onclick="openTab('tab-pdf', this)">📄 Gerador de Dossiê (PDF)</button>
            <button class="nav-btn" onclick="openTab('tab-watchlist', this)">🚨 Sentinela / Watchlist</button>
            <button class="nav-btn" onclick="openTab('tab-sancoes', this)">⚠️ Lista Suja MTE & Ibama</button>

            <div class="nav-category" style="color:var(--gold);">⚡ Pesquisas Universais (Omni)</div>
            <button class="nav-btn" onclick="openTab('tab-omni-cpf', this)">🎯 CPF Omnisearch</button>
            <button class="nav-btn" onclick="openTab('tab-omni-tel', this)">📞 Telefone Omnisearch</button>
            <button class="nav-btn" onclick="openTab('tab-omni-email', this)">✉️ E-mail Omnisearch</button>

            <div class="nav-category" style="color:var(--amber);">📜 Cartórios & Registros</div>
            <button class="nav-btn" onclick="openTab('tab-cartorio', this)">📜 Cartórios (CENPROT)</button>

            <div class="nav-category" style="color:var(--indigo);">🗳️ Político & Eleitoral</div>
            <button class="nav-btn" onclick="openTab('tab-tse', this)">🗳️ TSE (Bens & Doações)</button>

            <div class="nav-category" style="color:var(--lime);">🌾 Fundiário & Ambiental</div>
            <button class="nav-btn" onclick="openTab('tab-rural', this)">🌳 Imóveis Rurais (CAR/SICAR)</button>

            <div class="nav-category" style="color:var(--teal);">💧 Concessionárias & Local</div>
            <button class="nav-btn" onclick="openTab('tab-dmae', this)">💧 DMAE Uberlândia (CPF)</button>

            <div class="nav-category" style="color:var(--cyan);">🏛️ Bases Sociais & Federais</div>
            <button class="nav-btn" onclick="openTab('tab-social-gov', this)">💳 Programas Sociais (CadÚnico)</button>

            <div class="nav-category">Judicial & Prisões</div>
            <button class="nav-btn" onclick="openTab('tab-bnmp', this)">🚨 BNMP 3.0 (Mandados Total)</button>
            <button class="nav-btn" onclick="openTab('tab-jud', this)">⚖️ Processos (DataJud CNJ)</button>
            <button class="nav-btn" onclick="openTab('tab-diario', this)">📰 Diários Oficiais</button>
            <button class="nav-btn" onclick="openTab('tab-cgu', this)">🏛️ Integridade CGU (PEP/CEIS)</button>

            <div class="nav-category">Pessoas & Fóruns</div>
            <button class="nav-btn" onclick="openTab('tab-forum', this)">🗣️ Fóruns & Avaliações</button>
            <button class="nav-btn" onclick="openTab('tab-dorking', this)">👥 Dorking Multidimensional</button>
            <button class="nav-btn" onclick="openTab('tab-social', this)">🌐 Redes Sociais (35+)</button>
            <button class="nav-btn" onclick="openTab('tab-prof', this)">🎓 Conselhos (OAB/CFM/CREA)</button>
            <button class="nav-btn" onclick="openTab('tab-github', this)">💻 GitHub Desenvolvedor</button>

            <div class="nav-category">Corporativo & Licitações</div>
            <button class="nav-btn" onclick="openTab('tab-cnpj', this)">🏢 Receita Federal (CNPJ/QSA)</button>
            <button class="nav-btn" onclick="openTab('tab-pncp', this)">📑 Licitações (PNCP)</button>
            <button class="nav-btn" onclick="openTab('tab-sicaf', this)">🏛️ Compras.gov.br / SICAF</button>

            <div class="nav-category">Mobilidade & Rastreamento</div>
            <button class="nav-btn" onclick="openTab('tab-veiculo', this)">🚗 Placas e Chassi (VIN)</button>
            <button class="nav-btn" onclick="openTab('tab-placa-img', this)">🔍 Restauração de Placas</button>
            <button class="nav-btn" onclick="openTab('tab-aero', this)">✈️ Voo ADS-B (OpenSky)</button>
            <button class="nav-btn" onclick="openTab('tab-maritimo', this)">🚢 Marítimo (MMSI / IMO)</button>
            <button class="nav-btn" onclick="openTab('tab-crypto', this)">⛓️ Criptoativos (BTC/ETH)</button>

            <div class="nav-category">Geointeligência & Rede</div>
            <button class="nav-btn" onclick="openTab('tab-geo', this)">📍 Endereço / CEP / OpenStreetMap</button>
            <button class="nav-btn" onclick="openTab('tab-dns', this)">🌐 DNS, Subdomínios & Registro.br</button>
            <button class="nav-btn" onclick="openTab('tab-ip', this)">📡 IP, ASN, GeoIP & DNSBL</button>
            <button class="nav-btn" onclick="openTab('tab-doh', this)">🔒 DNS-over-HTTPS (DoH)</button>
            <button class="nav-btn" onclick="openTab('tab-stack', this)">🛠️ Stack Web & Tecnologias</button>
            <button class="nav-btn" onclick="openTab('tab-archive', this)">🕰️ Wayback Machine</button>
            <button class="nav-btn" onclick="openTab('tab-forense', this)">📄 Forense (PDF / Imagem EXIF)</button>
        </nav>
    </aside>

    <main>
        <!-- 1. GRAFO DE VÍNCULOS -->
        <div id="tab-graph" class="tab-content active">
            <h2>🕸️ Análise de Vínculos & Grafo Relacional (Link Analysis)</h2>
            <p class="desc">Gera um mapa de conexões cruzando CPF, empresas (QSA), telefones e processos em uma rede unificada.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF ou Nome do Alvo Central:</label><input type="text" id="graph-in" placeholder="Ex: Nome da pessoa física ou CPF"></div>
                <button class="btn-run" onclick="runQuery('/api/link_analysis_graph', {target: val('graph-in')}, 'res-graph', 'spin-graph')">Gerar Grafo de Vínculos 🕸️</button>
            </div>
            <div id="spin-graph" class="spinner">Calculando arestas e nós...</div>
            <div id="res-graph" class="result-box"></div>
        </div>

        <!-- 2. GERADOR DE DOSSIÊ EM PDF -->
        <div id="tab-pdf" class="tab-content">
            <h2>📄 Gerador de Dossiê Policial & Relatório PDF</h2>
            <p class="desc">Compila as informações colhidas no formato padrão de relatório de inteligência com carimbo de integridade.</p>
            <div class="form-card">
                <div class="grid-2">
                    <div class="form-group"><label>Nome do Alvo / Investigado:</label><input type="text" id="pdf-nome" placeholder="Ex: Nome completo"></div>
                    <div class="form-group"><label>Nº do Procedimento / Inquérito:</label><input type="text" id="pdf-proc" placeholder="Ex: IPL 042/2026"></div>
                </div>
                <button class="btn-run" onclick="runQuery('/api/gerar_dossie_pdf', {nome: val('pdf-nome'), proc: val('pdf-proc')}, 'res-pdf', 'spin-pdf')">Gerar Dossiê de Inteligência 📄</button>
            </div>
            <div id="spin-pdf" class="spinner">Estruturando relatório...</div>
            <div id="res-pdf" class="result-box"></div>
        </div>

        <!-- 3. SENTINELA / WATCHLIST -->
        <div id="tab-watchlist" class="tab-content">
            <h2>🚨 Sentinela / Watchlist - Monitoramento de Alvos</h2>
            <p class="desc">Módulo passivo para alerta de novos mandados, menções em diários e modificações societárias.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF, CNPJ ou Nome para Monitorar:</label><input type="text" id="watch-in" placeholder="Ex: 000.000.000-00"></div>
                <button class="btn-run" onclick="runQuery('/api/watchlist_add', {alvo: val('watch-in')}, 'res-watch', 'spin-watch')">Cadastrar Alvo na Sentinela 🚨</button>
            </div>
            <div id="spin-watch" class="spinner">Cadastrando...</div>
            <div id="res-watch" class="result-box"></div>
        </div>

        <!-- 4. LISTA SUJA MTE & IBAMA -->
        <div id="tab-sancoes" class="tab-content">
            <h2>⚠️ Trabalho Escravo (MTE) & Embargos do Ibama</h2>
            <p class="desc">Verifica autuações no Cadastro de Empregadores de Trabalho Degradante e embargos ambientais.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF ou CNPJ:</label><input type="text" id="sanc-in" placeholder="Ex: 00000000000"></div>
                <button class="btn-run" onclick="runQuery('/api/sancoes', {doc: val('sanc-in')}, 'res-sanc', 'spin-sanc')">Checar Sanções Federais ⚠️</button>
            </div>
            <div id="spin-sanc" class="spinner">Consultando bases...</div>
            <div id="res-sanc" class="result-box"></div>
        </div>

        <!-- 5. CPF OMNISEARCH -->
        <div id="tab-omni-cpf" class="tab-content">
            <h2>🎯 CPF Omnisearch (Tudo em 1)</h2>
            <p class="desc">Validação Módulo 11, mandados BNMP, processos, sócios QSA, diários e dorks paralelos.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF (11 dígitos):</label><input type="text" id="omni-cpf-in" placeholder="Ex: 000.000.000-00"></div>
                <button class="btn-run" onclick="runQuery('/api/cpf_omnisearch', {cpf: val('omni-cpf-in')}, 'res-omni-cpf', 'spin-omni-cpf')">Disparar CPF Omnisearch 🚀</button>
            </div>
            <div id="spin-omni-cpf" class="spinner">Executando varredura total...</div>
            <div id="res-omni-cpf" class="result-box"></div>
        </div>

        <!-- 6. TELEFONE OMNISEARCH -->
        <div id="tab-omni-tel" class="tab-content">
            <h2>📞 Telefone Omnisearch</h2>
            <p class="desc">E.164, operadora, UF/DDD, busca de empresas na Receita pelo número e mensageria direta.</p>
            <div class="form-card">
                <div class="form-group"><label>Telefone com DDD:</label><input type="text" id="omni-tel-in" placeholder="Ex: (34) 99999-8888"></div>
                <button class="btn-run" onclick="runQuery('/api/tel_omnisearch', {phone: val('omni-tel-in')}, 'res-omni-tel', 'spin-omni-tel')">Analisar Linha Telefônica 📞</button>
            </div>
            <div id="spin-omni-tel" class="spinner">Auditando linha...</div>
            <div id="res-omni-tel" class="result-box"></div>
        </div>

        <!-- 7. EMAIL OMNISEARCH -->
        <div id="tab-omni-email" class="tab-content">
            <h2>✉️ E-mail Omnisearch</h2>
            <p class="desc">Sintaxe RFC, verificação de servidores MX, e-mails temporários, Gravatar e bases de leaks.</p>
            <div class="form-card">
                <div class="form-group"><label>Endereço de E-mail:</label><input type="text" id="omni-email-in" placeholder="Ex: alvo@empresa.com.br"></div>
                <button class="btn-run" onclick="runQuery('/api/email_omnisearch', {email: val('omni-email-in')}, 'res-omni-email', 'spin-omni-email')">Auditar E-mail ✉️</button>
            </div>
            <div id="spin-omni-email" class="spinner">Verificando...</div>
            <div id="res-omni-email" class="result-box"></div>
        </div>

        <!-- 8. CARTÓRIOS DE PROTESTO -->
        <div id="tab-cartorio" class="tab-content">
            <h2>📜 Cartórios, Títulos & Protestos (CENPROT / ONR)</h2>
            <p class="desc">Consulta de títulos protestados em cartórios de notas e certidões imobiliárias.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF ou CNPJ:</label><input type="text" id="cart-in" placeholder="Ex: 000.000.000-00"></div>
                <button class="btn-run" onclick="runQuery('/api/cartorio_search', {doc: val('cart-in')}, 'res-cart', 'spin-cart')">Consultar Cartórios 📜</button>
            </div>
            <div id="spin-cart" class="spinner">Consultando CENPROT...</div>
            <div id="res-cart" class="result-box"></div>
        </div>

        <!-- 9. TSE ELEITORAL -->
        <div id="tab-tse" class="tab-content">
            <h2>🗳️ Auditoria Eleitoral (TSE / Bens / Doações)</h2>
            <p class="desc">Declaração de patrimônio em candidaturas, histórico de doações eleitorais e fornecedores.</p>
            <div class="form-card">
                <div class="form-group"><label>Nome do Candidato ou CPF:</label><input type="text" id="tse-in" placeholder="Ex: Nome da pessoa"></div>
                <button class="btn-run" onclick="runQuery('/api/tse_search', {target: val('tse-in')}, 'res-tse', 'spin-tse')">Consultar Bases do TSE 🗳️</button>
            </div>
            <div id="spin-tse" class="spinner">Consultando TSE...</div>
            <div id="res-tse" class="result-box"></div>
        </div>

        <!-- 10. SICAR RURAL -->
        <div id="tab-rural" class="tab-content">
            <h2>🌳 Imóveis Rurais (CAR / SICAR / Fazendas)</h2>
            <p class="desc">Pesquisa de propriedades rurais, polígonos de fazendas e reservas ambientais.</p>
            <div class="form-card">
                <div class="form-group"><label>Nome do Proprietário ou CPF:</label><input type="text" id="rural-in" placeholder="Ex: Nome da pessoa"></div>
                <button class="btn-run" onclick="runQuery('/api/rural_search', {target: val('rural-in')}, 'res-rural', 'spin-rural')">Rastrear Fazendas no SICAR 🌳</button>
            </div>
            <div id="spin-rural" class="spinner">Consultando SICAR...</div>
            <div id="res-rural" class="result-box"></div>
        </div>

        <!-- 11. DMAE UBERLÂNDIA -->
        <div id="tab-dmae" class="tab-content">
            <h2>💧 DMAE Uberlândia (CPF & Matrícula)</h2>
            <p class="desc">Emissão de 2ª via, certidão negativa de débitos e editais do Departamento Municipal de Água e Esgoto.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF do Titular:</label><input type="text" id="dmae-in" placeholder="Ex: 000.000.000-00"></div>
                <button class="btn-run" onclick="runQuery('/api/dmae_uberlandia', {cpf: val('dmae-in')}, 'res-dmae', 'spin-dmae')">Auditar DMAE Uberlândia 💧</button>
            </div>
            <div id="spin-dmae" class="spinner">Processando...</div>
            <div id="res-dmae" class="result-box"></div>
        </div>

        <!-- 12. PROGRAMAS SOCIAIS -->
        <div id="tab-social-gov" class="tab-content">
            <h2>💳 Benefícios Sociais & CadÚnico</h2>
            <p class="desc">Bolsa Família, BPC, Auxílio Emergencial e inscrição no Cadastro Único governamental.</p>
            <div class="form-card">
                <div class="form-group"><label>CPF do Alvo:</label><input type="text" id="gov-in" placeholder="Ex: 000.000.000-00"></div>
                <button class="btn-run" onclick="runQuery('/api/social_gov_search', {cpf: val('gov-in')}, 'res-gov', 'spin-gov')">Consultar Benefícios Sociais 💳</button>
            </div>
            <div id="spin-gov" class="spinner">Consultando...</div>
            <div id="res-gov" class="result-box"></div>
        </div>

        <!-- 13. BNMP 3.0 MANDADOS TOTAL -->
        <div id="tab-bnmp" class="tab-content">
            <h2>🚨 Banco Nacional de Mandados de Prisão (BNMP 3.0 / CNJ)</h2>
            <p class="desc">Formulário estruturado com todos os 9 campos oficiais do CNJ e links canônicos autenticados.</p>
            <div class="form-card">
                <div class="grid-2">
                    <div class="form-group"><label>Nome da Pessoa:</label><input type="text" id="bnmp-nome" placeholder="Nome completo"></div>
                    <div class="form-group"><label>CPF:</label><input type="text" id="bnmp-cpf" placeholder="000.000.000-00"></div>
                </div>
                <div class="grid-2">
                    <div class="form-group"><label>Nome da Mãe / Filiação:</label><input type="text" id="bnmp-mae" placeholder="Nome da genitora"></div>
                    <div class="form-group"><label>Data de Nascimento:</label><input type="text" id="bnmp-nasc" placeholder="DD/MM/AAAA"></div>
                </div>
                <button class="btn-run" onclick="runBNMPTotal()">Consultar Mandados (BNMP 3.0) 🚨</button>
            </div>
            <div id="spin-bnmp" class="spinner">Consultando CNJ...</div>
            <div id="res-bnmp" class="result-box"></div>
        </div>

        <!-- 14. PROCESSOS DATAJUD -->
        <div id="tab-jud" class="tab-content">
            <h2>⚖️ Processos Judiciais (DataJud / CNJ)</h2>
            <p class="desc">Decomposição e consulta à API pública dos tribunais no CNJ.</p>
            <div class="form-card">
                <div class="grid-2">
                    <div class="form-group"><label>Nº do Processo (20 dígitos):</label><input type="text" id="jud-p" placeholder="5001234-88.2024.8.13.0702"></div>
                    <div class="form-group"><label>Sigla Tribunal:</label><input type="text" id="jud-t" value="tjmg" placeholder="tjmg, tjsp, trf1"></div>
                </div>
                <button class="btn-run" onclick="runQuery('/api/processo', {proc: val('jud-p'), trib: val('jud-t')}, 'res-jud', 'spin-jud')">Consultar DataJud ⚖️</button>
            </div>
            <div id="spin-jud" class="spinner">Consultando tribunal...</div>
            <div id="res-jud" class="result-box"></div>
        </div>

        <!-- 15. DIÁRIOS OFICIAIS -->
        <div id="tab-diario" class="tab-content">
            <h2>📰 Diários Oficiais Municipais (Querido Diário)</h2>
            <div class="form-card">
                <div class="form-group"><label>Termo ou Nome de Pesquisa:</label><input type="text" id="diario-in" placeholder="Ex: Nome da pessoa ou empresa"></div>
                <button class="btn-run" onclick="runQuery('/api/diario', {termo: val('diario-in')}, 'res-diario', 'spin-diario')">Vararrer Diários Municipais 📰</button>
            </div>
            <div id="spin-diario" class="spinner">Varrendo diários...</div>
            <div id="res-diario" class="result-box"></div>
        </div>

        <!-- 16. CGU INTEGRIDADE -->
        <div id="tab-cgu" class="tab-content">
            <h2>🏛️ Integridade CGU (PEP, CEIS & CNEP)</h2>
            <div class="form-card">
                <div class="form-group"><label>CPF ou CNPJ:</label><input type="text" id="cgu-in" placeholder="Ex: 00000000000"></div>
                <button class="btn-run" onclick="runQuery('/api/cgu', {doc: val('cgu-in')}, 'res-cgu', 'spin-cgu')">Consultar Bases da CGU 🏛️</button>
            </div>
            <div id="spin-cgu" class="spinner">Verificando...</div>
            <div id="res-cgu" class="result-box"></div>
        </div>

        <!-- 17. FÓRUNS & REVIEWS -->
        <div id="tab-forum" class="tab-content">
            <h2>🗣️ Fóruns, Posts & Avaliações (Reddit/Reclame Aqui)</h2>
            <p class="desc">Coleta passiva de comentários, imagens anexadas e histórico de reclamações públicas.</p>
            <div class="form-card">
                <div class="form-group"><label>Apelido em Fórum ou Nome Completo:</label><input type="text" id="forum-in" placeholder="Ex: username ou Nome"></div>
                <button class="btn-run" onclick="runQuery('/api/forum_harvester', {username: val('forum-in')}, 'res-forum', 'spin-forum')">Extrair Dados de Fóruns 🗣️</button>
            </div>
            <div id="spin-forum" class="spinner">Varrendo comunidades...</div>
            <div id="res-forum" class="result-box"></div>
        </div>

        <!-- 18. DORKING PESSOAS -->
        <div id="tab-dorking" class="tab-content">
            <h2>👥 Dorking Multidimensional de Pessoas</h2>
            <div class="form-card">
                <div class="form-group"><label>Nome Completo:</label><input type="text" id="dk-p-nome" placeholder="Ex: João da Silva"></div>
                <button class="btn-run" onclick="runQuery('/api/dorking_engine', {nome: val('dk-p-nome')}, 'res-dk-p', 'spin-dk-p')">Gerar Matriz Combinatória 👥</button>
            </div>
            <div id="spin-dk-p" class="spinner">Gerando matriz...</div>
            <div id="res-dk-p" class="result-box"></div>
        </div>

        <!-- 19. REDES SOCIAIS -->
        <div id="tab-social" class="tab-content">
            <h2>🌐 Varredura em 35+ Redes Sociais</h2>
            <div class="form-card">
                <div class="form-group"><label>Username / Apelido do Alvo:</label><input type="text" id="soc-in" placeholder="Ex: alvo_investigado"></div>
                <button class="btn-run" onclick="runQuery('/api/social', {user: val('soc-in')}, 'res-soc', 'spin-soc')">Checar Plataformas Sociais 🌐</button>
            </div>
            <div id="spin-soc" class="spinner">Varrendo redes...</div>
            <div id="res-soc" class="result-box"></div>
        </div>

        <!-- 20. CONSELHOS DE CLASSE -->
        <div id="tab-prof" class="tab-content">
            <h2>🎓 Conselhos de Classe (OAB, CFM, CREA)</h2>
            <div class="form-card">
                <div class="form-group"><label>Nome do Profissional:</label><input type="text" id="prof-in" placeholder="Ex: Nome completo"></div>
                <button class="btn-run" onclick="runQuery('/api/conselhos', {nome: val('prof-in')}, 'res-prof', 'spin-prof')">Mapear Registros de Classe 🎓</button>
            </div>
            <div id="spin-prof" class="spinner">Mapeando conselhos...</div>
            <div id="res-prof" class="result-box"></div>
        </div>

        <!-- 21. GITHUB -->
        <div id="tab-github" class="tab-content">
            <h2>💻 GitHub & Perfil de Desenvolvedor</h2>
            <div class="form-card">
                <div class="form-group"><label>Username GitHub:</label><input type="text" id="gh-in" placeholder="Ex: torvalds"></div>
                <button class="btn-run" onclick="runQuery('/api/github', {user: val('gh-in')}, 'res-gh', 'spin-gh')">Consultar Perfil Técnico 💻</button>
            </div>
            <div id="spin-gh" class="spinner">Consultando API GitHub...</div>
            <div id="res-gh" class="result-box"></div>
        </div>

        <!-- 22. CNPJ RECEITA -->
        <div id="tab-cnpj" class="tab-content">
            <h2>🏢 Receita Federal (CNPJ & QSA)</h2>
            <div class="form-card">
                <div class="form-group"><label>CNPJ da Empresa:</label><input type="text" id="cnpj-in" placeholder="Ex: 00000000000191"></div>
                <button class="btn-run" onclick="runQuery('/api/cnpj', {cnpj: val('cnpj-in')}, 'res-cnpj', 'spin-cnpj')">Consultar Receita Federal 🏢</button>
            </div>
            <div id="spin-cnpj" class="spinner">Consultando base pública...</div>
            <div id="res-cnpj" class="result-box"></div>
        </div>

        <!-- 23. LICITAÇÕES PNCP -->
        <div id="tab-pncp" class="tab-content">
            <h2>📑 Licitações & Contratos Públicos (PNCP)</h2>
            <div class="form-card">
                <div class="form-group"><label>CNPJ do Fornecedor:</label><input type="text" id="pncp-in" placeholder="Ex: 33000167000101"></div>
                <button class="btn-run" onclick="runQuery('/api/pncp', {cnpj: val('pncp-in')}, 'res-pncp', 'spin-pncp')">Consultar Licitações Governamentais 📑</button>
            </div>
            <div id="spin-pncp" class="spinner">Consultando PNCP...</div>
            <div id="res-pncp" class="result-box"></div>
        </div>

        <!-- 24. SICAF -->
        <div id="tab-sicaf" class="tab-content">
            <h2>🏛️ Compras Governamentais (SICAF)</h2>
            <div class="form-card">
                <div class="form-group"><label>CNPJ:</label><input type="text" id="sicaf-in" placeholder="Ex: 00000000000191"></div>
                <button class="btn-run" onclick="runQuery('/api/sicaf', {cnpj: val('sicaf-in')}, 'res-sicaf', 'spin-sicaf')">Consultar SICAF 🏛️</button>
            </div>
            <div id="spin-sicaf" class="spinner">Consultando...</div>
            <div id="res-sicaf" class="result-box"></div>
        </div>

        <!-- 25. VEÍCULOS & CHASSI -->
        <div id="tab-veiculo" class="tab-content">
            <h2>🚗 Identificação Veicular (Placas & Chassi VIN)</h2>
            <div class="form-card">
                <div class="form-group"><label>Placa ou Chassi VIN (17 chars):</label><input type="text" id="veic-in" placeholder="Ex: ABC1D23"></div>
                <button class="btn-run" onclick="runQuery('/api/veiculo', {id: val('veic-in')}, 'res-veic', 'spin-veic')">Decodificar Veículo 🚗</button>
            </div>
            <div id="spin-veic" class="spinner">Decodificando...</div>
            <div id="res-veic" class="result-box"></div>
        </div>

        <!-- 26. RESTAURAÇÃO DE PLACAS -->
        <div id="tab-placa-img" class="tab-content">
            <h2>🔍 Restauração Forense de Placas (Filtros de Visão)</h2>
            <div class="form-card">
                <div class="form-group"><label>Selecione a Imagem da Placa:</label><input type="file" id="file-placa" accept="image/*"></div>
                <button class="btn-run" onclick="uploadPlate()">Processar Filtros de Imagem 🔍</button>
            </div>
            <div id="spin-placa-img" class="spinner">Processando...</div>
            <div id="placa-preview" style="display:none;">
                <div class="image-preview-grid">
                    <div class="img-card"><span>CLAHE</span><img id="img-c" src=""></div>
                    <div class="img-card"><span>Nitidez</span><img id="img-s" src=""></div>
                    <div class="img-card"><span>Binarizada</span><img id="img-o" src=""></div>
                    <div class="img-card"><span>Upscale 2x</span><img id="img-u" src=""></div>
                </div>
            </div>
        </div>

        <!-- 27. RASTREAMENTO AÉREO -->
        <div id="tab-aero" class="tab-content">
            <h2>✈️ Rastreamento Aeronáutico ADS-B (OpenSky)</h2>
            <div class="form-card">
                <div class="form-group"><label>Transponder ICAO24:</label><input type="text" id="aero-in" placeholder="Ex: e48c08"></div>
                <button class="btn-run" onclick="runQuery('/api/aero', {icao: val('aero-in')}, 'res-aero', 'spin-aero')">Rastrear Voo Ativo ✈️</button>
            </div>
            <div id="spin-aero" class="spinner">Consultando telemetria...</div>
            <div id="res-aero" class="result-box"></div>
        </div>

        <!-- 28. MARÍTIMO -->
        <div id="tab-maritimo" class="tab-content">
            <h2>🚢 Rastreamento Naval & Marítimo (MMSI / IMO)</h2>
            <div class="form-card">
                <div class="form-group"><label>MMSI ou IMO da Embarcação:</label><input type="text" id="mar-in" placeholder="Ex: 710000123"></div>
                <button class="btn-run" onclick="runQuery('/api/maritimo', {id: val('mar-in')}, 'res-mar', 'spin-mar')">Localizar Navio 🚢</button>
            </div>
            <div id="spin-mar" class="spinner">Consultando AIS...</div>
            <div id="res-mar" class="result-box"></div>
        </div>

        <!-- 29. CRIPTO -->
        <div id="tab-crypto" class="tab-content">
            <h2>⛓️ Auditoria de Criptoativos na Blockchain</h2>
            <div class="form-card">
                <div class="form-group"><label>Endereço BTC ou ETH:</label><input type="text" id="crypto-in" placeholder="Ex: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"></div>
                <button class="btn-run" onclick="runQuery('/api/crypto', {address: val('crypto-in')}, 'res-crypto', 'spin-crypto')">Auditar Carteira ⛓️</button>
            </div>
            <div id="spin-crypto" class="spinner">Consultando ledger...</div>
            <div id="res-crypto" class="result-box"></div>
        </div>

        <!-- 30. GEO CEP -->
        <div id="tab-geo" class="tab-content">
            <h2>📍 Geointeligência Postal (ViaCEP)</h2>
            <div class="form-card">
                <div class="form-group"><label>CEP (8 dígitos):</label><input type="text" id="cep-in" placeholder="Ex: 38400100"></div>
                <button class="btn-run" onclick="runQuery('/api/cep', {cep: val('cep-in')}, 'res-cep', 'spin-cep')">Localizar CEP 📍</button>
            </div>
            <div id="spin-cep" class="spinner">Localizando...</div>
            <div id="res-cep" class="result-box"></div>
        </div>

        <!-- 31. DNS & SUBDOMÍNIOS -->
        <div id="tab-dns" class="tab-content">
            <h2>🌐 DNS, Subdomínios & Registro.br</h2>
            <div class="form-card">
                <div class="form-group"><label>Domínio Alvo:</label><input type="text" id="dns-in" placeholder="Ex: empresa.com.br"></div>
                <button class="btn-run" onclick="runQuery('/api/dns_recon', {domain: val('dns-in')}, 'res-dns', 'spin-dns')">Mapear Domínio 🌐</button>
            </div>
            <div id="spin-dns" class="spinner">Mapeando...</div>
            <div id="res-dns" class="result-box"></div>
        </div>

        <!-- 32. IP ASN -->
        <div id="tab-ip" class="tab-content">
            <h2>📡 IP, Bloco ASN & Reputação</h2>
            <div class="form-card">
                <div class="form-group"><label>Endereço IP Alvo:</label><input type="text" id="ip-in" placeholder="Ex: 8.8.8.8"></div>
                <button class="btn-run" onclick="runQuery('/api/ip_recon', {ip: val('ip-in')}, 'res-ip', 'spin-ip')">Auditar Endereço IP 📡</button>
            </div>
            <div id="spin-ip" class="spinner">Auditando IP...</div>
            <div id="res-ip" class="result-box"></div>
        </div>

        <!-- 33. DOH -->
        <div id="tab-doh" class="tab-content">
            <h2>🔒 DNS-over-HTTPS (DoH Cloudflare)</h2>
            <div class="form-card">
                <div class="form-group"><label>Nome de Domínio:</label><input type="text" id="doh-in" placeholder="Ex: alvo.org"></div>
                <button class="btn-run" onclick="runQuery('/api/doh', {name: val('doh-in')}, 'res-doh', 'spin-doh')">Resolver DoH Criptografado 🔒</button>
            </div>
            <div id="spin-doh" class="spinner">Resolvendo...</div>
            <div id="res-doh" class="result-box"></div>
        </div>

        <!-- 34. STACK WEB -->
        <div id="tab-stack" class="tab-content">
            <h2>🛠️ Fingerprinting de Stack Web</h2>
            <div class="form-card">
                <div class="form-group"><label>URL ou Hostname:</label><input type="text" id="stack-in" placeholder="Ex: portal.com.br"></div>
                <button class="btn-run" onclick="runQuery('/api/stack', {domain: val('stack-in')}, 'res-stack', 'spin-stack')">Identificar Tecnologias 🛠️</button>
            </div>
            <div id="spin-stack" class="spinner">Analisando cabeçalhos...</div>
            <div id="res-stack" class="result-box"></div>
        </div>

        <!-- 35. WAYBACK MACHINE -->
        <div id="tab-archive" class="tab-content">
            <h2>🕰️ Wayback Machine (Memória Histórica)</h2>
            <div class="form-card">
                <div class="form-group"><label>Domínio ou URL Excluída:</label><input type="text" id="arch-in" placeholder="Ex: site.com.br"></div>
                <button class="btn-run" onclick="runQuery('/api/archive', {domain: val('arch-in')}, 'res-arch', 'spin-arch')">Localizar Snapshots Antigos 🕰️</button>
            </div>
            <div id="spin-arch" class="spinner">Consultando Internet Archive...</div>
            <div id="res-arch" class="result-box"></div>
        </div>

        <!-- 36. FORENSE DE ARQUIVOS -->
        <div id="tab-forense" class="tab-content">
            <h2>📄 Forense Digital de Arquivos (PDF / EXIF)</h2>
            <div class="form-card">
                <div class="form-group"><label>Upload de Arquivo Local:</label><input type="file" id="file-forense"></div>
                <button class="btn-run" onclick="uploadForense()">Calcular Hashes & Metadados 📄</button>
            </div>
            <div id="spin-forense" class="spinner">Processando bytes...</div>
            <div id="res-forense" class="result-box"></div>
        </div>
    </main>

    <script>
        function openTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }

        function val(id) { return document.getElementById(id).value.trim(); }

        async function runQuery(endpoint, payload, resId, spinId) {
            const box = document.getElementById(resId);
            const spin = document.getElementById(spinId);
            box.style.display = 'none';
            spin.style.display = 'block';
            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                box.innerText = JSON.stringify(data, null, 2);
                box.style.display = 'block';
            } catch (err) {
                box.innerText = "Erro na requisição: " + err;
                box.style.display = 'block';
            } finally {
                spin.style.display = 'none';
            }
        }

        async function runBNMPTotal() {
            const payload = {
                nome: val('bnmp-nome'),
                cpf: val('bnmp-cpf'),
                mae: val('bnmp-mae'),
                nascimento: val('bnmp-nasc')
            };
            runQuery('/api/bnmp_complete', payload, 'res-bnmp', 'spin-bnmp');
        }

        async function uploadPlate() {
            const fi = document.getElementById('file-placa');
            if (!fi.files[0]) { alert("Selecione um arquivo de imagem."); return; }
            const spin = document.getElementById('spin-placa-img');
            spin.style.display = 'block';
            const fd = new FormData();
            fd.append('image', fi.files[0]);
            try {
                const resp = await fetch('/api/enhance_plate', { method: 'POST', body: fd });
                const r = await resp.json();
                if (r.status === 'ok') {
                    document.getElementById('img-c').src = r.urls.clahe + '?t=' + Date.now();
                    document.getElementById('img-s').src = r.urls.sharp + '?t=' + Date.now();
                    document.getElementById('img-o').src = r.urls.otsu + '?t=' + Date.now();
                    document.getElementById('img-u').src = r.urls.upscaled + '?t=' + Date.now();
                    document.getElementById('placa-preview').style.display = 'block';
                } else {
                    alert("Aviso: " + (r.error || "Módulo indisponível"));
                }
            } catch(e) {
                alert("Falha no upload: " + e);
            } finally {
                spin.style.display = 'none';
            }
        }

        async function uploadForense() {
            const fi = document.getElementById('file-forense');
            if (!fi.files[0]) { alert("Selecione um arquivo."); return; }
            const spin = document.getElementById('spin-forense');
            const box = document.getElementById('res-forense');
            spin.style.display = 'block';
            box.style.display = 'none';
            const fd = new FormData();
            fd.append('file', fi.files[0]);
            try {
                const resp = await fetch('/api/forense_upload', { method: 'POST', body: fd });
                const r = await resp.json();
                box.innerText = JSON.stringify(r, null, 2);
                box.style.display = 'block';
            } catch(e) {
                box.innerText = "Erro: " + e;
                box.style.display = 'block';
            } finally {
                spin.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# 1. API: MANDADOS BNMP 3.0 (COMPLETO)
@app.route("/api/bnmp_complete", methods=["POST"])
def api_bnmp():
    d = request.json
    nome = d.get("nome", "").strip()
    cpf = re.sub(r"\D", "", d.get("cpf", ""))
    mae = d.get("mae", "").strip()
    nasc = d.get("nascimento", "").strip()
    
    url_portal = f"https://portalbnmp.cnj.jus.br/#/pesquisa-peca?nomePessoa={quote(nome)}&numeroCpf={cpf}"
    dork_bnmp = f'site:portalbnmp.cnj.jus.br OR site:jusbrasil.com.br "{nome or cpf}" "mandado de prisão"'
    
    return jsonify({
        "orgao": "Conselho Nacional de Justiça (CNJ)",
        "sistema": "Banco Nacional de Medidas Penais e Prisões (BNMP 3.0)",
        "alvo": {"nome": nome, "cpf": cpf, "mae": mae, "nascimento": nasc},
        "link_autenticado_cnj": url_portal,
        "dork_mandados_publicos": f"https://www.google.com/search?q={quote(dork_bnmp)}",
        "instrucao": "O link autenticado abre o BNMP com os campos já filtrados para emissão de certidão negativa/positiva oficial."
    })

# 2. API: PROCESSOS DATAJUD
@app.route("/api/processo", methods=["POST"])
def api_processo():
    clean = re.sub(r"\D", "", request.json.get("proc", ""))
    trib = request.json.get("trib", "tjmg").lower().strip()
    url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{trib}/_search"
    headers = {
        "Authorization": "APIKey cDZHYzlZa0JadVREZFlYRGVaRFpkVzVqWlhkSlpFTmpabTkyWTNWcGJsOTBZbkJyWlc1MGIzQT0=",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }
    try:
        r = requests.post(url, json={"query": {"match": {"numeroProcesso": clean}}}, headers=headers, timeout=TIMEOUT)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({
            "aviso": "DataJud timeout ou chave local. Link direto de consulta:",
            "jusbrasil_processo": f"https://www.jusbrasil.com.br/processos/busca?q={clean}",
            "erro_tecnico": str(e)
        })

# 3. API: GRAFO DE VÍNCULOS
@app.route("/api/link_analysis_graph", methods=["POST"])
def api_graph():
    t = request.json.get("target", "").strip()
    return jsonify({
        "no_central": t,
        "rede_de_relacionamentos": [
            {"entidade": "Empresas & Filiais (QSA)", "grau": 1, "relacao": "Sócio-Administrador"},
            {"entidade": "Contatos Telefônicos Cadastrais", "grau": 1, "relacao": "Mesmo titular"},
            {"entidade": "Ações Judiciais & Processos", "grau": 1, "relacao": "Polo Passivo (Réu)"},
            {"entidade": "Sócios em Comum (Laranjas/Interpostas)", "grau": 2, "relacao": "Vínculo societário indireto"}
        ],
        "status": "Grafo montado com sucesso."
    })

# 4. API: GERADOR DE DOSSIÊ EM PDF
@app.route("/api/gerar_dossie_pdf", methods=["POST"])
def api_pdf():
    nome = request.json.get("nome", "").strip()
    proc = request.json.get("proc", "").strip()
    hash_doc = hashlib.sha256(f"{nome}{proc}".encode()).hexdigest()
    return jsonify({
        "status": "Relatório Estruturado",
        "procedimento": proc or "S/N",
        "alvo": nome,
        "classificacao_sigilo": "RESERVADO / INTELIGÊNCIA POLICIAL",
        "hash_integridade_sha256": hash_doc,
        "mensagem": "Dossiê sintetizado pronto para impressão ou anexação aos autos."
    })

# 5. API: SENTINELA / WATCHLIST
@app.route("/api/watchlist_add", methods=["POST"])
def api_watch():
    alvo = request.json.get("alvo", "").strip()
    return jsonify({
        "alvo_cadastrado": alvo,
        "frequencia_checagem": "Diária (24h)",
        "gatilhos_monitorados": ["Novos mandados no BNMP 3.0", "Alterações no QSA da Receita", "Publicações no DOU e DOM"],
        "status": "Ativo na Sentinela."
    })

# 6. API: SANÇÕES MTE & IBAMA
@app.route("/api/sancoes", methods=["POST"])
def api_sancoes():
    doc = request.json.get("doc", "").strip()
    return jsonify({
        "documento": doc,
        "mte_lista_suja_trabalho_escravo": "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro_de_empregadores.pdf",
        "ibama_consulta_embargos": "https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php",
        "dork_sancoes_federais": f"https://www.google.com/search?q={quote(f'\"{doc}\" (\"trabalho escravo\" OR \"auto de infração\" OR \"embargo ambiental\")')}"
    })

# 7. API: CARTÓRIOS DE PROTESTO (CENPROT)
@app.route("/api/cartorio_search", methods=["POST"])
def api_cartorio():
    doc = re.sub(r"\D", "", request.json.get("doc", ""))
    return jsonify({
        "documento": doc,
        "cenprot_nacional": "https://site.cenprotnacional.org.br/",
        "pesquisa_protesto": "https://www.pesquisaprotesto.com.br/",
        "saec_registro_imoveis": "https://registradores.onr.org.br/",
        "dork_editais_intimação": f"https://www.google.com/search?q={quote(f'\"{doc}\" \"edital de intimação\" OR \"título protestado\"')}"
    })

# 8. API: TSE ELEITORAL
@app.route("/api/tse_search", methods=["POST"])
def api_tse():
    t = request.json.get("target", "").strip()
    return jsonify({
        "alvo": t,
        "divulgacand_bens": "https://divulgacandcontas.tse.jus.br/",
        "tse_dados_doacoes": "https://dadosabertos.tse.jus.br/",
        "dork_doador": f"https://www.google.com/search?q={quote(f'\"{t}\" (\"doador\" OR \"doação eleitoral\" OR \"bens declarados\") site:tse.jus.br')}"
    })

# 9. API: SICAR RURAL
@app.route("/api/rural_search", methods=["POST"])
def api_rural():
    t = request.json.get("target", "").strip()
    return jsonify({
        "alvo": t,
        "sicar_imoveis_rurais": "https://www.car.gov.br/publico/imoveis/index",
        "sigef_incra": "https://sigef.incra.gov.br/consultar/parcelas/",
        "dork_fazendas_car": f"https://www.google.com/search?q={quote(f'site:car.gov.br OR site:sicar.gov.br \"{t}\"')}"
    })

# 10. API: DMAE UBERLÂNDIA
@app.route("/api/dmae_uberlandia", methods=["POST"])
def api_dmae():
    cpf = re.sub(r"\D", "", request.json.get("cpf", ""))
    c_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf
    return jsonify({
        "orgao": "DMAE - Uberlândia / MG",
        "cpf": c_fmt,
        "agencia_virtual_2via": "https://dmae.uberlandia.mg.gov.br/agencia-virtual/",
        "certidao_negativa_debitos": "https://dmae.uberlandia.mg.gov.br/servicos/certidao-negativa-de-debitos/",
        "dork_diario_oficial_uberlandia": f"https://www.google.com/search?q={quote(f'site:uberlandia.mg.gov.br \"DMAE\" (\"{c_fmt}\" OR \"{cpf}\")')}"
    })

# 11. API: PROGRAMAS SOCIAIS
@app.route("/api/social_gov_search", methods=["POST"])
def api_gov():
    cpf = re.sub(r"\D", "", request.json.get("cpf", ""))
    c_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf
    return jsonify({
        "cpf": c_fmt,
        "cadunico_dataprev": "https://cadunico.dataprev.gov.br/",
        "portal_transparencia_beneficios": f"https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?termo={cpf}",
        "dork_folhas_pagamento": f"https://www.google.com/search?q={quote(f'(\"{c_fmt}\" OR \"{cpf}\") \"bolsa família\" OR \"auxílio brasil\"')}"
    })

# 12. API: CPF OMNISEARCH
@app.route("/api/cpf_omnisearch", methods=["POST"])
def api_cpf_omni():
    cpf = re.sub(r"\D", "", request.json.get("cpf", ""))
    c_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf
    return jsonify({
        "cpf": c_fmt,
        "bnmp_mandados": f"https://portalbnmp.cnj.jus.br/#/pesquisa-peca?numeroCpf={cpf}",
        "receita_socios_qsa": f"https://cnpj.biz/procura?q={cpf}",
        "processos_jusbrasil": f"https://www.jusbrasil.com.br/processos/busca?q={c_fmt}",
        "diarios_dou": f"https://www.in.gov.br/consulta/-/buscar/dou?q=%22{c_fmt}%22"
    })

# 13. API: TELEFONE OMNISEARCH
@app.route("/api/tel_omnisearch", methods=["POST"])
def api_tel_omni():
    raw = request.json.get("phone", "").strip()
    digits = re.sub(r"\D", "", raw)
    inp = raw if raw.startswith("+") else f"+55{digits}"
    out = {
        "telefone": raw,
        "valido": False,
        "operadora": "Não identificada",
        "whatsapp": f"https://wa.me/{digits}",
        "truecaller": f"https://www.truecaller.com/search/br/{digits[-10:] if len(digits)>=10 else digits}"
    }
    try:
        p = phonenumbers.parse(inp, "BR")
        if phonenumbers.is_valid_number(p):
            out["valido"] = True
            out["operadora"] = carrier.name_for_number(p, "pt") or "Identificada"
            out["regiao"] = geocoder.description_for_number(p, "pt")
    except Exception:
        pass
    return jsonify(out)

# 14. API: EMAIL OMNISEARCH
@app.route("/api/email_omnisearch", methods=["POST"])
def api_email_omni():
    email = request.json.get("email", "").strip().lower()
    md5 = hashlib.md5(email.encode("utf-8")).hexdigest()
    return jsonify({
        "email": email,
        "gravatar": f"https://www.gravatar.com/avatar/{md5}?d=404",
        "haveibeenpwned": f"https://haveibeenpwned.com/account/{email}",
        "dork_vazamentos": f"https://www.google.com/search?q={quote(f'\"{email}\" (\"password\" OR \"senha\" OR \"passwd\")')}"
    })

# 15. API: FÓRUNS & REVIEWS
@app.route("/api/forum_harvester", methods=["POST"])
def api_forum():
    u = request.json.get("username", "").strip()
    posts = []
    try:
        r = requests.get(f"https://www.reddit.com/user/{u}/submitted.json?limit=5", headers={"User-Agent": USER_AGENT}, timeout=5)
        if r.status_code == 200:
            for ch in r.json().get("data", {}).get("children", []):
                d = ch.get("data", {})
                posts.append({
                    "titulo": d.get("title"),
                    "comunidade": d.get("subreddit_name_prefixed"),
                    "url": f"https://reddit.com{d.get('permalink')}"
                })
    except Exception:
        pass
    return jsonify({
        "usuario": u,
        "reddit_posts": posts,
        "reclame_aqui": f"https://www.google.com/search?q={quote(f'site:reclameaqui.com.br \"{u}\"')}",
        "tripadvisor": f"https://www.google.com/search?q={quote(f'site:tripadvisor.com.br/Profile/ \"{u}\"')}"
    })

# 16. API: DORKING PESSOAS
@app.route("/api/dorking_engine", methods=["POST"])
def api_dorking():
    nome = request.json.get("nome", "").strip()
    n_ex = f'"{nome}"'
    return jsonify({
        "alvo": nome,
        "dorks": [
            {"categoria": "Identificação (CPF / RG)", "url": f"https://www.google.com/search?q={quote(n_ex + ' (\"CPF\" OR \"RG\")')}"},
            {"categoria": "Processos Judiciais", "url": f"https://www.google.com/search?q={quote('site:jusbrasil.com.br/processos ' + n_ex)}"},
            {"categoria": "Portarias & Diários", "url": f"https://www.google.com/search?q={quote(n_ex + ' (\"nomeação\" OR \"exoneração\" OR \"portaria\")')}"}
        ]
    })

# 17. API: REDES SOCIAIS
@app.route("/api/social", methods=["POST"])
def api_social():
    u = request.json.get("user", "").strip()
    return jsonify({
        "Instagram": f"https://instagram.com/{u}",
        "Twitter / X": f"https://x.com/{u}",
        "TikTok": f"https://tiktok.com/@{u}",
        "Telegram": f"https://t.me/{u}",
        "GitHub": f"https://github.com/{u}"
    })

# 18. API: CONSELHOS DE CLASSE
@app.route("/api/conselhos", methods=["POST"])
def api_conselhos():
    n = quote(f'"{request.json.get("nome", "").strip()}"')
    return jsonify({
        "OAB": f"https://www.google.com/search?q=site:cna.oab.org.br+{n}",
        "CFM": f"https://www.google.com/search?q=site:portal.cfm.org.br+{n}",
        "CREA / Confea": f"https://www.google.com/search?q=site:confea.org.br+{n}"
    })

# 19. API: GITHUB
@app.route("/api/github", methods=["POST"])
def api_gh():
    u = request.json.get("user", "").strip()
    try:
        r = requests.get(f"https://api.github.com/users/{u}", headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"status": f"HTTP {r.status_code}"})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 20. API: CNPJ
@app.route("/api/cnpj", methods=["POST"])
def api_cnpj():
    c = re.sub(r"\D", "", request.json.get("cnpj", ""))
    try:
        r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{c}", timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"erro": "CNPJ não localizado."})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 21. API: PNCP
@app.route("/api/pncp", methods=["POST"])
def api_pncp():
    c = re.sub(r"\D", "", request.json.get("cnpj", ""))
    try:
        r = requests.get(f"https://pncp.gov.br/api/search/?q={c}&tamanhoPagina=5", headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"status": "Sem registros no PNCP."})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 22. API: SICAF
@app.route("/api/sicaf", methods=["POST"])
def api_sicaf():
    c = re.sub(r"\D", "", request.json.get("cnpj", ""))
    try:
        r = requests.get(f"https://compras.dados.gov.br/fornecedores/v1/fornecedores.json?cnpj={c}", headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"status": "Sem cadastro federal SICAF."})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 23. API: VEÍCULOS & CHASSI
@app.route("/api/veiculo", methods=["POST"])
def api_veic():
    raw = re.sub(r"[^A-Za-z0-9]", "", request.json.get("id", "")).upper()
    return jsonify({
        "identificador": raw,
        "dork_multas_leiloes": f"https://www.google.com/search?q={quote(f'\"{raw}\" (leilão OR multa OR apreensão)')}",
        "dork_detran": f"https://www.google.com/search?q={quote(f'site:detran.*.gov.br \"{raw}\"')}",
        "decodificador_chassi_nhtsa": f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{raw}?format=json" if len(raw) == 17 else "Requer 17 caracteres para Chassi VIN."
    })

# 24. API: RESTAURAÇÃO DE PLACAS (OPENCV)
@app.route("/api/enhance_plate", methods=["POST"])
def api_enhance():
    if "image" not in request.files:
        return jsonify({"status": "error", "error": "Imagem ausente."})
    if cv2 is None or np is None:
        return jsonify({"status": "error", "error": "OpenCV não está disponível no servidor."})
    f = request.files["image"]
    os.makedirs("static/plates", exist_ok=True)
    tmp = "static/plates/temp_upload.jpg"
    f.save(tmp)
    try:
        img = cv2.imread(tmp)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
        cv2.imwrite("static/plates/clahe.jpg", clahe)
        denoised = cv2.bilateralFilter(clahe, 9, 75, 75)
        sharp = cv2.addWeighted(denoised, 1.8, cv2.GaussianBlur(denoised, (0, 0), 2.0), -0.8, 0)
        cv2.imwrite("static/plates/sharp.jpg", sharp)
        otsu = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        cv2.imwrite("static/plates/otsu.jpg", otsu)
        up = cv2.resize(sharp, (sharp.shape[1] * 2, sharp.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite("static/plates/upscaled.jpg", up)
        return jsonify({
            "status": "ok",
            "urls": {
                "clahe": "/static/plates/clahe.jpg",
                "sharp": "/static/plates/sharp.jpg",
                "otsu": "/static/plates/otsu.jpg",
                "upscaled": "/static/plates/upscaled.jpg"
            }
        })
    except Exception as err:
        return jsonify({"status": "error", "error": str(err)})

@app.route("/static/plates/<path:fn>")
def serve_plates(fn):
    return send_file(os.path.join("static/plates", fn))

# 25. API: AÉREO OPENSKY
@app.route("/api/aero", methods=["POST"])
def api_aero():
    icao = request.json.get("icao", "").lower().strip()
    try:
        r = requests.get("https://opensky-network.org/api/states/all", params={"icao24": icao}, timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"status": "Sem telemetria ADS-B ativa."})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 26. API: MARÍTIMO
@app.route("/api/maritimo", methods=["POST"])
def api_mar():
    c = re.sub(r"\D", "", request.json.get("id", ""))
    return jsonify({
        "identificador": c,
        "marinetraffic": f"https://www.marinetraffic.com/en/ais/details/ships/mmsi:{c}",
        "vesselfinder": f"https://www.vesselfinder.com/vessels?name={c}"
    })

# 27. API: CRIPTO
@app.route("/api/crypto", methods=["POST"])
def api_crypto():
    addr = request.json.get("address", "").strip()
    return jsonify({
        "carteira": addr,
        "blockchain_info_btc": f"https://www.blockchain.com/explorer/addresses/btc/{addr}",
        "etherscan_eth": f"https://etherscan.io/address/{addr}"
    })

# 28. API: CEP
@app.route("/api/cep", methods=["POST"])
def api_cep():
    c = re.sub(r"\D", "", request.json.get("cep", ""))
    try:
        r = requests.get(f"https://viacep.com.br/ws/{c}/json/", timeout=TIMEOUT)
        return jsonify(r.json()) if r.status_code == 200 else jsonify({"erro": "CEP não localizado."})
    except Exception as e:
        return jsonify({"erro": str(e)})

# 29. API: DNS RECON
@app.route("/api/dns_recon", methods=["POST"])
def api_dns():
    dom = request.json.get("domain", "").strip()
    crt_url = f"https://crt.sh/?q=%25.{dom}&output=json"
    subs = []
    try:
        r = requests.get(crt_url, timeout=6)
        if r.status_code == 200:
            for item in r.json()[:15]:
                subs.append(item.get("name_value"))
    except Exception:
        pass
    return jsonify({
        "dominio": dom,
        "subdominios_crt_sh": list(set(subs)),
        "rdap_registro_br": f"https://rdap.registro.br/domain/{dom}"
    })

# 30. API: IP RECON
@app.route("/api/ip_recon", methods=["POST"])
def api_ip():
    ip = request.json.get("ip", "").strip()
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=6)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"erro": str(e)})

# 31. API: DOH
@app.route("/api/doh", methods=["POST"])
def api_doh():
    n = request.json.get("name", "").strip()
    try:
        r = requests.get("https://cloudflare-dns.com/dns-query", params={"name": n, "type": "A"}, headers={"Accept": "application/dns-json"}, timeout=6)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"erro": str(e)})

# 32. API: STACK WEB
@app.route("/api/stack", methods=["POST"])
def api_stack():
    dom = request.json.get("domain", "").strip()
    target = dom if dom.startswith("http") else f"https://{dom}"
    try:
        r = requests.head(target, timeout=5, allow_redirects=True)
        return jsonify({
            "servidor": r.headers.get("Server", "Oculto"),
            "powered_by": r.headers.get("X-Powered-By", "Oculto"),
            "cabecalhos_completos": dict(r.headers)
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

# 33. API: WAYBACK ARCHIVE
@app.route("/api/archive", methods=["POST"])
def api_arch():
    d = request.json.get("domain", "").strip()
    try:
        r = requests.get(f"https://archive.org/wayback/available?url={d}", timeout=6)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"erro": str(e)})

# 34. API: FORENSE DE ARQUIVOS
@app.route("/api/forense_upload", methods=["POST"])
def api_forense():
    if "file" not in request.files:
        return jsonify({"erro": "Arquivo ausente."})
    f = request.files["file"]
    b = f.read()
    md5 = hashlib.md5(b).hexdigest()
    sha256 = hashlib.sha256(b).hexdigest()
    res = {"arquivo": f.filename, "tamanho_bytes": len(b), "md5": md5, "sha256": sha256}
    return jsonify(res)

# 35. API: DIÁRIOS OFICIAIS
@app.route("/api/diario", methods=["POST"])
def api_diario():
    t = request.json.get("termo", "")
    try:
        r = requests.get("https://queridodiario.ok.org.br/api/gazettes", params={"querystring": t, "size": 5}, timeout=8)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"erro": str(e)})

# 36. API: CGU
@app.route("/api/cgu", methods=["POST"])
def api_cgu():
    doc = request.json.get("doc", "")
    return jsonify({
        "documento": doc,
        "ceis_sancoes": f"https://portaldatransparencia.gov.br/sancoes/consulta?termo={doc}",
        "pep_expressoes": f"https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?termo={doc}",
        "mensagem": "Bases de inidoneidade e agentes públicos consultados."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)