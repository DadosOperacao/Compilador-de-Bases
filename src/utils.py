import re
import unicodedata
import pandas as pd

INVALID_EXCEL_CHARS = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]")
MAX_EXCEL_CELL_LEN = 32767

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().lower().replace("\xa0", " ")
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

def limpar_colunas(df):
    df = df.copy()
    df.columns = [str(c).strip().replace("\xa0", " ") for c in df.columns]
    return df

def limpar_textos_df(df):
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)
    return df

def limpar_formula_excel(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor).strip()
    if valor.startswith('="') and valor.endswith('"'):
        valor = valor[2:-1]
    if valor.startswith("="):
        valor = valor[1:]
    return valor

def sanitizar_valor_excel(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor)
    valor = INVALID_EXCEL_CHARS.sub("", valor)
    if len(valor) > MAX_EXCEL_CELL_LEN:
        valor = valor[:MAX_EXCEL_CELL_LEN]
    if valor.startswith(("=", "+", "-", "@")):
        valor = "'" + valor
    return valor

def formatar_data_coluna(df, col):
    df = df.copy()
    if col in df.columns:
        dt = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        df[col] = dt.dt.strftime("%d/%m/%Y %H:%M:%S").fillna("")
    return df

def formatar_tempo(series):
    def fmt(x):
        if pd.isna(x):
            return ""
        if isinstance(x, pd.Timedelta):
            sec = int(x.total_seconds())
            if sec < 0: return ""
            return f"{sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}"
        txt = str(x).strip()
        if txt.lower() in ["nat", "nan", "none"]:
            return ""
        if "days" in txt:
            return txt.split(" ")[-1]
        return txt
    return series.apply(fmt)
