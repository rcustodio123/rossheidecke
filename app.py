from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import webbrowser  # Adicionado para abrir o link no navegador

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"

# Constantes para curvas de depreciação
CURVAS_DEPRECIACAO = {
    "a": 0.0,
    "b": 0.0032,
    "c": 0.0252,
    "d": 0.0809,
    "e": 0.1810,
    "f": 0.3320,
    "g": 0.5260,
    "h": 0.7520,
    "i": 1.0
}
DESCRICAO_CURVAS = (
    "Classificação do estado do imóvel:\n"
    "a = Novo\n"
    "b = Entre novo e regular\n"
    "c = Regular\n"
    "d = Entre regular e reparos simples\n"
    "e = Reparos simples\n"
    "f = Entre reparos simples e importantes\n"
    "g = Reparos importantes\n"
    "h = Entre reparos importantes e sem valor\n"
    "i = Sem valor"
)

# Link da tabela CUB
LINK_CUB = "https://sindusconpr.com.br/tabela-completa-370-p"

# Função para abrir o link da tabela CUB
def abrir_link_cub():
    webbrowser.open(LINK_CUB)

# Função para calcular o custo de reedificação
def calcular_custo(CUB, BDI, area, idade_aparente, vida_util, opcao):
    try:
        # Validação das entradas
        CUB = round(float(CUB), 2)
        BDI = round(float(BDI), 4)
        area = round(float(area), 2)
        idade_aparente = int(idade_aparente)
        vida_util = int(vida_util)

        if opcao not in CURVAS_DEPRECIACAO:
            raise ValueError("Selecione uma opção válida para a curva de depreciação!")

        # Cálculos principais
        Valor_do_imovel_novo = round(CUB * area, 2)
        Valor_depreciavel = round(0.8 * Valor_do_imovel_novo, 2)
        Valor_Residual = round(Valor_do_imovel_novo - Valor_depreciavel, 2)
        dummy1 = idade_aparente / vida_util

        C = CURVAS_DEPRECIACAO[opcao]
        K = round((0.5 * (dummy1 + dummy1 ** 2) + (1.0 - 0.5 * (dummy1 + dummy1 ** 2)) * C) * 100, 2)
        C_depreciacao = round(1 - K / 100, 2)
        Custo_de_reedicao = round(((Valor_depreciavel * C_depreciacao) + Valor_Residual) * BDI, 2)

        # Formatando o resultado
        return (
            f"Resultados:\n"
            f"Valor do Imóvel Novo (Sem BDI): R$ {Valor_do_imovel_novo:.2f}\n"
            f"Valor Residual (20%): R$ {Valor_Residual:.2f}\n"
            f"Valor Depreciável (80%): R$ {Valor_depreciavel:.2f}\n"
            f"K: {K:.2f}% (Extraída da Tabela de Ross-Heidecke)\n"
            f"Fator de Depreciação: {C_depreciacao:.2f}\n"
            f"Custo de Reedificação (com BDI): R$ {Custo_de_reedicao:.2f}\n"
            f"[({Valor_depreciavel:.2f} x {C_depreciacao:.2f}) + {Valor_Residual:.2f}] x {BDI:.4f}"
        )

    except ValueError as e:
        return f"Erro: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        CUB = request.form.get("cub")
        BDI = request.form.get("bdi")
        area = request.form.get("area")
        idade_aparente = request.form.get("idade")
        vida_util = request.form.get("vida_util")
        opcao = request.form.get("opcao")

        resultado = calcular_custo(CUB, BDI, area, idade_aparente, vida_util, opcao)
        flash(resultado)

    return render_template("index.html", descricao_curvas=DESCRICAO_CURVAS, resultado=resultado, link_cub=LINK_CUB)

if __name__ == "__main__":
    app.run(debug=True)
