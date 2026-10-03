"""Junta os arquivos de conteudo/fonte/*.json em conteudo/diario.js (lido pelo site).

Para editar o conteúdo: altere os .json em conteudo/fonte/ e rode
    python3 conteudo/montar.py
"""
import json
from pathlib import Path

PASTA = Path(__file__).parent
FONTE = PASTA / "fonte"


def carregar(nome):
    return json.loads((FONTE / nome).read_text(encoding="utf-8"))


areas = carregar("areas_a.json") + carregar("areas_b.json") + carregar("areas_c.json")
dados = {
    "devocional": carregar("devocional.json"),
    "estoico": carregar("estoico.json"),
    "areas": areas,
    "trilhas": carregar("trilhas.json"),
}

# Conferências mínimas para não publicar conteúdo quebrado.
CAMPOS = {
    "devocional": ["tema", "referencia", "livro_slug", "capitulo", "ideia_central", "reflexao", "oracao", "acao"],
    "estoico": ["autor", "obra", "frase", "aplicacao", "pratica"],
}
for chave, campos in CAMPOS.items():
    for i, item in enumerate(dados[chave]):
        faltam = [c for c in campos if not item.get(c)]
        assert not faltam, f"{chave}[{i}] sem {faltam}"
for a in areas:
    for i, l in enumerate(a["licoes"]):
        faltam = [c for c in ["titulo", "fonte", "ideia", "pratica", "pergunta"] if not l.get(c)]
        assert not faltam, f"{a['area_id']}[{i}] sem {faltam}"
for t in dados["trilhas"]:
    assert len(t["dias"]) == 21, f"trilha {t['id']} com {len(t['dias'])} dias"
    for i, d in enumerate(t["dias"]):
        faltam = [c for c in ["titulo", "acao", "por_que"] if not d.get(c)]
        assert not faltam, f"{t['id']}[{i}] sem {faltam}"

saida = PASTA / "diario.js"
saida.write_text(
    "// Gerado por conteudo/montar.py — edite os .json em conteudo/fonte/\n"
    "window.INSPIRE_CONTEUDO = " + json.dumps(dados, ensure_ascii=False, indent=1) + ";\n",
    encoding="utf-8",
)
print(f"{saida}: {len(dados['devocional'])} devocionais, {len(dados['estoico'])} estoicos, "
      f"{len(areas)} áreas ({sum(len(a['licoes']) for a in areas)} lições), {len(dados['trilhas'])} trilhas")
