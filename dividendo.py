from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Função para formatar os valores em reais
def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para calcular o investimento com reinvestimento de dividendos e aportes mensais
def calcular_investimento(valor_inicial, aporte_mensal, anos, juros_ano):
    juros_mensal = (1 + juros_ano) ** (1 / 12) - 1
    saldo = valor_inicial
    total_dividendos = 0
    total_aportado = valor_inicial
    historico = []

    for mes in range(1, anos * 12 + 1):
        dividendos = saldo * juros_mensal
        total_dividendos += dividendos
        saldo += dividendos + aporte_mensal
        total_aportado += aporte_mensal

        historico.append({
            'Mês': mes,
            'Saldo (R$)': formatar_reais(saldo),
            'Dividendos do Mês (R$)': formatar_reais(dividendos),
            'Aporte (R$)': formatar_reais(aporte_mensal),
            'Dividendos Acumulados (R$)': formatar_reais(total_dividendos),
            'Total Aportado (R$)': formatar_reais(total_aportado)
        })

    df_historico = pd.DataFrame(historico)

    saldo_final = formatar_reais(saldo)
    total_aportado = formatar_reais(total_aportado)
    total_dividendos = formatar_reais(total_dividendos)
    rendimento_total = formatar_reais(saldo - valor_inicial)

    return {
        'df_historico': df_historico,
        'saldo_final': saldo_final,
        'total_aportado': total_aportado,
        'total_dividendos': total_dividendos,
        'rendimento_total': rendimento_total
    }

# Função para gerar o gráfico e retornar a imagem em base64
def gerar_grafico(df_historico):
    df_historico_numeric = df_historico.copy()
    df_historico_numeric['Saldo (R$)'] = df_historico_numeric['Saldo (R$)'].apply(lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.')))
    df_historico_numeric['Dividendos Acumulados (R$)'] = df_historico_numeric['Dividendos Acumulados (R$)'].apply(lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.')))
    df_historico_numeric['Total Aportado (R$)'] = df_historico_numeric['Total Aportado (R$)'].apply(lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.')))

    plt.figure(figsize=(10, 6))
    plt.plot(df_historico_numeric['Mês'], df_historico_numeric['Saldo (R$)'], label='Saldo Total (R$)', color='blue')
    plt.plot(df_historico_numeric['Mês'], df_historico_numeric['Dividendos Acumulados (R$)'], label='Dividendos Acumulados (R$)', color='green')
    plt.plot(df_historico_numeric['Mês'], df_historico_numeric['Total Aportado (R$)'], label='Total Aportado (R$)', color='orange')
    plt.xlabel('Mês')
    plt.ylabel('Valor (R$)')
    plt.title('Evolução do Saldo, Dividendos e Aportes')
    plt.legend()
    plt.grid(True)

    # Converter o gráfico em imagem
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url

# Rota principal que aceita GET e POST
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    grafico_url = None
    df_historico_html = None

    if request.method == "POST":
        valor_inicial = float(request.form['valor_inicial'])
        aporte_mensal = float(request.form['aporte_mensal'])
        anos = int(request.form['anos'])
        juros_ano = float(request.form['juros_ano']) / 100  # Converter para decimal

        resultado = calcular_investimento(valor_inicial, aporte_mensal, anos, juros_ano)

        # Gerar gráfico
        grafico_url = gerar_grafico(resultado['df_historico'])

        # Converter o DataFrame em tabela HTML
        df_historico_html = resultado['df_historico'].to_html(classes='table table-striped', index=False)

    return render_template("index.html", resultado=resultado, grafico_url=grafico_url, df_historico_html=df_historico_html)

if __name__ == "__main__":
    app.run(debug=True)
