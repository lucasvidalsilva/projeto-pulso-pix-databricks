from collections.abc import Mapping, Sequence
from math import isfinite
from numbers import Integral, Real
from urllib.parse import quote, urlencode

URL_ESTATISTICAS_PIX = (
    "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
    "EstatisticasTransacoesPix(Database=@Database)"
)

CAMPOS_DIMENSAO = (
    "PAG_PFPJ",
    "REC_PFPJ",
    "PAG_REGIAO",
    "REC_REGIAO",
    "PAG_IDADE",
    "REC_IDADE",
    "FORMAINICIACAO",
    "NATUREZA",
    "FINALIDADE",
)
CAMPOS_MEDIDA = ("VALOR", "QUANTIDADE")
CAMPOS_OBRIGATORIOS = ("AnoMes", *CAMPOS_DIMENSAO, *CAMPOS_MEDIDA)


class ContratoFonteInvalido(ValueError):
    pass


def construir_url(ano_mes: int, limite: int | None = None) -> str:
    _validar_ano_mes(ano_mes)
    if limite is not None and (
        isinstance(limite, bool) or not isinstance(limite, int) or limite <= 0
    ):
        raise ValueError("limite deve ser um inteiro positivo")

    parametros: dict[str, str | int] = {
        "$format": "json",
        "@Database": f"'{ano_mes}'",
        "$filter": f"AnoMes eq {ano_mes}",
    }
    if limite is not None:
        parametros["$top"] = limite
    consulta = urlencode(parametros, safe="$@'", quote_via=quote)
    return f"{URL_ESTATISTICAS_PIX}?{consulta}"


def validar_resposta(registros: Sequence[Mapping[str, object]], ano_mes_esperado: int) -> None:
    _validar_ano_mes(ano_mes_esperado)
    if not registros:
        raise ContratoFonteInvalido("a fonte não retornou registros")

    graos: set[tuple[object, ...]] = set()
    for indice, registro in enumerate(registros):
        ausentes = set(CAMPOS_OBRIGATORIOS).difference(registro)
        if ausentes:
            campos = ", ".join(sorted(ausentes))
            raise ContratoFonteInvalido(f"registro {indice} sem campos obrigatórios: {campos}")

        if registro["AnoMes"] != ano_mes_esperado:
            raise ContratoFonteInvalido(
                f"registro {indice} tem AnoMes={registro['AnoMes']!r}; esperado={ano_mes_esperado}"
            )

        for campo in CAMPOS_DIMENSAO:
            valor = registro[campo]
            if valor is not None and not isinstance(valor, str):
                raise ContratoFonteInvalido(f"registro {indice}: {campo} deve ser texto ou nulo")

        _validar_medida(registro["VALOR"], "VALOR", indice)
        _validar_quantidade(registro["QUANTIDADE"], indice)

        grao = tuple(registro[campo] for campo in ("AnoMes", *CAMPOS_DIMENSAO))
        if grao in graos:
            raise ContratoFonteInvalido(f"registro {indice} duplica o grão da fonte")
        graos.add(grao)


def _validar_ano_mes(ano_mes: int) -> None:
    if isinstance(ano_mes, bool) or not isinstance(ano_mes, int):
        raise TypeError("ano_mes deve ser um inteiro no formato AAAAMM")
    ano, mes = divmod(ano_mes, 100)
    if ano < 2000 or not 1 <= mes <= 12:
        raise ValueError("ano_mes deve ser um mês válido no formato AAAAMM")


def _validar_medida(valor: object, campo: str, indice: int) -> None:
    if isinstance(valor, bool) or not isinstance(valor, Real) or not isfinite(valor) or valor < 0:
        raise ContratoFonteInvalido(f"registro {indice}: {campo} deve ser numérico e não negativo")


def _validar_quantidade(valor: object, indice: int) -> None:
    _validar_medida(valor, "QUANTIDADE", indice)
    if not isinstance(valor, Integral) and not float(valor).is_integer():
        raise ContratoFonteInvalido(f"registro {indice}: QUANTIDADE deve representar um inteiro")
