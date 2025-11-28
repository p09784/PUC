import os
import sys
import getpass
from datetime import datetime
from typing import Optional

try:
    import mysql.connector  # type: ignore
    MYSQL_AVAILABLE = True
except Exception:
    MYSQL_AVAILABLE = False

resultados = []

faixas = {
    "PM10":  [(0, 50, 0, 40), (51, 100, 41, 80), (101, 150, 81, 120), (151, 250, 121, 200), (251, 600, 201, 300)],
    "PM25":  [(0, 25, 0, 40), (26, 50, 41, 80), (51, 75, 81, 120), (76, 125, 121, 200), (126, 300, 201, 300)],
    "O3":    [(0, 100, 0, 40), (101, 130, 41, 80), (131, 160, 81, 120), (161, 200, 121, 200), (201, 400, 201, 300)],
    "CO":    [(0, 4, 0, 40), (5, 9, 41, 80), (10, 13, 81, 120), (14, 15, 121, 200), (16, 50, 201, 300)],
    "NO2":   [(0, 200, 0, 40), (201, 240, 41, 80), (241, 320, 81, 120), (321, 1130, 121, 200), (1131, 4000, 201, 300)],
    "SO2":   [(0, 20, 0, 40), (21, 40, 41, 80), (41, 365, 81, 120), (366, 800, 121, 200), (801, 1600, 201, 300)]
}


def conectar_banco() -> Optional["mysql.connector.connection.MySQLConnection"]:
    """Tenta conectar ao MySQL. Retorna conexão ou `None` se não disponível."""
    if not MYSQL_AVAILABLE:
        print("Aviso: pacote 'mysql-connector-python' não disponível — sem persistência no banco.")
        return None

    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME", "qualidade_ar")

    if password is None:
        try:
            password = getpass.getpass(f"MySQL password for user '{user}': ")
        except Exception:
            password = None

    try:
        conexao = mysql.connector.connect(host=host, user=user, password=password)
    except Exception as err:
        print("Erro ao conectar ao MySQL:", err)
        return None

    try:
        cursor = conexao.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        conexao.database = database

        create_table = """
        CREATE TABLE IF NOT EXISTS medidas_iqa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_hora DATETIME,
            pm10 FLOAT, pm25 FLOAT, o3 FLOAT, co FLOAT, no2 FLOAT, so2 FLOAT,
            i_pm10 FLOAT, i_pm25 FLOAT, i_o3 FLOAT, i_co FLOAT, i_no2 FLOAT, i_so2 FLOAT,
            iqa_max FLOAT,
            qualidade VARCHAR(50),
            efeito VARCHAR(255)
        )
        """
        cursor.execute(create_table)
        cursor.close()
    except Exception as err:
        print("Erro ao preparar o banco de dados:", err)
        try:
            conexao.close()
        except Exception:
            pass
        return None

    return conexao


def salvar_medida(conexao: Optional["mysql.connector.connection.MySQLConnection"], dados: dict) -> None:
    """Salva a medida no banco se a conexão estiver disponível; caso contrário, ignora."""
    if conexao is None:
        return

    cursor = conexao.cursor()
    sql = (
        "INSERT INTO medidas_iqa "
        "(data_hora, pm10, pm25, o3, co, no2, so2, "
        "i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2, "
        "iqa_max, qualidade, efeito) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
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
        dados["efeito"],
    )
    cursor.execute(sql, valores)
    conexao.commit()
    cursor.close()


def calcular_iqa(valor: float, tabela: list) -> float:
    for (cl, ch, il, ih) in tabela:
        if cl <= valor <= ch:
            return ((ih - il) / (ch - cl)) * (valor - cl) + il
    return 300.0


def get_float(prompt: str) -> float:
    """Lê um valor float do usuário, repetindo até receber um número válido."""
    while True:
        try:
            raw = input(prompt)
        except EOFError:
            raise
        raw = raw.strip()
        try:
            return float(raw)
        except ValueError:
            print("Entrada inválida. Digite um número (ex: 12.3). Tente novamente.")


def imprimir_resultados(i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2):
    print("\n--- ÍNDICES OFICIAIS IQA ---")
    print(f"PM10: {i_pm10:.1f}")
    print(f"PM2.5: {i_pm25:.1f}")
    print(f"O3: {i_o3:.1f}")
    print(f"CO: {i_co:.1f}")
    print(f"NO2: {i_no2:.1f}")
    print(f"SO2: {i_so2:.1f}")


def avaliar_qualidade(maior: float):
    if maior <= 40:
        return "Boa", "Nenhum efeito à saúde."
    if maior <= 80:
        return "Moderada", "Pode causar leve desconforto em sensíveis."
    if maior <= 120:
        return "Ruim", "Irritação nos olhos e respiração difícil."
    if maior <= 200:
        return "Muito Ruim", "Agravamento de doenças respiratórias."
    return "Péssima", "Risco grave à saúde. Evitar exposição."


def main() -> None:
    print("Sistema QA")
    print("Digite os valores dos poluentes.")
    print("Se digitar 0, o programa continua; se negativo, encerra.\n")

    conexao = conectar_banco()

    while True:
        try:
            pm10 = get_float("PM10 (µg/m3): ")
            pm25 = get_float("PM2.5 (µg/m3): ")
            o3 = get_float("O3 (µg/m3): ")
            co = get_float("CO (ppm): ")
            no2 = get_float("NO2 (µg/m3): ")
            so2 = get_float("SO2 (µg/m3): ")
        except EOFError:
            print("\nEntrada encerrada. Saindo...")
            break

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

        imprimir_resultados(i_pm10, i_pm25, i_o3, i_co, i_no2, i_so2)
        print(f"\n>> IQA Atual (maior índice): {maior:.1f}")

        qualidade, efeito = avaliar_qualidade(maior)
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
            "efeito": efeito,
        }

        salvar_medida(conexao, dados_medida)
        if conexao is not None:
            print(">> Medição salva no banco de dados.\n")
        else:
            print(">> Medição não persistida (sem conexão ao DB).\n")

        try:
            again = input("\nCalcular de novo? (s/n): ").lower()
        except EOFError:
            break
        if again != "s":
            break

    print("\n=== Resultado Final ===")
    if resultados:
        final = max(resultados)
        print(f"Maior IQA obtido: {final:.1f}")
    else:
        print("Nenhum valor válido inserido.")

    if conexao is not None:
        try:
            conexao.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()