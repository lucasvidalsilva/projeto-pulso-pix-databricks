import json
import re
from pathlib import Path

CAMINHO_DASHBOARD = Path(__file__).parents[2] / "src" / "dashboards" / "uso_pix.lvdash.json"


def carregar_dashboard():
    return json.loads(CAMINHO_DASHBOARD.read_text(encoding="utf-8"))


def test_dashboard_usa_tabela_portavel_e_querylines_separadas():
    dashboard = carregar_dashboard()
    dataset = dashboard["datasets"][0]

    assert dataset["name"] == "ds_uso_pix"
    assert all(linha.endswith((" ", "\n")) for linha in dataset["queryLines"])
    consulta = "".join(dataset["queryLines"])
    assert "FROM uso_pix_mensal" in consulta
    assert "workspace.gold" not in consulta


def test_dashboard_tem_grid_completo_e_nomes_validos():
    dashboard = carregar_dashboard()

    for pagina in dashboard["pages"]:
        assert pagina["layoutVersion"] == "GRID_V1"
        for item in pagina["layout"]:
            nome = item["widget"]["name"]
            assert re.fullmatch(r"[A-Za-z0-9_-]{1,60}", nome)
            posicao = item["position"]
            assert 0 <= posicao["x"] < 12
            assert posicao["x"] + posicao["width"] <= 12


def test_campos_dos_widgets_correspondem_as_consultas():
    dashboard = carregar_dashboard()

    for pagina in dashboard["pages"]:
        for item in pagina["layout"]:
            widget = item["widget"]
            for consulta in widget.get("queries", []):
                nomes = {campo["name"] for campo in consulta["query"].get("fields", [])}
                especificacao = widget["spec"]
                campos = _campos_referenciados(especificacao.get("encodings", {}))
                campos_da_consulta = {
                    campo["fieldName"]
                    for campo in campos
                    if campo.get("queryName") in (None, consulta["name"])
                }
                assert campos_da_consulta <= nomes


def _campos_referenciados(valor):
    if isinstance(valor, dict):
        campos = [valor] if "fieldName" in valor else []
        for item in valor.values():
            campos.extend(_campos_referenciados(item))
        return campos
    if isinstance(valor, list):
        return [campo for item in valor for campo in _campos_referenciados(item)]
    return []
