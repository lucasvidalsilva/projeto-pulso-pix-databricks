import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, localcontext
from importlib.resources import files
from json import dumps
from pathlib import Path
from uuid import uuid4

from pulso_pix.estatisticas_pix import (
    ArtefatoBruto,
    ContratoFonteInvalido,
    baixar_resposta,
    extrair_registros,
    gravar_artefato_bruto,
    preparar_artefato_bruto,
    validar_identificador,
)

TABELA_ESTATISTICAS = "estatisticas_transacoes"
TABELA_USO_PIX = "uso_pix_mensal"
VISAO_ENTRADA = "estatisticas_pix_entrada"
VISAO_SILVER_MES = "estatisticas_pix_silver_mes"


@dataclass(frozen=True)
class ResultadoExecucao:
    ano_mes: int
    extracao_id: str
    caminho_resposta: str
    registros_publicados: int
    tabela_silver: str
    tabela_gold: str


def preparar_linhas_entrada(
    registros: list[dict[str, object]],
    artefato: ArtefatoBruto,
    caminho_resposta: str,
) -> list[dict[str, object]]:
    extraido_em_utc = artefato.extraido_em.astimezone(UTC).replace(tzinfo=None)
    linhas: list[dict[str, object]] = []

    for indice, registro in enumerate(registros):
        linha = dict(registro)
        linha["VALOR"] = _decimal_centavos(registro["VALOR"], indice)
        linha["QUANTIDADE"] = int(registro["QUANTIDADE"])
        linha["extracao_id"] = artefato.extracao_id
        linha["extraido_em"] = extraido_em_utc
        linha["caminho_resposta"] = caminho_resposta
        linha["sha256_resposta"] = artefato.sha256
        linhas.append(linha)

    return linhas


def publicar_silver(
    spark: object,
    registros: list[dict[str, object]],
    artefato: ArtefatoBruto,
    catalogo: str,
    schema_silver: str,
    caminho_resposta: str,
) -> str:
    validar_identificador(catalogo, "catalogo")
    validar_identificador(schema_silver, "schema_silver")
    tabela = f"{catalogo}.{schema_silver}.{TABELA_ESTATISTICAS}"
    linhas = preparar_linhas_entrada(registros, artefato, caminho_resposta)

    spark.conf.set("spark.sql.session.timeZone", "UTC")
    quadro_entrada = spark.createDataFrame(linhas, schema=_schema_entrada())
    quadro_entrada.createOrReplaceTempView(VISAO_ENTRADA)
    quadro_silver = spark.sql(_carregar_sql_transformacao())
    quadro_silver.createOrReplaceTempView(VISAO_SILVER_MES)
    (
        quadro_silver.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"ano_mes = {artefato.ano_mes}")
        .saveAsTable(tabela)
    )
    return tabela


def publicar_gold(
    spark: object,
    artefato: ArtefatoBruto,
    catalogo: str,
    schema_gold: str,
) -> str:
    validar_identificador(catalogo, "catalogo")
    validar_identificador(schema_gold, "schema_gold")
    tabela = f"{catalogo}.{schema_gold}.{TABELA_USO_PIX}"
    quadro_gold = spark.sql(_carregar_sql_gold())
    (
        quadro_gold.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"ano_mes = {artefato.ano_mes}")
        .saveAsTable(tabela)
    )
    return tabela


def executar(
    ano_mes: int,
    catalogo: str,
    schema_bronze: str,
    schema_silver: str,
    schema_gold: str,
    volume: str,
    spark: object | None = None,
) -> ResultadoExecucao:
    validar_identificador(catalogo, "catalogo")
    validar_identificador(schema_bronze, "schema_bronze")
    validar_identificador(schema_silver, "schema_silver")
    validar_identificador(schema_gold, "schema_gold")
    validar_identificador(volume, "volume")

    conteudo = baixar_resposta(ano_mes)
    artefato = preparar_artefato_bruto(
        conteudo=conteudo,
        ano_mes=ano_mes,
        extracao_id=str(uuid4()),
        extraido_em=datetime.now(UTC),
    )
    raiz_volume = Path("/Volumes", catalogo, schema_bronze, volume)
    caminho_resposta, _ = gravar_artefato_bruto(artefato, raiz_volume)
    registros = extrair_registros(conteudo, ano_mes)
    sessao_spark = spark if spark is not None else _obter_spark()
    tabela_silver = publicar_silver(
        spark=sessao_spark,
        registros=registros,
        artefato=artefato,
        catalogo=catalogo,
        schema_silver=schema_silver,
        caminho_resposta=caminho_resposta.as_posix(),
    )
    tabela_gold = publicar_gold(
        spark=sessao_spark,
        artefato=artefato,
        catalogo=catalogo,
        schema_gold=schema_gold,
    )
    return ResultadoExecucao(
        ano_mes=ano_mes,
        extracao_id=artefato.extracao_id,
        caminho_resposta=caminho_resposta.as_posix(),
        registros_publicados=len(registros),
        tabela_silver=tabela_silver,
        tabela_gold=tabela_gold,
    )


def main() -> None:
    argumentos = _criar_analisador().parse_args()
    resultado = executar(
        ano_mes=argumentos.ano_mes,
        catalogo=argumentos.catalogo,
        schema_bronze=argumentos.schema_bronze,
        schema_silver=argumentos.schema_silver,
        schema_gold=argumentos.schema_gold,
        volume=argumentos.volume,
    )
    print(dumps(resultado.__dict__, ensure_ascii=False, sort_keys=True))


def _criar_analisador() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(description="Processa estatísticas mensais do Pix")
    analisador.add_argument("--ano-mes", required=True, type=int)
    analisador.add_argument("--catalogo", required=True)
    analisador.add_argument("--schema-bronze", required=True)
    analisador.add_argument("--schema-silver", required=True)
    analisador.add_argument("--schema-gold", required=True)
    analisador.add_argument("--volume", required=True)
    return analisador


def _decimal_centavos(valor: object, indice: int) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 40
        try:
            decimal = Decimal(str(valor))
            quantizado = decimal.quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError) as erro:
            raise ContratoFonteInvalido(
                f"registro {indice}: VALOR não cabe em decimal(38,2)"
            ) from erro

    if decimal != quantizado or quantizado.adjusted() + 1 > 36:
        raise ContratoFonteInvalido(f"registro {indice}: VALOR não cabe em decimal(38,2)")
    return quantizado


def _carregar_sql_transformacao() -> str:
    return files("pulso_pix").joinpath("sql", "estatisticas_transacoes.sql").read_text("utf-8")


def _carregar_sql_gold() -> str:
    return files("pulso_pix").joinpath("sql", "uso_pix_mensal.sql").read_text("utf-8")


def _schema_entrada() -> object:
    from pyspark.sql.types import (
        DecimalType,
        IntegerType,
        LongType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )

    return StructType(
        [
            StructField("AnoMes", IntegerType(), False),
            StructField("PAG_PFPJ", StringType(), True),
            StructField("REC_PFPJ", StringType(), True),
            StructField("PAG_REGIAO", StringType(), True),
            StructField("REC_REGIAO", StringType(), True),
            StructField("PAG_IDADE", StringType(), True),
            StructField("REC_IDADE", StringType(), True),
            StructField("FORMAINICIACAO", StringType(), True),
            StructField("NATUREZA", StringType(), True),
            StructField("FINALIDADE", StringType(), True),
            StructField("VALOR", DecimalType(38, 2), False),
            StructField("QUANTIDADE", LongType(), False),
            StructField("extracao_id", StringType(), False),
            StructField("extraido_em", TimestampType(), False),
            StructField("caminho_resposta", StringType(), False),
            StructField("sha256_resposta", StringType(), False),
        ]
    )


def _obter_spark() -> object:
    from pyspark.sql import SparkSession

    return SparkSession.builder.getOrCreate()
