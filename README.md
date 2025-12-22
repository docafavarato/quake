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

O nome do mapa é extraído apenas da linha `InitGame`, utilizando a chave `mapname`.

---

### Identificação de jogadores

- Os jogadores são identificados pelo **ID numérico**, conforme aparece nos eventos `ClientConnect`
- O nome atual do jogador é atualizado a partir de `ClientUserinfoChanged`, guardando o nome antigo em uma variável.

---

### Interpretação das mortes

As regras adotadas foram:

| Situação | Tratamento |
|--------|-----------|
| `killer == victim` | Suicídio |
| `killer == <world>`) | Morte pelo ambiente |
| `killer != victim` | Kill normal |

Decisões importantes:
- World kills não contam como suicídio
- World kills incrementam apenas `deaths`, ou seja, não são contabilizadas em `total_kills`
  
---

### Arma favorita

A arma favorita é definida com o auxílio de uma variável temporária `used_weapons`, que armazena todas as armas utilizadas em kills de um jogador. Depois, a arma com maior frequência na lista é selecionada como a `favorite_weapon`

---

### Itens coletados

Itens são capturados a partir dos eventos `Item:` e armazenados na ordem em que aparecem no log. Optei por não manter itens duplicados.

---

### Parquet

Utilizei as bibliotecas `pandas` e `pyarrow` para gerar o arquivo parquet, e o esquema foi modelado conforme a seguinte estrutura:
```text
root
 |-- game: int32
 |-- map: string
 |-- total_kills: int32
 |-- players: list<struct>
 |    |-- id: int32
 |    |-- current_name: string
 |    |-- old_names: list<string>
 |    |-- kills: int32
 |    |-- deaths: int32
 |    |-- suicides: int32
 |    |-- favorite_weapon: string
 |    |-- collected_items: list<string>
