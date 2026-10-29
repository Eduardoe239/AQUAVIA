# AQUAVIA — Guia de Marca (v1.0, proposta)

> Proposta de identidade gerada a partir da direção do Documento Mestre (§2). **Não substitui** pesquisa de anterioridade (INPI), de domínio e revisão jurídica, exigidas antes de uso comercial e registro.

## 1. Conceito
**AQUA + VIA** — a água e o caminho. O nome já contém a ideia do produto: água que flui e um caminho por onde ela é medida, compreendida e gerida.

- **Símbolo:** uma gota cortada por um **canal de fluxo** (a "via"). Em cima, a água ainda por ser entendida (ciano); embaixo, a água medida e estruturada (navy). Sobre o canal, uma **conta** — o **ponto de medição**, o sensor. Um único gesto reúne gota (hídrico), caminho/fluxo (circulação) e ponto (medição e conexão), como pede o documento.
- **Wordmark:** traço monolinear arredondado, geométrico, sem serifa, mesmo "peso" do canal do símbolo. O **pingo do I** em ciano repete o ponto de medição: o sistema inteiro se assina com a mesma ideia.
- **Personalidade:** confiável, clara, técnica sem complicação, responsável com a água. Sem brilhos, gradientes ou clichês de "onda + folha".

## 2. Slogan
**Principal (oficial de trabalho):** *Uma união para um gasto eficiente.*
Lê-se de duas formas: a união **AQUA + VIA** (o nome) e a união entre **pessoas, dados e técnica** (o produto). Mantém "gasto eficiente" — sem prometer percentual de economia.

**Assinatura curta (espaços pequenos, app, embalagem):** *Meça. Entenda. Aja.* — descreve o que o produto faz, sem promessa de resultado.

**Regras (Documento Mestre §2):** não usar o slogan ou a marca com promessa de economia garantida, detecção infalível de vazamento, precisão certificada ou cobertura universal. O slogan segue "de trabalho": testar com clientes (Home e Agro) e passar por revisão linguística/comercial antes do registro.

## 3. Cores (tokens do Documento de Desenvolvimento §10)
| Papel | Cor |
|---|---|
| Navy — estrutura, confiança | `#12385A` |
| Azul — ação e dados | `#178DD1` |
| Ciano — destaque hídrico, ponto de medição | `#55C5E8` |
| Gelo — fundo | `#F4F7FA` |
Verde, âmbar e vermelho são **só estados de sistema** (sucesso, atenção, falha) — nunca cor de marca.

## 4. Arquivos (`brand/logo/`)
| Arquivo | Uso |
|---|---|
| `aquavia-logo-horizontal.svg` | principal, fundo claro |
| `aquavia-logo-horizontal-dark.svg` | fundo navy/escuro |
| `aquavia-logo-stacked(-dark).svg` | formatos quadrados, capas, QR/etiqueta |
| `aquavia-symbol(-dark).svg` | avatar, app, selo |
| `*-mono-navy.svg`, `*-mono-white.svg` | gravação, carimbo, uma cor, fundos coloridos |
| `favicon.svg` + `png/favicon-*.png` | favicon, ícone de app |
| `png/*` | pré-visualizações e uso rápido |

Todas as peças são **SVG puro em curvas** (sem fonte embutida, sem máscaras): o wordmark é desenho, não texto. `build_brand.py` regenera tudo; `board.py` gera a prancha.

## 5. Uso
- **Área de respeito:** altura do "I" (≈ metade da altura do símbolo) em todos os lados.
- **Tamanhos mínimos:** símbolo 16 px (digital) / 6 mm (impresso e gravação); logo horizontal 96 px de largura / 25 mm. Abaixo disso, use só o símbolo.
- **Fundos:** versão colorida em claros; `-dark` em navy; mono sobre fotos, cores de acento e gravação a laser/estampa (o canal e o ponto funcionam como recorte).
- **Não fazer:** esticar ou girar; trocar as cores; aplicar sombra, brilho ou gradiente; reescrever o wordmark em outra fonte; separar o pingo do I; colocar sobre fundos de baixo contraste; usar verde/âmbar/vermelho na marca.

## 6. Pendências antes do uso comercial
1. Pesquisa de anterioridade de marca e símbolo (INPI) e de domínio/redes; validar nomes de módulos (Console, Care, Connect).
2. Teste de reconhecimento e preferência com moradores, produtores e técnicos (Documento de Desenvolvimento §10, Pesquisa UX).
3. Teste em gravação/estampa no hardware (a marca prevê traços ≥ 0,4 mm em escala 25 mm; validar com o fornecedor da caixa).
4. Revisão linguística/comercial do slogan.
