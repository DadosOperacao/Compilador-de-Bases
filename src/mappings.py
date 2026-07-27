import pandas as pd
from .utils import normalizar_texto, limpar_colunas

MEDICO_FAMILIA_NORM = normalizar_texto("Médico da Família")
TIPOS_N3_MEDICO_FAMILIA = {
    normalizar_texto("Atendimento Assíncrono"),
    normalizar_texto("Pronto Atendimento"),
}

def load_clientes(path):
    df = pd.read_excel(path, sheet_name="Clientes", header=3)
    df = limpar_colunas(df)
    req = ["Arquivo Original", "Campo Original", "Valor Original", "Valor Formatado", "Grupo de Clientes Formatado"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise ValueError(f"Aba Clientes sem colunas: {missing}. Disponíveis: {list(df.columns)}")
    df = df.dropna(subset=["Arquivo Original", "Valor Original"]).copy()
    for c in ["Arquivo Original", "Campo Original", "Valor Original"]:
        df[c+" Norm"] = df[c].apply(normalizar_texto)
    return df

def build_empresa_grupo_map(df_clientes, origem, campo):
    sub = df_clientes[(df_clientes["Arquivo Original Norm"] == normalizar_texto(origem)) &
                      (df_clientes["Campo Original Norm"] == normalizar_texto(campo))].copy()
    mapa_empresa = dict(zip(sub["Valor Original Norm"], sub["Valor Formatado"].fillna("")))
    mapa_grupo = dict(zip(sub["Valor Original Norm"], sub["Grupo de Clientes Formatado"].fillna("")))
    return mapa_empresa, mapa_grupo


def map_empresa(series, mapa):
    return series.apply(lambda v: mapa.get(normalizar_texto(v), v if not pd.isna(v) else ""))

def map_grupo(series, mapa):
    return series.apply(lambda v: mapa.get(normalizar_texto(v), ""))

def map_status(series, mapa):
    return series.apply(lambda v: mapa.get(normalizar_texto(v), ""))

def load_niveis(path):
    df = pd.read_excel(path, sheet_name="Níveis", header=2)
    df = limpar_colunas(df)
    return df

def load_status(path):
    df = pd.read_excel(path, sheet_name="Status", header=2)
    df = limpar_colunas(df)
    return df


def build_nivel_telefonia(df):
    req = ["Valor Original", "Nível da fila"]
    missing=[c for c in req if c not in df.columns]
    if missing: raise ValueError(f"Aba Níveis sem colunas Telefonia: {missing}")
    sub=df[req].dropna(subset=req).copy()
    sub["key"]=sub["Valor Original"].apply(normalizar_texto)
    return dict(zip(sub["key"], sub["Nível da fila"]))

def build_nivel_whatsapp(df):
    req=["Filas de WhatsApp","Nível de WhatsApp"]
    missing=[c for c in req if c not in df.columns]
    if missing: raise ValueError(f"Aba Níveis sem colunas WhatsApp: {missing}")
    sub=df[req].dropna(subset=req).copy()
    sub=sub[sub["Filas de WhatsApp"].apply(normalizar_texto)!="filas"]
    sub["key"]=sub["Filas de WhatsApp"].apply(normalizar_texto)
    return dict(zip(sub["key"], sub["Nível de WhatsApp"]))

def build_nivel_teleconsulta(df):
    req=["Especialidade","Tipo de Atendimento","Nível"]
    missing=[c for c in req if c not in df.columns]
    if missing: raise ValueError(f"Aba Níveis sem colunas Teleconsulta: {missing}. Disponíveis: {list(df.columns)}")
    sub=df[req].dropna(subset=req).copy()
    sub=sub[sub["Especialidade"].apply(normalizar_texto)!="especialidade"]
    especifico, todos = {}, {}
    for _, r in sub.iterrows():
        esp=normalizar_texto(r["Especialidade"]); tipo=normalizar_texto(r["Tipo de Atendimento"]); nivel=r["Nível"]
        if tipo == "todos": todos[esp]=nivel
        else: especifico[(esp,tipo)] = nivel
    return especifico, todos

def build_nivel_chatvideo(df):
    req = ["Filas chatvideo", "Nível chatvideo"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise ValueError(
            f"Aba Níveis sem colunas ChatVideo: {missing}. "
            f"Disponíveis: {list(df.columns)}"
        )
    sub = df[req].dropna(subset=req).copy()
    # Remove eventual linha de cabeçalho interna se vier como dado
    sub = sub[
        sub["Filas chatvideo"].apply(normalizar_texto) != "filas chatvideo"
    ]
    sub["key"] = sub["Filas chatvideo"].apply(normalizar_texto)
    return dict(zip(sub["key"], sub["Nível chatvideo"]))

def build_status_map(df):
    req=["Campo Original","Status"]
    missing=[c for c in req if c not in df.columns]
    if missing: raise ValueError(f"Aba Níveis sem colunas WhatsApp: {missing}")
    sub=df[req].dropna(subset=req).copy()
    sub=sub[sub["Campo Original"].apply(normalizar_texto)!="filas"]
    sub["key"]=sub["Campo Original"].apply(normalizar_texto)
    return dict(zip(sub["key"], sub["Status"]))


def apply_nivel_telefonia(series, mapa):
    return series.apply(lambda v: mapa.get(normalizar_texto(v), ""))

def apply_nivel_whatsapp(series, mapa):
    def f(v):
        k=normalizar_texto(v)
        if k in mapa: return mapa[k]
        if "todas" in mapa: return mapa["todas"]
        return ""
    return series.apply(f)

def apply_nivel_teleconsulta(esp_series, tipo_series, mapa_esp, mapa_todos):
    out = []
    for esp, tipo in zip(esp_series, tipo_series):
        e = normalizar_texto(esp)
        t = normalizar_texto(tipo)
        
        if e == MEDICO_FAMILIA_NORM:
            out.append("N3" if t in TIPOS_N3_MEDICO_FAMILIA else "N4")
            continue

        out.append(mapa_esp.get((e, t), mapa_todos.get(e, "")))

    return pd.Series(out, index=esp_series.index)

def apply_nivel_chatvideo(series_empresa, mapa):
    return series_empresa.apply(
        lambda v: mapa.get(normalizar_texto(v), "")
    )

def apply_Status_chatvideo(series_empresa, mapa):
    return series_empresa.apply(
        lambda v: mapa.get(normalizar_texto(v), "")
    )