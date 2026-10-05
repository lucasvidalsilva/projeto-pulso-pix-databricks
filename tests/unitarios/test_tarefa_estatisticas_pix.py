from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from sqlite3 import connect

import pytest

from pulso_pix.estatisticas_pix import ContratoFonteInvalido, preparar_artefato_bruto
from pulso_pix.tarefa_estatisticas_pix import (
    _carregar_sql_gold,
    preparar_linhas_entrada,
    publicar_gold,
    publicar_silver,
)


@pytest.fixture
def registro_valido():
    return {
        "AnoMes": 202501,
        "PAG_PFPJ": "PF",
        "REC_PFPJ": "PJ",
        "PAG_REGIAO": "SUL",
        "REC_REGIAO": "SUDESTE",
        "PAG_IDADE": "entre 30 e 39 anos",
        "REC_IDADE": None,
        "FORMAINICIACAO": "QRES",
        "NATUREZA": "P2B",
        "FINALIDADE": "Pix",
        "VALOR": 12709601.53,
        "QUANTIDADE": 81721,
    }


@pytest.fixture
def artefato():
    return preparar_artefato_bruto(
        b'{"value": []}',
        202501,
        "31b10af6-a8ab-4162-976c-29de93436840",
        datetime(2026, 10, 3, 14, 30, tzinfo=UTC),
    )


def test_prepara_linha_tipificada_com_rastreabilidade(registro_valido, artefato):
    caminho = "/Volumes/workspace/bronze/respostas_pix/resposta.json"

    linhas = preparar_linhas_entrada([registro_valido], artefato, caminho)

    assert linhas == [
        {
            **registro_valido,
            "VALOR": Decimal("12709601.53"),
            "QUANTIDADE": 81721,
            "extracao_id": artefato.extracao_id,
            "extraido_em": datetime(2026, 10, 3, 14, 30, tzinfo=UTC).replace(tzinfo=None),
            "caminho_resposta": caminho,
            "sha256_resposta": artefato.sha256,
        }
    ]


def test_rejeita_valor_que_perderia_centavos(registro_valido, artefato):
    registro_valido["VALOR"] = 1.001

    with pytest.raises(ContratoFonteInvalido, match=r"decimal\(38,2\)"):
        preparar_linhas_entrada([registro_valido], artefato, "/Volumes/resposta.json")


class ConfiguracaoSparkFalsa:
    def __init__(self):
        self.valores = {}

    def set(self, chave, valor):
        self.valores[chave] = valor


class EscritaFalsa:
    def __init__(self):
        self.formato = None
        self.modo = None
        self.opcoes = {}
        self.tabela = None

    def format(self, formato):
        self.formato = formato
        return self

    def mode(self, modo):
        self.modo = modo
        return self

    def option(self, chave, valor):
        self.opcoes[chave] = valor
        return self

    def saveAsTable(self, tabela):
        self.tabela = tabela


class QuadroEntradaFalso:
    def __init__(self):
        self.visao = None

    def createOrReplaceTempView(self, visao):
        self.visao = visao


class QuadroSaidaFalso:
    def __init__(self):
        self.write = EscritaFalsa()
        self.visao = None

    def createOrReplaceTempView(self, visao):
        self.visao = visao


class SparkFalso:
    def __init__(self):
        self.conf = ConfiguracaoSparkFalsa()
        self.entrada = QuadroEntradaFalso()
        self.saida = QuadroSaidaFalso()
        self.linhas = None
        self.schema = None
        self.consulta = None

    def createDataFrame(self, linhas, schema):
        self.linhas = linhas
        self.schema = schema
        return self.entrada

    def sql(self, consulta):
        self.consulta = consulta
        return self.saida


def test_publica_apenas_mes_escolhido_com_sql_versionado(monkeypatch, registro_valido, artefato):
    spark = SparkFalso()
    schema = object()
    monkeypatch.setattr("pulso_pix.tarefa_estatisticas_pix._schema_entrada", lambda: schema)

    tabela = publicar_silver(
        spark=spark,
        registros=[registro_valido],
        artefato=artefato,
        catalogo="workspace",
        schema_silver="silver",
        caminho_resposta="/Volumes/workspace/bronze/respostas_pix/resposta.json",
    )

    assert tabela == "workspace.silver.estatisticas_transacoes"
    assert spark.conf.valores == {"spark.sql.session.timeZone": "UTC"}
    assert spark.entrada.visao == "estatisticas_pix_entrada"
    assert spark.saida.visao == "estatisticas_pix_silver_mes"
    assert "PAG_PFPJ AS pagador_pf_pj" in spark.consulta
    assert spark.saida.write.formato == "delta"
    assert spark.saida.write.modo == "overwrite"
    assert spark.saida.write.opcoes == {"replaceWhere": "ano_mes = 202501"}
    assert spark.saida.write.tabela == tabela


def test_agrega_gold_no_grao_escolhido():
    conexao = connect(":memory:")
    conexao.execute(
        """
        CREATE TABLE estatisticas_pix_silver_mes (
          ano_mes INTEGER,
          natureza TEXT,
          forma_iniciacao TEXT,
          regiao_pagador TEXT,
          regiao_recebedor TEXT,
          valor NUMERIC,
          quantidade INTEGER
        )
        """
    )
    conexao.executemany(
        "INSERT INTO estatisticas_pix_silver_mes VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (202501, "P2P", "MANU", "SUL", "SUDESTE", 10.5, 2),
            (202501, "P2P", "MANU", "SUL", "SUDESTE", 20.0, 3),
            (202501, "P2P", "MANU", "SUL", "SUL", 5.0, 1),
        ],
    )

    resultado = conexao.execute(_carregar_sql_gold()).fetchall()

    assert sorted(resultado) == [
        (202501, "P2P", "MANU", "SUL", "SUDESTE", 30.5, 5),
        (202501, "P2P", "MANU", "SUL", "SUL", 5, 1),
    ]


def test_publica_gold_apenas_para_mes_escolhido(artefato):
    spark = SparkFalso()

    tabela = publicar_gold(
        spark=spark,
        artefato=artefato,
        catalogo="workspace",
        schema_gold="gold",
    )

    assert tabela == "workspace.gold.uso_pix_mensal"
    assert "SUM(valor) AS valor_total" in spark.consulta
    assert spark.saida.write.formato == "delta"
    assert spark.saida.write.modo == "overwrite"
    assert spark.saida.write.opcoes == {"replaceWhere": "ano_mes = 202501"}
    assert spark.saida.write.tabela == tabela


def test_preserva_resposta_antes_de_validar(monkeypatch):
    eventos = []

    monkeypatch.setattr(
        "pulso_pix.tarefa_estatisticas_pix.baixar_resposta",
        lambda _ano_mes: b"nao e json",
    )

    def gravar(artefato, raiz_volume):
        eventos.append((artefato.conteudo, raiz_volume.as_posix()))
        return Path("/Volumes/resposta.json"), Path("/Volumes/metadados.json")

    monkeypatch.setattr("pulso_pix.tarefa_estatisticas_pix.gravar_artefato_bruto", gravar)

    from pulso_pix.tarefa_estatisticas_pix import executar

    with pytest.raises(ContratoFonteInvalido):
        executar(202501, "workspace", "bronze", "silver", "gold", "respostas_pix")

    assert eventos == [(b"nao e json", "/Volumes/workspace/bronze/respostas_pix")]
