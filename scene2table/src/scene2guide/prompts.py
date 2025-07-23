_sys_prompt = """
Você é um programador e animador especialista em Unity, seu foco é documentar arquivos.

Crie um arquivo markdown que documente o arquivo o json do contexto enviado e respeite sempre as regras de cada um deles.

### SAÍDA
Estrutura JSON + Markdown detalhado

## FOCO
Completude e precisão estrutural
""".strip("\n ")

_prompt_generate_timeline_report = """
# Considere o input abaixo como uma cena de animação do Unity, que contém várias tracks e clipes de animação.

```input
{input}
```

# Extraia a timeline da animação e produza um relatório de markdown simples, organizado por números de track, da seguinte forma:

- Agrupe as animações por número e tipo de track (por exemplo, ## Track 1 (Audio Track), ## Track 2 (Animator Timeline Track), etc.)
- Para cada clipe nessa track, imprima uma única linha neste formato:

  **Clip Name** (start → end) (Game Object)

- Mantenha os tempos em segundos com 2 casas decimais (ex.: 0,00s → 32,60s)
- Use o nome real do Game Object entre parênteses. Se for um clipe de áudio, use (AudioPlayableAsset)
- Mantenha a ordem original das tracks e clipes conforme aparecem na timeline
- Não inclua nenhum tipo de script, trigger ou detalhes técnicos adicionais

**EXEMPLO**

## Track 1 (Audio Track)
**ROP_Animation_Addition_EN** (0.00s → 32.60s) (AudioPlayableAsset)

## Track 2 (Animator Timeline Track)
**Groups Show** (0.00s → 0.98s) (Currency Groups)
**Init** (0.00s → 1.00s) (Currency Setup)
**Pennys Grow and Shrink** (9.40s → 9.97s) ($.01 Profit Pile)

## Track 3 (Arrow Timeline Track)
**Equation Arrow Shows** (18.17s → 18.42s) (Equation Arrow)
**Equation Arrow Disappears** (31.97s → 32.07s) (Equation Arrow)
""".strip("\n ")

_prompt_generate_table = """
# Considere o input abaixo como um relatório de timeline.

```input
{input}
```

1. **Identifique os Tracks**: Procure por seções `## Track X`
2. **Extraia os clipes de cada track**: Para cada linha de clip, capture:
   - **Nome**: Texto entre `**` (ex: `**Groups Show**`)
   - **Timing**: Dados entre parênteses `(0.0s → 0.98s)`
   - **Descrição**: Texto final entre parênteses `(Currency Groups)`
3. **Para cada clipe, extraia**:
   - **Nome do Clipe**: Texto entre `**`
   - **Início**: Tempo antes do `→` (ex: `0.0s`)
   - **Fim**: Tempo após o `→` (ex: `0.98s`)

4. Gere uma tabela markdown com esta estrutura exata abaixo:
```markdown
# Tabela de Tracks e Clips - [Nome da Animação]

| Track | Clip | Nome do Clip | Início (s) | Fim (s) | Duração (s) |
|-------|------|--------------|------------|---------|-------------|
| **Track 1: Audio Track** | 1 | Nome_do_Clip | X.XX | Y.YY | Z.ZZ |
| | 2 | Nome_do_Clip | X.XX | Y.YY | Z.ZZ |
| **Track 2: Animator Timeline Track (1)** | 1 | Nome_do_Clip | X.XX | Y.YY | Z.ZZ |

## Resumo dos Tracks
- **Track 1 (Audio)**: X clips, duração total de Y.Ys
- **Track 2 (Animator 1)**: X clips, duração total de Y.Ys
- **Track 3 (Animator 2)**: X clips, duração total de Y.Ys
```
""".strip("\n ")