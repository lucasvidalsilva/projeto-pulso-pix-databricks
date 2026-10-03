from copy import deepcopy
from urllib.parse import parse_qs, urlsplit

import pytest

from pulso_pix.estatisticas_pix import (
    ContratoFonteInvalido,
    construir_url,
    validar_resposta,
)


@pytest.fixture
def registro_valido():
    return {
        "AnoMes": 202501,
        "PAG_PFPJ": "PF",
        "REC_PFPJ": "PF",
        "PAG_REGIAO": "SUL",
        "REC_REGIAO": "SUL",
        "PAG_IDADE": "mais de 60 anos",
        "REC_IDADE": "entre 30 e 39 anos",
        "FORMAINICIACAO": "QRES",
        "NATUREZA": "P2P",
        "FINALIDADE": "Pix",
        "VALOR": 12709601.53,
        "QUANTIDADE": 81721,
    }


def test_constroi_consulta_com_mes_exato_e_limite():
    url = construir_url(202501, limite=5)
    partes = urlsplit(url)
    consulta = parse_qs(partes.query)

    assert partes.path.endswith(
        "/Pix_DadosAbertos/versao/v1/odata/EstatisticasTransacoesPix(Database=@Database)"
    )
    assert consulta == {
        "$format": ["json"],
        "@Database": ["'202501'"],
        "$filter": ["AnoMes eq 202501"],
        "$top": ["5"],
    }
    assert "%24" not in url
    assert "%40" not in url
    assert "+" not in url


@pytest.mark.parametrize("ano_mes", [True, "202501", 202500, 202513, 199912])
def test_rejeita_ano_mes_invalido(ano_mes):
    with pytest.raises((TypeError, ValueError), match="ano_mes"):
        construir_url(ano_mes)


@pytest.mark.parametrize("limite", [True, 0, -1, 1.5])
def test_rejeita_limite_invalido(limite):
    with pytest.raises(ValueError, match="limite"):
        construir_url(202501, limite=limite)


def test_aceita_amostra_valida_e_dimensao_nula(registro_valido):
    outro_registro = deepcopy(registro_valido)
    outro_registro["REC_IDADE"] = None

    validar_resposta([registro_valido, outro_registro], 202501)


def test_rejeita_resposta_vazia():
    with pytest.raises(ContratoFonteInvalido, match="não retornou"):
        validar_resposta([], 202501)


def test_rejeita_mes_divergente(registro_valido):
    registro_valido["AnoMes"] = 202502

    with pytest.raises(ContratoFonteInvalido, match="esperado=202501"):
        validar_resposta([registro_valido], 202501)


def test_rejeita_campo_ausente(registro_valido):
    del registro_valido["NATUREZA"]

    with pytest.raises(ContratoFonteInvalido, match="NATUREZA"):
        validar_resposta([registro_valido], 202501)


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("VALOR", -0.01),
        ("VALOR", float("nan")),
        ("VALOR", float("inf")),
        ("QUANTIDADE", -1),
        ("QUANTIDADE", 1.5),
        ("VALOR", True),
    ],
)
def test_rejeita_medida_invalida(registro_valido, campo, valor):
    registro_valido[campo] = valor

    with pytest.raises(ContratoFonteInvalido, match=campo):
        validar_resposta([registro_valido], 202501)


def test_rejeita_grao_duplicado(registro_valido):
    with pytest.raises(ContratoFonteInvalido, match="duplica o grão"):
        validar_resposta([registro_valido, deepcopy(registro_valido)], 202501)
