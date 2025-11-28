import mysql.connector
from datetime import datetime

print("Sistema QA")
print("Digite os valores dos poluentes.")
print("Se digitar 0, o programa continua; se negativo, encerra.\n")

resultados = []

faixas = {
    "PM10":  [(0, 50, 0, 40), (51, 100, 41, 80), (101, 150, 81, 120), (151, 250, 121, 200), (251, 600, 201, 300)],
    "PM25":  [(0, 25, 0, 40), (26, 50, 41, 80), (51, 75, 81, 120), (76, 125, 121, 200), (126, 300, 201, 300)],
    "O3":    [(0, 100, 0, 40), (101, 130, 41, 80), (131, 160, 81, 120), (161, 200, 121, 200), (201, 400, 201, 300)],
    "CO":    [(0, 4, 0, 40), (5, 9, 41, 80), (10, 13, 81, 120), (14, 15, 121, 200), (16, 50, 201, 300)],
    "NO2":   [(0, 200, 0, 40), (201, 240, 41, 80), (241, 320, 81, 120), (321, 1130, 121, 200), (1131, 4000, 201, 300)],
    "SO2":   [(0, 20, 0, 40), (21, 40, 41, 80), (41, 365, 81, 120), (366, 800, 121, 200), (801, 1600, 201, 300)]
}

def conectar_banco():
    """
    Ajuste os parâmetros de conexão com o seu MySQL aqui.
    """
    conexao = mysql.connector.connect(
        host="localhost",  # <-- troque
        user="root",      # <-- troque
        password="",    # <-- troque
        database="qualidade_ar"  # <-- crie esse database ou troque o nome
    )
    return conexao

def criar_tabela(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medidas_iqa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_hora DATETIME NOT NULL,
            pm10 FLOAT,
            pm25 FLOAT,
            o3 FLOAT,
            co FLOAT,
            no2 FLOAT,
            so2 FLOAT,
            i_pm10 FLOAT,
            i_pm25 FLOAT,
            i_o3 FLOAT,
            i_co FLOAT,
            i_no2 FLOAT,
            i_so2 FLOAT,
            iqa_max FLOAT,
            qualidade VARCHAR(20),
            efeito TEXT
        )
    """)
    conexao.commit()
    cursor.close()

def salvar_medida(conexao, dados):
    """
    dados é um dicionário com todos os valores da medição.
    """
    cursor = conexao.cursor()
    sql = """
        INSERT INTO medidas_iqa
        (data_hora, pm10, pm25, o3, co, no2, so2,
         i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2,
         iqa_max, qualidade, efeito)
        VALUES (%s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s)
    """
    valores = (
        dados["data_hora"],
        dados["pm10"],
        dados["pm25"],
        dados["o3"],
        dados["co"],
        dados["no2"],
        dados["so2"],
        dados["i_pm10"],
        dados["i_pm25"],
        dados["i_o3"],
        dados["i_co"],
        dados["i_no2"],
        dados["i_so2"],
        dados["iqa_max"],
        dados["qualidade"],
        dados["efeito"]
    )
    cursor.execute(sql, valores)
    conexao.commit()
    cursor.close()

def calcular_iqa(valor, tabela):
    for (cl, ch, il, ih) in tabela:
        if cl <= valor <= ch:
            return ((ih - il) / (ch - cl)) * (valor - cl) + il
    return 300

conexao = conectar_banco()
criar_tabela(conexao)

while True:
    pm10 = float(input("PM10 (µg/m3): "))
    pm25 = float(input("PM2.5 (µg/m3): "))
    o3 = float(input("O3 (µg/m3): "))
    co = float(input("CO (ppm): "))
    no2 = float(input("NO2 (µg/m3): "))
    so2 = float(input("SO2 (µg/m3): "))

    if any(v < 0 for v in [pm10, pm25, o3, co, no2, so2]):
        print("\nValor negativo detectado. Encerrando...")
        break

    if any(v == 0 for v in [pm10, pm25, o3, co, no2, so2]):
        print("\nValor ZERO detectado. Continuando...\n")

    i_pm10 = calcular_iqa(pm10, faixas["PM10"])
    i_pm25 = calcular_iqa(pm25, faixas["PM25"])
    i_o3   = calcular_iqa(o3, faixas["O3"])
    i_co   = calcular_iqa(co, faixas["CO"])
    i_no2  = calcular_iqa(no2, faixas["NO2"])
    i_so2  = calcular_iqa(so2, faixas["SO2"])

    indices = [i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2]
    maior = max(indices)
    resultados.extend(indices)

    print("\n--- ÍNDICES OFICIAIS IQA ---")
    print(f"PM10: {i_pm10:.1f}")
    print(f"PM2.5: {i_pm25:.1f}")
    print(f"O3: {i_o3:.1f}")
    print(f"CO: {i_co:.1f}")
    print(f"NO2: {i_no2:.1f}")
    print(f"SO2: {i_so2:.1f}")

    print(f"\n>> IQA Atual (maior índice): {maior:.1f}")

    if maior <= 40:
        qualidade = "Boa"
        efeito = "Nenhum efeito à saúde."
    elif maior <= 80:
        qualidade = "Moderada"
        efeito = "Pode causar leve desconforto em sensíveis."
    elif maior <= 120:
        qualidade = "Ruim"
        efeito = "Irritação nos olhos e respiração difícil."
    elif maior <= 200:
        qualidade = "Muito Ruim"
        efeito = "Agravamento de doenças respiratórias."
    else:
        qualidade = "Péssima"
        efeito = "Risco grave à saúde. Evitar exposição."

    print(f"Qualidade do ar: {qualidade}")
    print(f"Efeitos à saúde: {efeito}")

    dados_medida = {
        "data_hora": datetime.now(),
        "pm10": pm10,
        "pm25": pm25,
        "o3": o3,
        "co": co,
        "no2": no2,
        "so2": so2,
        "i_pm10": i_pm10,
        "i_pm25": i_pm25,
        "i_o3": i_o3,
        "i_co": i_co,
        "i_no2": i_no2,
        "i_so2": i_so2,
        "iqa_max": maior,
        "qualidade": qualidade,
        "efeito": efeito
    }
    salvar_medida(conexao, dados_medida)
    print(">> Medição salva no banco de dados.\n")

    if input("\nCalcular de novo? (s/n): ").lower() != "s":
        break

print("\n=== Resultado Final ===")
if resultados:
    final = max(resultados)
    print(f"Maior IQA obtido: {final:.1f}")
else:
    print("Nenhum valor válido inserido.")

conexao.close()