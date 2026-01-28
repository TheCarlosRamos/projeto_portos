from __future__ import annotations
import pandas as pd
from typing import List, Tuple

SHEET_NAMES_CAD = ["Tabela 00 - Cadastro", "Planilha 00", "Cadastro", "00"]
SHEET_NAMES_SRV = ["Tabela 01 - Serviços", "Planilha 01", "Serviços", "01"]
SHEET_NAMES_MON = ["Tabela 02 - Acompanhamento", "Planilha 02", "Acompanhamento", "02"]

COLS_00 = [
    "Zona portuária","UF","Obj. de Concessão","Tipo","CAPEX Total","CAPEX Executado","% CAPEX Executado",
    "Data de assinatura do contrato","Descrição","Latitude","Longitude"
]

COLS_01 = [
    "Zona portuária","UF","Obj. de Concessão","Tipo de Serviço","Fase","Serviço","Descrição do serviço",
    "Prazo início (anos)","Data de início","Prazo final (anos)","Data final","Fonte (Prazo)",
    "% de CAPEX para o serviço","CAPEX do Serviço (total)","CAPEX do Serviço (exec.)","% CAPEX exec.",
    "Fonte (% do CAPEX)"
]

COLS_02 = [
    "Zona portuária","UF","Obj. de Concessão","Tipo de Serviço","Fase","Serviço","Descrição",
    "% executada","CAPEX (Reaj.)","Valor executado","Data da atualização",
    "Responsável","Cargo","Setor","Riscos Relacionados (Tipo)","Riscos Relacionados (Descrição)"
]

def _find_sheet_name(book: pd.ExcelFile, candidates: List[str]) -> str | None:
    for cand in candidates:
        if cand in book.sheet_names:
            return cand
    return None

def read_excel(path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    xl = pd.ExcelFile(path)
    name00 = _find_sheet_name(xl, SHEET_NAMES_CAD)
    name01 = _find_sheet_name(xl, SHEET_NAMES_SRV)
    name02 = _find_sheet_name(xl, SHEET_NAMES_MON)

    def _read(name, cols):
        if name is None:
            return pd.DataFrame(columns=cols)
        df = xl.parse(name)
        common = [c for c in cols if c in df.columns]
        df = df[common]
        for c in cols:
            if c not in df.columns:
                df[c] = pd.Series(dtype=object)
        return df[cols]

    return _read(name00, COLS_00), _read(name01, COLS_01), _read(name02, COLS_02)


def write_excel(path_or_buffer, df00: pd.DataFrame, df01: pd.DataFrame, df02: pd.DataFrame) -> None:
    with pd.ExcelWriter(path_or_buffer, engine='openpyxl') as writer:
        df00.to_excel(writer, index=False, sheet_name=SHEET_NAMES_CAD[0])
        df01.to_excel(writer, index=False, sheet_name=SHEET_NAMES_SRV[0])
        df02.to_excel(writer, index=False, sheet_name=SHEET_NAMES_MON[0])
