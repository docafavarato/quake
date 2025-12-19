# Processamento de Logs do Quake III Arena

## Descrição do desafio

Este projeto tem como objetivo processar um arquivo de log bruto do jogo **Quake III Arena**, extraindo informações estruturadas sobre cada partida e os jogadores participantes.

A partir do log, o sistema:
- Identifica corretamente cada partida (`InitGame`)
- Extrai estatísticas detalhadas dos jogadores
- Gera um **JSON estruturado** conforme especificado no desafio
- Converte os dados para o formato **Parquet**, utilizando **PyArrow**
- Garante fidelidade semântica ao funcionamento real do jogo
---

## Requisitos

- Python
- Biblioteca PyArrow

### Instalação das dependências

```bash
pip install pyarrow
```

---

## Como executar

1. Coloque o arquivo `Quake 1.log` no mesmo diretório do `main.py`
2. Execute o script:

```bash
python main.py
```

3. Os seguintes arquivos serão gerados:
   - `quake_games.json`
   - `quake_games.parquet`

---

## Decisões técnicas e raciocínio

### Separação correta das partidas

Cada partida no log começa com o evento:

```
InitGame:
```

A decisão foi separar as partidas exclusivamente com base nesse marcador, acumulando todas as linhas subsequentes até o próximo `InitGame`.

---

### Extração do mapa (`mapname`)

O nome do mapa é extraído apenas da linha `InitGame`, utilizando a chave `mapname`, independentemente da ordem dos parâmetros.

---

### Identificação de jogadores

- Os jogadores são identificados pelo **ID numérico**, conforme aparece nos eventos `ClientConnect`
- Caso um jogador apareça em um evento antes do `ClientConnect`, ele é criado sob demanda
- O nome atual do jogador é atualizado a partir de `ClientUserinfoChanged`

---

### Interpretação correta das mortes

As regras adotadas foram:

| Situação | Tratamento |
|--------|-----------|
| `killer == victim` | Suicídio |
| `killer == 1022` (`<world>`) | Morte pelo ambiente |
| `killer != victim` | Kill normal |

Decisões importantes:
- **World kills não contam como suicídio**
- World kills incrementam apenas `deaths`
- Apenas kills válidas incrementam `kills` e contam para `favorite_weapon`
  
---

### Arma favorita (`favorite_weapon`)

A arma favorita é definida como:
- A arma com maior número de kills feitas pelo jogador
- Apenas kills válidas entram no cálculo
- Em caso de empate, qualquer arma com maior frequência é aceita
- Se o jogador não matou ninguém, o campo é `null`

---

### Itens coletados

Itens são capturados a partir dos eventos `Item:` e armazenados na ordem em que aparecem no log. Optei por manter itens duplicados, pois funciona como um histórico de coleta.

---
