# Pipeline Modular de Padronização e Consolidação

## Estrutura
- `input/`: arquivos de entrada: Telefonia.csv, WhatsApp.csv, ChatVideo.xlsx, Teleconsultas.xlsx, Aux_tempos.xlsx, Aux_evolucao.xlsx
- `config/`: Padronizacao.xlsx
- `output/`: Base_Consolidada.xlsx será gerada aqui
- `logs/`: logs de execução
- `src/`: módulos Python

## Instalação
```bash
cd "CAMINHO_DO_PROJETO"
python -m pip install -r requirements.txt
```

## Execução
1. Ajuste os caminhos em `src/config.py` se necessário.
2. Coloque os arquivos nas pastas `input` e `config`.
3. Execute:
```bash
python main.py
```

## Observações
- O arquivo final é salvo com escrita segura via openpyxl, evitando corrupção por fórmulas, caracteres XML inválidos e limite de tamanho de célula.
- Empresa, Grupo de Clientes e Nível são carregados do `Padronizacao.xlsx`.
