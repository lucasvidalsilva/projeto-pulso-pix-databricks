from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from json import JSONDecodeError, loads
from math import isfinite
from numbers import Integral, Real
from re import fullmatch
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from uuid import UUID

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
SCHEMA_BRONZE = "bronze"
VOLUME_RESPOSTAS_PIX = "respostas_pix"


@dataclass(frozen=True)
class ArtefatoBruto:
    conteudo: bytes = field(repr=False)
    ano_mes: int
    extracao_id: str
    extraido_em: datetime
    url_origem: str
    sha256: str
    tamanho_bytes: int
    caminho_relativo: str

    def caminho_volume(self, catalogo: str) -> str:
        if fullmatch(r"[a-z][a-z0-9_]*", catalogo) is None:
            raise ValueError("catalogo deve ser um identificador snake_case")
        return f"/Volumes/{catalogo}/{SCHEMA_BRONZE}/{VOLUME_RESPOSTAS_PIX}/{self.caminho_relativo}"


class ContratoFonteInvalido(ValueError):
    pass


class FontePixIndisponivel(RuntimeError):
    pass


def preparar_artefato_bruto(
    conteudo: bytes,
    ano_mes: int,
    extracao_id: str,
    extraido_em: datetime,
) -> ArtefatoBruto:
    _validar_ano_mes(ano_mes)
    if not isinstance(conteudo, bytes):
        raise TypeError("conteudo deve ser bytes")

    try:
        extracao_id_normalizado = str(UUID(extracao_id))
    except (AttributeError, TypeError, ValueError) as erro:
        raise ValueError("extracao_id deve ser um UUID válido") from erro

    if not isinstance(extraido_em, datetime):
        raise TypeError("extraido_em deve ser uma data e hora")
    if extraido_em.tzinfo is None or extraido_em.utcoffset() is None:
        raise ValueError("extraido_em deve incluir fuso horário")
    extraido_em_utc = extraido_em.astimezone(UTC)
    caminho_relativo = (
        f"estatisticas_transacoes/ano_mes={ano_mes}/"
        f"extracao_id={extracao_id_normalizado}/resposta.json"
    )

    return ArtefatoBruto(
        conteudo=conteudo,
        ano_mes=ano_mes,
        extracao_id=extracao_id_normalizado,
        extraido_em=extraido_em_utc,
        url_origem=construir_url(ano_mes),
        sha256=sha256(conteudo).hexdigest(),
        tamanho_bytes=len(conteudo),
        caminho_relativo=caminho_relativo,
    )


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


def baixar_resposta(
    ano_mes: int,
    limite: int | None = None,
    tentativas: int = 3,
    timeout_segundos: float = 60,
    espera_segundos: float = 1,
) -> bytes:
    if isinstance(tentativas, bool) or not isinstance(tentativas, int):
        raise TypeError("tentativas deve ser um inteiro positivo")
    if tentativas <= 0:
        raise ValueError("tentativas deve ser um inteiro positivo")
    if timeout_segundos <= 0:
        raise ValueError("timeout_segundos deve ser positivo")
    if espera_segundos < 0:
        raise ValueError("espera_segundos não pode ser negativo")

    requisicao = Request(
        construir_url(ano_mes, limite),
        headers={"Accept": "application/json", "User-Agent": "pulso-pix/0.1"},
    )
    erro_final: HTTPError | URLError | TimeoutError | None = None

    for tentativa in range(1, tentativas + 1):
        try:
            with urlopen(requisicao, timeout=timeout_segundos) as resposta:
                return resposta.read()
        except HTTPError as erro:
            if erro.code != 429 and not 500 <= erro.code < 600:
                raise
            erro_final = erro
        except (URLError, TimeoutError) as erro:
            erro_final = erro

        if tentativa < tentativas:
            sleep(espera_segundos * 2 ** (tentativa - 1))

    raise FontePixIndisponivel(
        f"fonte Pix indisponível após {tentativas} tentativas para {ano_mes}"
    ) from erro_final


def extrair_registros(
    conteudo: bytes | bytearray | str, ano_mes_esperado: int
) -> list[dict[str, object]]:
    try:
        documento = loads(conteudo)
    except (JSONDecodeError, UnicodeDecodeError, TypeError) as erro:
        raise ContratoFonteInvalido("resposta não contém JSON válido") from erro

    if not isinstance(documento, Mapping) or not isinstance(documento.get("value"), list):
        raise ContratoFonteInvalido("resposta não contém a lista value")

    registros: list[dict[str, object]] = []
    for indice, registro in enumerate(documento["value"]):
        if not isinstance(registro, Mapping):
            raise ContratoFonteInvalido(f"item {indice} de value não é um registro")
        registros.append(dict(registro))

    validar_resposta(registros, ano_mes_esperado)
    return registros


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
