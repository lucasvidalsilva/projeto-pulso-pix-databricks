from copy import deepcopy
from json import dumps
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from pulso_pix.estatisticas_pix import (
    ContratoFonteInvalido,
    FontePixIndisponivel,
    baixar_resposta,
    construir_url,
    extrair_registros,
    validar_resposta,
)


class RespostaFalsa:
    def __init__(self, conteudo):
        self.conteudo = conteudo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.conteudo


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


def test_baixa_resposta_mensal(monkeypatch):
    chamadas = []

    def abrir(requisicao, timeout):
        chamadas.append((requisicao, timeout))
        return RespostaFalsa(b'{"value": []}')

    monkeypatch.setattr("pulso_pix.estatisticas_pix.urlopen", abrir)

    assert baixar_resposta(202501, limite=1) == b'{"value": []}'
    assert chamadas[0][1] == 60
    assert "$filter=AnoMes%20eq%20202501" in chamadas[0][0].full_url
    assert chamadas[0][0].headers["Accept"] == "application/json"


def test_repete_falha_transitoria_com_espera_exponencial(monkeypatch):
    resultados = iter(
        [
            HTTPError("url", 500, "erro", {}, None),
            URLError("temporário"),
            RespostaFalsa(b"ok"),
        ]
    )
    esperas = []

    def abrir(*_args, **_kwargs):
        resultado = next(resultados)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado

    monkeypatch.setattr("pulso_pix.estatisticas_pix.urlopen", abrir)
    monkeypatch.setattr("pulso_pix.estatisticas_pix.sleep", esperas.append)

    assert baixar_resposta(202501, espera_segundos=0.5) == b"ok"
    assert esperas == [0.5, 1.0]


def test_nao_repete_erro_http_nao_transitorio(monkeypatch):
    def abrir(*_args, **_kwargs):
        raise HTTPError("url", 400, "erro", {}, None)

    monkeypatch.setattr("pulso_pix.estatisticas_pix.urlopen", abrir)

    with pytest.raises(HTTPError) as erro:
        baixar_resposta(202501)

    assert erro.value.code == 400


def test_informa_indisponibilidade_apos_esgotar_tentativas(monkeypatch):
    monkeypatch.setattr(
        "pulso_pix.estatisticas_pix.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("temporário")),
    )
    monkeypatch.setattr("pulso_pix.estatisticas_pix.sleep", lambda _segundos: None)

    with pytest.raises(FontePixIndisponivel, match="3 tentativas"):
        baixar_resposta(202501)


def test_extrai_e_valida_registros(registro_valido):
    conteudo = dumps({"@odata.context": "origem", "value": [registro_valido]}).encode()

    assert extrair_registros(conteudo, 202501) == [registro_valido]


@pytest.mark.parametrize(
    "conteudo",
    [b"nao e json", b"[]", b'{"value": {}}', b'{"value": [1]}'],
)
def test_rejeita_envelope_invalido(conteudo):
    with pytest.raises(ContratoFonteInvalido):
        extrair_registros(conteudo, 202501)


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
