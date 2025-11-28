import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error

print("Sistema QA")
print("Digite os valores dos poluentes.")
print("Se digitar 0, o programa continua; se negativo, encerra.\n")

faixas = {
    "PM10": [(0, 50, 0, 40), (51, 100, 41, 80), (101, 150, 81, 120), (151, 250, 121, 200), (251, 600, 201, 300)],
    "PM25": [(0, 25, 0, 40), (26, 50, 41, 80), (51, 75, 81, 120), (76, 125, 121, 200), (126, 300, 201, 300)],
    "O3": [(0, 100, 0, 40), (101, 130, 41, 80), (131, 160, 81, 120), (161, 200, 121, 200), (201, 400, 201, 300)],
    "CO": [(0, 4, 0, 40), (5, 9, 41, 80), (10, 13, 81, 120), (14, 15, 121, 200), (16, 50, 201, 300)],
    "NO2": [(0, 200, 0, 40), (201, 240, 41, 80), (241, 320, 81, 120), (321, 1130, 121, 200), (1131, 4000, 201, 300)],
    "SO2": [(0, 20, 0, 40), (21, 40, 41, 80), (41, 365, 81, 120), (366, 800, 121, 200), (801, 1600, 201, 300)],
}

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "qualidade_ar"),
}


def conectar_banco():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        print(f"Erro ao conectar no MySQL: {exc}")
        raise


def criar_tabela(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
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
            """
        )
    conexao.commit()


def salvar_medida(conexao, dados):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO medidas_iqa
            (data_hora, pm10, pm25, o3, co, no2, so2,
             i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2,
             iqa_max, qualidade, efeito)
            VALUES (%s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s)
            """,
            (
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
                dados["efeito"],
            ),
        )
    conexao.commit()


def calcular_iqa(valor, tabela):
    for (cl, ch, il, ih) in tabela:
        if cl <= valor <= ch:
            return ((ih - il) / (ch - cl)) * (valor - cl) + il
    return 300


def ler_valor(rotulo):
    while True:
        try:
            return float(input(f"{rotulo}: "))
        except ValueError:
            print("Digite um numero valido.")


def main():
    try:
        conexao = conectar_banco()
    except Error:
        return

    criar_tabela(conexao)
    resultados = []

    try:
        while True:
            pm10 = ler_valor("PM10 (ug/m3)")
            pm25 = ler_valor("PM2.5 (ug/m3)")
            o3 = ler_valor("O3 (ug/m3)")
            co = ler_valor("CO (ppm)")
            no2 = ler_valor("NO2 (ug/m3)")
            so2 = ler_valor("SO2 (ug/m3)")

            if any(v < 0 for v in [pm10, pm25, o3, co, no2, so2]):
                print("\nValor negativo detectado. Encerrando...")
                break

            if any(v == 0 for v in [pm10, pm25, o3, co, no2, so2]):
                print("\nValor ZERO detectado. Continuando...\n")

            i_pm10 = calcular_iqa(pm10, faixas["PM10"])
            i_pm25 = calcular_iqa(pm25, faixas["PM25"])
            i_o3 = calcular_iqa(o3, faixas["O3"])
            i_co = calcular_iqa(co, faixas["CO"])
            i_no2 = calcular_iqa(no2, faixas["NO2"])
            i_so2 = calcular_iqa(so2, faixas["SO2"])

            indices = [i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2]
            maior = max(indices)
            resultados.extend(indices)

            print("\n--- INDICES OFICIAIS IQA ---")
            print(f"PM10: {i_pm10:.1f}")
            print(f"PM2.5: {i_pm25:.1f}")
            print(f"O3: {i_o3:.1f}")
            print(f"CO: {i_co:.1f}")
            print(f"NO2: {i_no2:.1f}")
            print(f"SO2: {i_so2:.1f}")
            print(f"\n>> IQA Atual (maior indice): {maior:.1f}")

            if maior <= 40:
                qualidade = "Boa"
                efeito = "Nenhum efeito a saude."
            elif maior <= 80:
                qualidade = "Moderada"
                efeito = "Pode causar leve desconforto em sensiveis."
            elif maior <= 120:
                qualidade = "Ruim"
                efeito = "Irritacao nos olhos e respiracao dificil."
            elif maior <= 200:
                qualidade = "Muito Ruim"
                efeito = "Agravamento de doencas respiratorias."
            else:
                qualidade = "Pessima"
                efeito = "Risco grave a saude. Evitar exposicao."

            print(f"Qualidade do ar: {qualidade}")
            print(f"Efeitos a saude: {efeito}")

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
                "efeito": efeito,
            }
            salvar_medida(conexao, dados_medida)
            print(">> Medicao salva no banco de dados.\n")

            if input("\nCalcular de novo? (s/n): ").lower() != "s":
                break

        print("\n=== Resultado Final ===")
        if resultados:
            final = max(resultados)
            print(f"Maior IQA obtido: {final:.1f}")
        else:
            print("Nenhum valor valido inserido.")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
