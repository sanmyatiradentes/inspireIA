"""Junta os arquivos de conteudo/fonte/ em conteudo/diario.js (lido pelo site).

Base:   fonte/devocional.json, estoico.json, areas_a/b/c.json, trilhas.json
Extras: fonte/extra/devocional_*.json, estoico_*.json, areas_novas_*.json, trilhas_novas.json

Os lotes são intercalados (dias seguidos vêm de livros/autores diferentes) e
itens repetidos são retirados automaticamente — o relatório diz o que saiu.

Para editar o conteúdo: altere os .json e rode
    python3 conteudo/montar.py
"""
import json
import re
import unicodedata
from pathlib import Path

PASTA = Path(__file__).parent
FONTE = PASTA / "fonte"
EXTRA = FONTE / "extra"
relatorio = []


def carregar(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def chave(texto):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def intercalar(listas):
    """Uma de cada lista por vez: A1, B1, C1, A2, B2..."""
    saida, i = [], 0
    while any(i < len(l) for l in listas):
        for l in listas:
            if i < len(l):
                saida.append(l[i])
        i += 1
    return saida


def sem_repetidos(itens, fn_chave, nome):
    vistos, saida = set(), []
    for it in itens:
        k = fn_chave(it)
        if k in vistos:
            relatorio.append(f"{nome}: retirado repetido -> {k[:80]}")
            continue
        vistos.add(k)
        saida.append(it)
    return saida


def completos(itens, campos, nome):
    saida = []
    for it in itens:
        faltam = [c for c in campos if not it.get(c)]
        if faltam:
            relatorio.append(f"{nome}: retirado item incompleto (sem {faltam}) -> {str(it)[:80]}")
            continue
        saida.append(it)
    return saida


def lotes(padrao):
    return [carregar(p) for p in sorted(EXTRA.glob(padrao))]


# Devocional: a base primeiro, depois os lotes intercalados por livro.
CAMPOS_DEV = ["tema", "referencia", "livro_slug", "capitulo", "ideia_central", "reflexao", "oracao", "acao"]
devocional = carregar(FONTE / "devocional.json") + intercalar(lotes("devocional_*.json"))
devocional = completos(devocional, CAMPOS_DEV, "devocional")
devocional = sem_repetidos(devocional, lambda d: chave(d["referencia"]), "devocional")

CAMPOS_EST = ["autor", "obra", "frase", "aplicacao", "pratica"]
estoico = carregar(FONTE / "estoico.json") + intercalar(lotes("estoico_*.json"))
estoico = completos(estoico, CAMPOS_EST, "estoico")
estoico = sem_repetidos(estoico, lambda e: chave(e["frase"]), "estoico")

# Áreas: lições novas entram depois das atuais, na mesma área.
CAMPOS_LIC = ["titulo", "fonte", "ideia", "pratica", "pergunta"]
areas = carregar(FONTE / "areas_a.json") + carregar(FONTE / "areas_b.json") + carregar(FONTE / "areas_c.json")
novas = {}
for lote in lotes("areas_novas_*.json"):
    for a in lote:
        novas.setdefault(a["area_id"], []).extend(a["licoes"])
for a in areas:
    licoes = a["licoes"] + novas.pop(a["area_id"], [])
    licoes = completos(licoes, CAMPOS_LIC, a["area_id"])
    a["licoes"] = sem_repetidos(licoes, lambda l: chave(l["titulo"]), a["area_id"])
for sobra in novas:
    relatorio.append(f"áreas: lote com area_id desconhecido '{sobra}' ignorado")

trilhas = carregar(FONTE / "trilhas.json")
if (EXTRA / "trilhas_novas.json").exists():
    trilhas += carregar(EXTRA / "trilhas_novas.json")
validas = []
for t in sem_repetidos(trilhas, lambda t: t["id"], "trilhas"):
    dias = [d for d in t.get("dias", []) if all(d.get(c) for c in ["titulo", "acao", "por_que"])]
    if len(dias) != 21:
        relatorio.append(f"trilhas: '{t.get('id')}' retirada ({len(dias)} dias completos em vez de 21)")
        continue
    validas.append(t)
trilhas = validas

dados = {"devocional": devocional, "estoico": estoico, "areas": areas, "trilhas": trilhas}
saida = PASTA / "diario.js"
saida.write_text(
    "// Gerado por conteudo/montar.py — edite os .json em conteudo/fonte/\n"
    "window.INSPIRE_CONTEUDO = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print(f"{saida.name}: {len(devocional)} devocionais, {len(estoico)} estoicos, "
      f"{len(trilhas)} trilhas, {saida.stat().st_size // 1024} KB")
for a in areas:
    print(f"  {a['area_nome']}: {len(a['licoes'])} lições")
for linha in relatorio:
    print("  ·", linha)
