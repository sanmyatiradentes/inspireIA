"""Gera um PDF (livro A5) com todo o conteúdo diário da InspireIA.

Lê conteudo/diario.js (gerado por montar.py) e grava, por padrão,
~/Downloads/InspireIA_Conteudo_Completo.pdf

    python3 conteudo/gerar_pdf.py [caminho_de_saida.pdf]
"""
import json
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "InspireIA_Conteudo_Completo.pdf"

VINHO, ROSA, ROSA_CLARO, TINTA, CINZA, CREME = (HexColor(c) for c in
                                                ("#632240", "#C2185B", "#E694B0", "#1d1418", "#7a6a70", "#FCEFF3"))

FONTES = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Georgia", FONTES + "Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-B", FONTES + "Georgia Bold.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-I", FONTES + "Georgia Italic.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-BI", FONTES + "Georgia Bold Italic.ttf"))
pdfmetrics.registerFontFamily("Georgia", normal="Georgia", bold="Georgia-B", italic="Georgia-I", boldItalic="Georgia-BI")

src = (RAIZ / "conteudo" / "diario.js").read_text(encoding="utf-8")
C = json.loads(src[src.index("=") + 1:].rstrip().rstrip(";"))


def E(s):
    return escape(str(s))


def estilo(nome, **kw):
    base = dict(fontName="Georgia", fontSize=9.6, leading=14.2, textColor=TINTA)
    base.update(kw)
    return ParagraphStyle(nome, **base)


S = {
    "corpo": estilo("corpo", spaceAfter=6, alignment=4),
    "rotulo": estilo("rotulo", fontName="Georgia-B", fontSize=7, leading=9, textColor=ROSA, spaceAfter=2),
    "dia": estilo("dia", fontName="Georgia-B", fontSize=7.5, leading=10, textColor=ROSA, spaceBefore=4),
    "tit": estilo("tit", fontName="Georgia-B", fontSize=15, leading=19, textColor=VINHO, spaceAfter=3),
    "tit2": estilo("tit2", fontName="Georgia-B", fontSize=12.5, leading=16, textColor=VINHO, spaceAfter=2),
    "ref": estilo("ref", fontName="Georgia-B", fontSize=9, leading=12, textColor=VINHO, spaceAfter=6),
    "fonte": estilo("fonte", fontName="Georgia-I", fontSize=8.4, leading=11, textColor=CINZA, spaceAfter=7),
    "ideia": estilo("ideia", fontName="Georgia-I", fontSize=11, leading=15.5, textColor=VINHO,
                    leftIndent=9, borderPadding=(0, 0, 0, 7), spaceAfter=8),
    "frase": estilo("frase", fontName="Georgia-I", fontSize=12.2, leading=17, textColor=VINHO, spaceAfter=4),
    "caixa": estilo("caixa", fontSize=9.2, leading=13.4),
    "caixa_i": estilo("caixa_i", fontName="Georgia-I", fontSize=9.2, leading=13.4),
    "pergunta": estilo("pergunta", fontName="Georgia-B", fontSize=9.4, leading=13.5, textColor=VINHO, spaceBefore=2),
    "parte_num": estilo("parte_num", fontName="Georgia-B", fontSize=10, leading=14, textColor=ROSA_CLARO, alignment=TA_CENTER),
    "parte": estilo("parte", fontName="Georgia-B", fontSize=26, leading=32, textColor="#FFFFFF", alignment=TA_CENTER),
    "parte_sub": estilo("parte_sub", fontName="Georgia-I", fontSize=11, leading=16, textColor="#F6DCE6", alignment=TA_CENTER),
    "h1": estilo("h1", fontName="Georgia-B", fontSize=18, leading=23, textColor=VINHO, spaceAfter=8),
    "toc1": estilo("toc1", fontName="Georgia-B", fontSize=10.5, leading=17, textColor=VINHO),
    "toc2": estilo("toc2", fontSize=9.2, leading=13.5, leftIndent=12, textColor=TINTA),
}


class Marcador(Flowable):
    """Ponto invisível que vira marcador lateral do PDF (e item do sumário, se nivel_toc)."""

    def __init__(self, titulo, nivel, nivel_toc=None):
        super().__init__()
        self.titulo, self.nivel, self.nivel_toc = titulo, nivel, nivel_toc
        self.chave = f"m{id(self)}"

    def wrap(self, *a):
        return 0, 0

    def draw(self):
        c = self.canv
        c.bookmarkPage(self.chave)
        c.addOutlineEntry(self.titulo, self.chave, level=self.nivel, closed=self.nivel < 1)


def caixa(rotulo, texto, italico=False):
    t = Table([[Paragraph(E(rotulo).upper(), S["rotulo"])],
               [Paragraph(E(texto), S["caixa_i" if italico else "caixa"])]],
              colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREME),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
        ("TOPPADDING", (0, 1), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
    ]))
    t.spaceAfter = 6
    return t


def divisor():
    t = Table([[""]], colWidths=["100%"], rowHeights=[1])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.5, ROSA_CLARO)]))
    t.spaceBefore, t.spaceAfter = 8, 8
    return t


class Doc(BaseDocTemplate):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.secao = self.sub = ""
        m = dict(leftMargin=16 * mm, rightMargin=16 * mm, topMargin=17 * mm, bottomMargin=16 * mm)
        w, h = A5
        corpo = Frame(m["leftMargin"], m["bottomMargin"], w - 32 * mm, h - 33 * mm, id="corpo",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        cheia = Frame(0, 0, w, h, id="cheia", leftPadding=18 * mm, rightPadding=18 * mm,
                      topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate("capa", [cheia], onPage=self.fundo_capa),
            PageTemplate("parte", [cheia], onPage=self.fundo_parte),
            PageTemplate("normal", [corpo], onPageEnd=self.moldura),
        ])

    def handle_documentBegin(self):
        self.secao = self.sub = ""
        super().handle_documentBegin()

    def afterFlowable(self, f):
        if isinstance(f, Marcador):
            if f.nivel == 0:
                self.secao, self.sub = f.titulo, ""
            elif f.nivel_toc is not None:
                self.sub = f.titulo
            if f.nivel_toc is not None:
                self.notify("TOCEntry", (f.nivel_toc, f.titulo, self.page, f.chave))

    def fundo_capa(self, c, d):
        w, h = A5
        c.setFillColor(VINHO); c.rect(0, 0, w, h, stroke=0, fill=1)
        c.setFillColor(HexColor("#4A1830")); c.rect(0, 0, w, 52 * mm, stroke=0, fill=1)

    def fundo_parte(self, c, d):
        w, h = A5
        c.setFillColor(VINHO); c.rect(0, 0, w, h, stroke=0, fill=1)

    def moldura(self, c, d):
        w, h = A5
        c.saveState()
        c.setFont("Georgia", 7); c.setFillColor(CINZA)
        c.drawString(16 * mm, h - 10 * mm, "InspireIA")
        c.drawRightString(w - 16 * mm, h - 10 * mm, self.sub or self.secao)
        c.setStrokeColor(ROSA_CLARO); c.setLineWidth(0.4)
        c.line(16 * mm, h - 11.8 * mm, w - 16 * mm, h - 11.8 * mm)
        c.drawCentredString(w / 2, 9 * mm, str(d.page))
        c.restoreState()


def pagina_de_parte(numero, titulo, sub, story):
    story += [NextPageTemplate("parte"), PageBreak(), Marcador(titulo, 0, 0), Spacer(1, 62 * mm),
              Paragraph(f"PARTE {numero}", S["parte_num"]), Spacer(1, 4 * mm),
              Paragraph(E(titulo), S["parte"]), Spacer(1, 5 * mm), Paragraph(E(sub), S["parte_sub"]),
              NextPageTemplate("normal"), PageBreak()]


story = []
# Capa
logo = RAIZ / "img" / "icone-512.png"
story += [NextPageTemplate("capa"), Spacer(1, 40 * mm), Image(str(logo), 30 * mm, 30 * mm), Spacer(1, 8 * mm),
          Paragraph("Inspire<font color='#E694B0'>IA</font>", estilo("capa_t", fontName="Georgia-B", fontSize=34,
                    leading=40, textColor="#FFFFFF", alignment=TA_CENTER)),
          Spacer(1, 4 * mm),
          Paragraph("Um ano de devocionais, sabedoria estoica,<br/>aprendizados e trilhas de 21 dias",
                    estilo("capa_s", fontName="Georgia-I", fontSize=12.5, leading=18, textColor="#F6DCE6", alignment=TA_CENTER)),
          Spacer(1, 50 * mm),
          Paragraph("Sanmya Tiradentes", estilo("capa_a", fontName="Georgia-B", fontSize=11, leading=15,
                    textColor="#FFFFFF", alignment=TA_CENTER)),
          Paragraph(f"inspireia.com.br · {['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'][date.today().month-1]} de {date.today().year}",
                    estilo("capa_d", fontSize=9, leading=13, textColor="#F6DCE6", alignment=TA_CENTER)),
          NextPageTemplate("normal"), PageBreak()]

# Apresentação
n_lic = sum(len(a["licoes"]) for a in C["areas"])
story += [Marcador("Apresentação", 0), Paragraph("Apresentação", S["h1"])]
for p in [
    "Pessoas movem pessoas. Este livro reúne todo o conteúdo diário da InspireIA, a mentora comportamental "
    "de bolso que une neurociência, psicologia, liderança e sabedoria milenar para ajudar você a ser a melhor "
    "versão de si mesmo no trabalho, em casa e nas relações.",
    f"São {len(C['devocional'])} devocionais e {len(C['estoico'])} lições de sabedoria estoica, um para cada dia do ano, "
    f"{n_lic} aprendizados distribuídos em {len(C['areas'])} áreas da vida e {len(C['trilhas'])} trilhas de 21 dias, "
    "com uma microação por dia. No site, cada dia mostra um item de cada parte; aqui você encontra tudo reunido, "
    "para ler no seu ritmo, voltar ao que mais tocou você ou usar em reuniões, grupos e conversas em família.",
    "Os devocionais trazem a referência bíblica e uma reflexão escrita com palavras próprias. Para ler o texto "
    "completo, use a Nova Tradução na Linguagem de Hoje (NTLH), da Sociedade Bíblica do Brasil: as referências são "
    "clicáveis e abrem a passagem em bibliaonline.com.br/ntlh. As frases estoicas são traduções livres dos originais "
    "de Sêneca, Marco Aurélio, Epicteto e Musônio Rufo, e as lições de cada área explicam, com palavras próprias, "
    "ideias de autores e pesquisas indicados na fonte de cada uma.",
    "Este conteúdo oferece orientação geral e não substitui psicólogo, psiquiatra ou médico. Se você estiver "
    "passando por sofrimento intenso, ligue 188 (CVV, 24 horas, gratuito).",
]:
    story.append(Paragraph(E(p), S["corpo"]))
story += [Spacer(1, 6), Paragraph("Com propósito e com amor,<br/><b>Sanmya Tiradentes</b>", S["corpo"]), PageBreak()]

# Sumário
toc = TableOfContents(levelStyles=[S["toc1"], S["toc2"]], dotsMinLevel=0)
story += [Marcador("Sumário", 0), Paragraph("Sumário", S["h1"]), toc]

# Parte 1 — Devocional
pagina_de_parte(1, "Devocional", "Uma passagem bíblica, uma reflexão, uma oração e uma ação para cada dia do ano", story)
for i, d in enumerate(C["devocional"], 1):
    url = f"https://www.bibliaonline.com.br/ntlh/{d['livro_slug']}/{d['capitulo']}"
    bloco = [Marcador(f"Dia {i} — {d['tema']}", 1), Paragraph(f"DIA {i}", S["dia"]),
             Paragraph(E(d["tema"]), S["tit"]),
             Paragraph(f"<a href='{url}' color='#632240'>{E(d['referencia'])}</a> "
                       f"<font color='#C2185B' size='7.5'>· ler na NTLH</font>", S["ref"]),
             Paragraph(E(d["ideia_central"]), S["ideia"])]
    story += [CondPageBreak(70 * mm), KeepTogether(bloco), Paragraph(E(d["reflexao"]), S["corpo"]),
              KeepTogether([caixa("Oração", d["oracao"], italico=True)]),
              KeepTogether([caixa("Ação de hoje", d["acao"])]), divisor()]

# Parte 2 — Estoicos
pagina_de_parte(2, "Sabedoria Estoica", "Sêneca, Marco Aurélio, Epicteto e Musônio Rufo aplicados à vida de hoje", story)
for i, e in enumerate(C["estoico"], 1):
    story += [CondPageBreak(45 * mm), KeepTogether([
        Marcador(f"Dia {i} — {e['autor']}", 1), Paragraph(f"DIA {i}", S["dia"]),
        Paragraph(E(e["frase"]), S["frase"]),
        Paragraph(f"{E(e['autor'])} — {E(e['obra'])}", S["fonte"])]),
        Paragraph(E(e["aplicacao"]), S["corpo"]),
        KeepTogether([caixa("Exercício", e["pratica"])]), divisor()]

# Parte 3 — Áreas
pagina_de_parte(3, "Aprendizados por Área", f"{len(C['areas'])} áreas da vida, {n_lic} lições práticas", story)
for a in C["areas"]:
    story += [PageBreak(), Marcador(a["area_nome"], 1, 1), Paragraph(E(a["area_nome"]), S["h1"])]
    for j, l in enumerate(a["licoes"], 1):
        story += [CondPageBreak(42 * mm), KeepTogether([
            Paragraph(f"LIÇÃO {j}", S["dia"]), Paragraph(E(l["titulo"]), S["tit2"]),
            Paragraph(E(l["fonte"]), S["fonte"])]), Paragraph(E(l["ideia"]), S["corpo"]),
            KeepTogether([caixa("Pratique hoje", l["pratica"]), Paragraph(E(l["pergunta"]), S["pergunta"])]), divisor()]

# Parte 4 — Trilhas
pagina_de_parte(4, "Trilhas de 21 Dias", "Uma microação por dia: consciência, prática e consolidação", story)
for t in C["trilhas"]:
    story += [PageBreak(), Marcador(t["nome"], 1, 1), Paragraph(E(t["nome"]), S["h1"]),
              Paragraph(E(t["subtitulo"]), estilo("sub", fontName="Georgia-B", fontSize=10.5, leading=14.5, textColor=ROSA, spaceAfter=4)),
              Paragraph(E(t["para_quem"]), S["corpo"]), Paragraph("Fontes: " + E(t["fontes"]), S["fonte"]), divisor()]
    for k, dia in enumerate(t["dias"], 1):
        story += [KeepTogether([
            Paragraph(f"DIA {k}", S["dia"]), Paragraph(E(dia["titulo"]), S["tit2"]),
            Paragraph(E(dia["acao"]), S["corpo"]),
            Paragraph(f"<b>Por quê:</b> {E(dia['por_que'])}", estilo("pq", fontSize=8.8, leading=12.5, textColor=CINZA, spaceAfter=4))])]

doc = Doc(str(SAIDA), pagesize=A5, title="InspireIA — Conteúdo completo", author="Sanmya Tiradentes",
          subject="Devocionais, sabedoria estoica, aprendizados por área e trilhas de 21 dias")
doc.multiBuild(story)
print(f"{SAIDA} ({SAIDA.stat().st_size // 1024} KB)")
