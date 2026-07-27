from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
LOG_DIR = PROJECT_ROOT / "logs"

FILES = {
    "telefonia": "Telefonia.csv",
    "whatsapp": "WhatsApp.csv",
    "chatvideo": "ChatVideo.xlsx",
    "teleconsultas": "Teleconsulta.xlsx",
    "aux_tempos": "Aux_Tempos.xlsx",
    "aux_evolucao": "Aux_Evolucao.xlsx",
    "padronizacao": "Padronizacao.xlsx",
}

OUTPUT_FILE = OUTPUT_DIR / "Base_Consolidada.xlsx"
FINAL_COLUMNS = [
    "Data", "ID", "Status", "Empresa", "Grupo de Clientes",
    "Tempo de Atendimento", "Tempo de Espera", "Nível", "Centro de Custo",
    "Canal de Atendimento", "Nota de Serviço", "LinkedID (Telefonia)",
    "Status Final (Telefonia)", "Tipo de Atendimento (Teleconsulta/N2)",
    "Especialidade (Teleconsulta)", "Razão da Chamada (Chat/Video)",
    "Desfecho (Teleconsulta/N2)", "Origem"
]
