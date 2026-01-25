from __future__ import annotations
import pandas as pd
from typing import List, Tuple
SHEET_NAMES_CAD=["Tabela 00 - Cadastro","Planilha 00","Cadastro","00"]
SHEET_NAMES_SRV=["Tabela 01 - Serviços","Planilha 01","Serviços","01"]
SHEET_NAMES_MON=["Tabela 02 - Acompanhamento","Planilha 02","Acompanhamento","02"]
COLS_00=["Zona portuária","UF","Obj. de Concessão","Tipo","CAPEX Total","Data de assinatura do contrato","Descrição","Coordenada E (UTM)","Coordenada S (UTM)","Fuso"]
COLS_01=["Zona portuária","UF","Obj. de Concessão","Tipo de Serviço","Fase","Serviço","Descrição do serviço","Prazo início (anos)","Data de início","Prazo final (anos)","Data final","Fonte (Prazo)","% de CAPEX para o serviço","CAPEX do Serviço","Fonte (% do CAPEX)"]
COLS_02=["Zona portuária","UF","Obj. de Concessão","Tipo de Serviço","Fase","Serviço","Descrição","% executada","CAPEX (Reaj.)","Valor executado","Data da atualização","Responsável","Cargo","Setor","Riscos Relacionados (Tipo)","Riscos Relacionados (Descrição)"]

def _find(book: pd.ExcelFile, cands: List[str]):
    for c in cands:
        if c in book.sheet_names:
            return c
    return None

def read_excel(path) -> Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    xl=pd.ExcelFile(path)
    def read(name, cols):
        if not name: return pd.DataFrame(columns=cols)
        df=xl.parse(name)
        common=[c for c in cols if c in df.columns]
        df=df[common]
        for c in cols:
            if c not in df.columns:
                df[c]=pd.Series(dtype=object)
        return df[cols]
    return (
        read(_find(xl,SHEET_NAMES_CAD),COLS_00),
        read(_find(xl,SHEET_NAMES_SRV),COLS_01),
        read(_find(xl,SHEET_NAMES_MON),COLS_02)
    )

def write_excel(path_or_buf, df00, df01, df02):
    with pd.ExcelWriter(path_or_buf, engine='openpyxl') as w:
        df00.to_excel(w,index=False, sheet_name=SHEET_NAMES_CAD[0])
        df01.to_excel(w,index=False, sheet_name=SHEET_NAMES_SRV[0])
        df02.to_excel(w,index=False, sheet_name=SHEET_NAMES_MON[0])
