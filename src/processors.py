import pandas as pd
from .utils import limpar_colunas, limpar_textos_df, normalizar_texto, limpar_formula_excel
from .mappings import (
    apply_Status_chatvideo,
    map_empresa,
    map_grupo,
    apply_nivel_telefonia,
    apply_nivel_whatsapp,
    apply_nivel_teleconsulta,
    apply_nivel_chatvideo,
)
import numpy as np

def processar_telefonia(df, mapa_empresa, mapa_grupo, mapa_nivel):
    df=limpar_textos_df(limpar_colunas(df))
    for c in ["Identificador - UniqueID","Identificador - LinkedID"]:
        df[c]=df[c].apply(limpar_formula_excel)
    df=df[~df["Agrupador - Centro de Custo"].apply(normalizar_texto).isin(["raiz","medico","cac"])]
    df=df[df["Agrupador - Tipo de Ligação"].apply(normalizar_texto)=="fila"]
    df=df[~df["Agrupador - Fila"].apply(normalizar_texto).isin(["hospitalclinicashc","medico","cac","filateste3","filateste1"])]
    out=pd.DataFrame()
    out["Data"]=df["Data/Hora - Inicio"]
    out["ID"]=df["Identificador - UniqueID"]
    out["Status"]=df["Agrupador - Status"]
    out["Empresa"]=map_empresa(df["Agrupador - Fila"], mapa_empresa)
    out["Grupo de Clientes"]=map_grupo(df["Agrupador - Fila"], mapa_grupo)
    out["Tempo de Atendimento"]=df["Tempo - Atendimento - Total"]
    out["Tempo de Espera"]=df["Tempo - Espera - Total"]
    out["Nível"]=apply_nivel_telefonia(df["Agrupador - Fila"], mapa_nivel)
    out["Centro de Custo"]=df["Agrupador - Centro de Custo"]
    out["Canal de Atendimento"]="Telefone"
    out["LinkedID (Telefonia)"]=df["Identificador - LinkedID"]
    out["Status Final (Telefonia)"]=df["Agrupador - Status Final"]
    out["Origem"]="Telefonia"
    return out

def processar_whatsapp(df, mapa_empresa, mapa_grupo, mapa_nivel):
    df = limpar_colunas(df)
    df = limpar_textos_df(df)

    # Filtro de Centro de Custo — mesmo padrão de processar_telefonia():
    # exclui por lista (~isin), agora removendo apenas "CAC"
    df = df[
        ~df["Detalhe - Centro de Custo"].apply(normalizar_texto).isin(["cac"])
    ]

    # Filtro de linhas sem fila/rede social válida
    df = df[df["Detalhe - Rede Social"].notna()]
    df = df[df["Detalhe - Rede Social"].apply(normalizar_texto) != "-"]

    df_out = pd.DataFrame()
    df_out["Data"] = df["Data/Hora - Inicio"]
    df_out["ID"] = df["Detalhe - Protocolo"]
    df_out["Status"] = "Concluído" # Rever métrica para definir um atendimento concluído de WhatsApp, mas por enquanto todos os registros são considerados concluídos
    df_out["Empresa"] = map_empresa(df["Detalhe - Rede Social"], mapa_empresa)
    df_out["Grupo de Clientes"] = map_grupo(df["Detalhe - Rede Social"], mapa_grupo)
    df_out["Tempo de Atendimento"] = df["Tempos - Atendimento"]
    df_out["Tempo de Espera"] = "00:00:00"  # não fornecido no novo formato
    df_out["Nível"] = apply_nivel_whatsapp(df["Detalhe - Rede Social"], mapa_nivel)
    df_out["Centro de Custo"] = df["Detalhe - Centro de Custo"]
    df_out["Canal de Atendimento"] = "WhatsApp"
    df_out["Origem"] = "WhatsApp"

    total_linhas = len(df)
    print(f"[WhatsApp] Linhas totais após filtros: {total_linhas}")

    return df_out

def tratar_aux_tempos(aux):
    aux=limpar_colunas(aux)
    req=["IdAtendimento","TME","TMA"]
    miss=[c for c in req if c not in aux.columns]
    if miss: raise ValueError(f"Aux_tempos sem colunas: {miss}. Disponíveis: {list(aux.columns)}")
    aux=aux[req].copy()
    aux["IdAtendimento"]=pd.to_numeric(aux["IdAtendimento"], errors="coerce")
    return aux.drop_duplicates("IdAtendimento", keep="first")

def processar_chatvideo(df, aux_tempos, mapa_empresa, mapa_grupo, mapa_nivel, mapa_status):
    df=limpar_textos_df(limpar_colunas(df))
    df=df[df["Tipo Comunicação"].apply(normalizar_texto).isin(["chat","video"])]
    df=df[df["Descrição CBO"].apply(normalizar_texto)=="enfermeiro"]
    df["IdAtendimento"]=pd.to_numeric(df["IdAtendimento"], errors="coerce")
    df=df.merge(tratar_aux_tempos(aux_tempos), on="IdAtendimento", how="left")
    out=pd.DataFrame()
    out["Data"]=df["Data"]
    out["ID"]=df["IdAtendimento"]
    out["Status"]=apply_Status_chatvideo(df["Razão Chamada"], mapa_status)
    out["Empresa"]=map_empresa(df["Empresa"], mapa_empresa)
    out["Grupo de Clientes"]=map_grupo(df["Empresa"], mapa_grupo)
    out["Tempo de Atendimento"]=df["TMA"]
    out["Tempo de Espera"]=df["TME"]
    out["Tipo de Atendimento (Teleconsulta/N2)"]=df["Tipo Atendimento"]
    out["Nível"] = apply_nivel_chatvideo(df["Empresa"], mapa_nivel)
    out["Canal de Atendimento"]=df["Tipo Comunicação"]
    out["Razão da Chamada (Chat/Video)"]=df["Razão Chamada"]
    out["Desfecho (Teleconsulta/N2)"]=df["Desfecho"]
    out["Origem"]="ChatVideo"
    print(f"[ChatVideo] Linhas após filtro: {len(df)} | sem TMA: {df['TMA'].isna().sum()}")
    return out

def tratar_aux_evolucao(aux):
    aux = limpar_textos_df(limpar_colunas(aux))

    mapa_colunas = {
        normalizar_texto(c): c
        for c in aux.columns
    }
    col_id = mapa_colunas.get("idatendimento")
    col_item = mapa_colunas.get("item atendimento")
    col_resposta = mapa_colunas.get("resposta")
    if not col_id or not col_item or not col_resposta:
        raise ValueError(
            "Aux_evolucao.xlsx não possui as colunas obrigatórias para a lógica de desfecho.\n"
            "Esperado: IdAtendimento, Item Atendimento, Resposta.\n"
            f"Colunas disponíveis: {list(aux.columns)}"
        )
    aux = aux[[col_id, col_item, col_resposta]].copy()
    aux.columns = [
        "IdAtendimento",
        "Item Atendimento",
        "Resposta"
    ]
    aux = aux[
        aux["Item Atendimento"]
        .apply(normalizar_texto)
        .str.contains("desfecho", na=False)
    ].copy()
    aux["IdAtendimento"] = pd.to_numeric(
        aux["IdAtendimento"],
        errors="coerce"
    )
    aux = aux.dropna(subset=["IdAtendimento"])
    aux = aux.drop_duplicates(
        subset="IdAtendimento",
        keep="last"
    )
    return aux

def processar_teleconsultas(df,aux_evolucao,mapa_empresa,mapa_grupo,mapa_nivel_esp,mapa_nivel_todos):
    df = limpar_textos_df(limpar_colunas(df))
    df["IdAgendamento"] = pd.to_numeric(
        df["IdAgendamento"],
        errors="coerce"
    )

    aux = tratar_aux_evolucao(aux_evolucao)
    df = df.merge(
        aux,
        left_on="IdAgendamento",
        right_on="IdAtendimento",
        how="left"
    )

    out = pd.DataFrame()
    out["Data"] = df["Data Slot"]
    out["ID"] = df["IdAgendamento"]
    out["Empresa"] = map_empresa(df["Empresa"], mapa_empresa)
    out["Grupo de Clientes"] = map_grupo(df["Empresa"], mapa_grupo)
    out["Nível"] = apply_nivel_teleconsulta(
        df["Especialidade"],
        df["Tipo Atendimento"],
        mapa_nivel_esp,
        mapa_nivel_todos
    ) 

    out["Tempo de Espera"] = (
        df["Data Profissional Acessou Sala"] -
        df["Data Paciente Entrou na Fila"]
    )

    out["Tempo de Atendimento"] = (
        df["Data Profissional Saiu Sessão Vídeo"] -
        df["Data Paciente Acessou Sala"]
    )

    out["Status"] = np.where(
        df["Tipo Atendimento"].apply(normalizar_texto) == "atendimento assincrono",
        df["Situacao do Atendimento"],
        np.where(
            out["Tempo de Atendimento"].isna() |
            out["Tempo de Espera"].isna(),
            "Não Realizado",
            df["Situacao do Atendimento"]
        )
    )

    out["Canal de Atendimento"] = "Teleconsulta"
    out["Nota de Serviço"] = df["Nota Avaliação Serviço"]
    out["Tipo de Atendimento (Teleconsulta/N2)"] = df["Tipo Atendimento"]
    out["Especialidade (Teleconsulta)"] = df["Especialidade"]
    out["Desfecho (Teleconsulta/N2)"] = df["Resposta"]
    out["Origem"] = "Teleconsulta"
    print(f"[Teleconsultas] Linhas após join evolução: {len(df)}")
    print(
        f"[Teleconsultas] Sem desfecho após join: "
        f"{df['Resposta'].isna().sum()} ({df['Resposta'].isna().mean():.1%})"
    )
    return out
