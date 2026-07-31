import pandas as pd
from .config import INPUT_DIR, CONFIG_DIR, OUTPUT_FILE, FILES, FINAL_COLUMNS
from .io_utils import read_csv_semicolon, read_excel_default, save_excel_safe, read_csv_comma
from .utils import formatar_tempo, formatar_data_coluna, sanitizar_valor_excel
from .mappings import (
    build_status_map,
    load_clientes,
    build_empresa_grupo_map,
    load_niveis,
    build_nivel_telefonia,
    build_nivel_whatsapp,
    build_nivel_chatvideo,
    build_nivel_teleconsulta,
    load_status,
)
from .processors import processar_telefonia, processar_whatsapp, processar_chatvideo, processar_teleconsultas

def ensure_final_columns(df):
    for c in FINAL_COLUMNS:
        if c not in df.columns:
            df[c]=""
    return df[FINAL_COLUMNS]

def run_pipeline():
    pad = CONFIG_DIR / FILES["padronizacao"]
    clientes = load_clientes(pad)
    niveis = load_niveis(pad)
    status = load_status(pad)
    emp_tel, grp_tel = build_empresa_grupo_map(clientes, "Telefonia", "Agrupador - Fila")
    emp_wpp, grp_wpp = build_empresa_grupo_map(clientes, "WhatsApp", "Detalhe - Rede Social")
    emp_chat, grp_chat = build_empresa_grupo_map(clientes, "ChatVideo", "Empresa")
    emp_tele, grp_tele = build_empresa_grupo_map(clientes, "Teleconsulta", "Empresa")
    status_map = build_status_map(status)
    nivel_tel = build_nivel_telefonia(niveis)
    nivel_wpp = build_nivel_whatsapp(niveis)
    nivel_chat = build_nivel_chatvideo(niveis)
    nivel_tele_esp, nivel_tele_todos = build_nivel_teleconsulta(niveis)
    print(f"[Mapas] Empresa Tel/Wpp/Chat/Tele: {len(emp_tel)}/{len(emp_wpp)}/{len(emp_chat)}/{len(emp_tele)}")
    print(
        f"[Mapas] Nível Tel/Wpp/Chat/TeleEsp/TeleTodos: "
        f"{len(nivel_tel)}/{len(nivel_wpp)}/{len(nivel_chat)}/{len(nivel_tele_esp)}/{len(nivel_tele_todos)}"
    )
    tel=read_csv_comma(INPUT_DIR / FILES["telefonia"])
    wpp=read_csv_semicolon(INPUT_DIR / FILES["whatsapp"])
    chat=read_excel_default(INPUT_DIR / FILES["chatvideo"])
    tele=read_excel_default(INPUT_DIR / FILES["teleconsultas"])
    aux_t=read_excel_default(INPUT_DIR / FILES["aux_tempos"])
    aux_e=read_excel_default(INPUT_DIR / FILES["aux_evolucao"])

    tel_p=processar_telefonia(tel, emp_tel, grp_tel, nivel_tel)
    wpp_p=processar_whatsapp(wpp, emp_wpp, grp_wpp, nivel_wpp)
    chat_p = processar_chatvideo(chat, aux_t, emp_chat, grp_chat, nivel_chat, status_map)
    tele_p=processar_teleconsultas(tele, aux_e, emp_tele, grp_tele, nivel_tele_esp, nivel_tele_todos)

    final=pd.concat([tel_p,wpp_p,chat_p,tele_p], ignore_index=True).dropna(how="all")
    final=ensure_final_columns(final)
    final["Tempo de Atendimento"]=formatar_tempo(final["Tempo de Atendimento"])
    final["Tempo de Espera"]=formatar_tempo(final["Tempo de Espera"])


    final=formatar_data_coluna(final, "Data")
    final=final.fillna("")
    for col in final.columns:
        final[col]=final[col].apply(sanitizar_valor_excel)
    save_excel_safe(final, OUTPUT_FILE)
