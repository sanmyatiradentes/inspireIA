# Guia de escrita — conteúdo diário da InspireIA

A InspireIA (inspireia.com.br) é uma "mentora comportamental de bolso" gratuita criada por Sanmya Tiradentes (cristã; diretora da Polícia Científica do Amazonas; Lean Six Sigma Master Black Belt; especialista em neurociência). O conteúdo diário é lido por pessoas que voltam todo dia — por isso NADA pode repetir ideia, passagem ou frase já usada (veja os arquivos `_existentes_*.txt` nesta pasta) nem repetir dentro do seu próprio lote.

## Tom
Português do Brasil com acentuação correta. Um par sábio, acolhedor e direto — nunca acadêmico arrogante, nunca coach motivacional vazio. Linguagem simples, analogias do cotidiano (casa, trabalho, trânsito, cozinha, escola, serviço público), zero jargão (se usar termo técnico, explique em palavras simples). Textos em parágrafo corrido, sem listas. Varie as aberturas: não comece vários textos do mesmo jeito ("Pense na última vez…", "Quantas vezes…").

## Tamanho (NÃO aumentar — manter igual ao conteúdo atual)
Siga exatamente as faixas de palavras de cada formato abaixo.

## Direitos autorais (obrigatório)
- Bíblia: NTLH, NVI, ARA, NAA etc. têm direitos. Use só a REFERÊNCIA; escreva a ideia com SUAS palavras, sem imitar a redação de nenhuma tradução, sem aspas.
- Estoicos (Sêneca, Marco Aurélio, Epicteto, Musônio Rufo — originais em domínio público): tradução/paráfrase PRÓPRIA e curta; nunca copie traduções publicadas.
- Livros modernos: explique a ideia com suas palavras e atribua ("Autor — Obra"). Sem citações longas.

## Precisão
Só use referências/atribuições de que tem CERTEZA. Na dúvida, escolha outra. Nada de mitos científicos nem provérbios apócrifos. Achados controversos são apresentados com honestidade.

## Formatos (JSON — um array, validar com python3 json.load)

Devocional:
{"tema": "3-6 palavras", "referencia": "Provérbios 15:1", "livro_slug": "pv", "capitulo": 15, "ideia_central": "paráfrase própria em 1 frase", "reflexao": "120-170 palavras ligando o texto à vida real de hoje", "oracao": "oração curta em 1ª pessoa, 35-60 palavras", "acao": "ação concreta para hoje, 1-2 frases"}
`livro_slug`/`capitulo` formam o link https://www.bibliaonline.com.br/ntlh/{livro_slug}/{capitulo}. Confirme TODOS com curl: `curl -s -L https://www.bibliaonline.com.br/ntlh/pv/15 | grep -o '<title>[^<]*'` deve mostrar o livro e capítulo certos ("Provérbios 15 | NTLH"). Atenção: "jo" = João; Jó, Jonas etc. têm slugs próprios — descubra testando.

Estoico:
{"autor": "Sêneca", "obra": "Cartas a Lucílio, 1", "frase": "tradução/paráfrase própria, até 30 palavras", "aplicacao": "60-100 palavras: como usar hoje no trabalho, família ou liderança", "pratica": "exercício estoico concreto para hoje, 1-2 frases"}

Lição de área:
{"titulo": "3-7 palavras", "fonte": "Autor — Obra", "ideia": "70-110 palavras com exemplo concreto do dia a dia", "pratica": "ação pequena para hoje, 1-2 frases", "pergunta": "pergunta de reflexão pessoal, 1 frase"}

Trilha:
{"id": "kebab-case", "nome": "...", "subtitulo": "frase curta do que a pessoa conquista", "para_quem": "1 frase", "fontes": "autores", "dias": [21 × {"titulo": "2-6 palavras", "acao": "o que fazer hoje, 2-3 frases concretas", "por_que": "1 frase com o mecanismo (ciência ou sabedoria)"}]}
Dias 1-7 consciência, 8-14 prática, 15-21 consolidação/identidade; dia 21 = fechamento (revisar a jornada, ensinar alguém).

## Entrega
Grave só o arquivo pedido. Valide (json.load, contagem, campos não vazios, faixas de palavras, nenhuma duplicata com `_existentes_*.txt` nem dentro do lote). Resposta final: caminho, contagem e (para devocional) a lista de slugs/capítulos verificados.
