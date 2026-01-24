from __future__ import annotations
import pandas as pd
from datetime import datetime, date

UF_LIST = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR',
    'PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
]
TIPO_LIST = ['Concessão','Arrendamento','Autorização']

def _parse_date(s):
    if pd.isna(s) or s == '':
        return None
    if isinstance(s, (date, datetime)):
        return pd.to_datetime(s).date()
    for fmt in ("%d/%m/%Y","%Y-%m-%d","%d-%m-%Y","%m/%d/%Y"):
        try:
            return datetime.strptime(str(s), fmt).date()
        except Exception:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True).date()
    except Exception:
        return None

def add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + int(years))
    except ValueError:
        return d.replace(month=2, day=28, year=d.year + int(years))

def normalize_percentage(x):
    if pd.isna(x) or x == '':
        return None
    try:
        val = float(x)
        if val > 1:
            val = val / 100.0
        return max(0.0, min(1.0, val))
    except Exception:
        return None

def compute_service_fields(row01: pd.Series, df00: pd.DataFrame) -> pd.Series:
    mask = (
        (df00['Zona portuária'] == row01['Zona portuária']) &
        (df00['UF'] == row01['UF']) &
        (df00['Obj. de Concessão'] == row01['Obj. de Concessão'])
    )
    cad = df00[mask]
    if cad.empty:
        return row01

    assinatura = _parse_date(cad.iloc[0].get('Data de assinatura do contrato'))
    try:
        capex_total = float(cad.iloc[0].get('CAPEX Total'))
    except Exception:
        capex_total = None

    for col in ['Prazo início (anos)','Prazo final (anos)']:
        try:
            row01[col] = int(row01.get(col)) if pd.notna(row01.get(col)) and row01.get(col) != '' else None
        except Exception:
            row01[col] = None

    if assinatura and row01['Prazo início (anos)'] is not None:
        row01['Data de início'] = add_years(assinatura, row01['Prazo início (anos)'])
    if assinatura and row01['Prazo final (anos)'] is not None:
        row01['Data final'] = add_years(assinatura, row01['Prazo final (anos)'])

    perc = normalize_percentage(row01.get('% de CAPEX para o serviço'))
    if perc is not None and capex_total is not None:
        row01['CAPEX do Serviço'] = round(capex_total * perc, 2)
    return row01


def validate_cadastro(df00: pd.DataFrame) -> pd.DataFrame:
    errors = []
    for idx, r in df00.iterrows():
        tipo = r.get('Tipo')
        if pd.notna(tipo) and tipo not in TIPO_LIST:
            errors.append((idx,'Tipo',f"Valor inválido: {tipo}. Opções: {', '.join(TIPO_LIST)}"))
        uf = str(r.get('UF') or '').replace(',', ';')
        if uf.strip():
            for u in [x.strip() for x in uf.split(';') if x.strip()]:
                if u not in UF_LIST:
                    errors.append((idx,'UF',f'UF inválida: {u}'))
        d = r.get('Data de assinatura do contrato')
        if pd.notna(d) and _parse_date(d) is None:
            errors.append((idx,'Data de assinatura do contrato','Data inválida (use DD/MM/AAAA).'))
        for col in ['CAPEX Total','Coordenada E (UTM)','Coordenada S (UTM)','Fuso']:
            v = r.get(col)
            if pd.isna(v) or v == '':
                continue
            try:
                float(v)
            except Exception:
                errors.append((idx,col,'Valor numérico inválido.'))
    return pd.DataFrame(errors, columns=['linha','coluna','erro'])


def validate_servicos(df01: pd.DataFrame, df00: pd.DataFrame) -> pd.DataFrame:
    errors = []
    key00 = set(tuple(x) for x in df00[['Zona portuária','UF','Obj. de Concessão']].dropna().values)
    for idx, r in df01.iterrows():
        k = (r.get('Zona portuária'), r.get('UF'), r.get('Obj. de Concessão'))
        if any(pd.isna(x) or x == '' for x in k):
            continue
        if k not in key00:
            errors.append((idx,'chave (00)','Cadastro (Tabela 00) não encontrado para o serviço.'))
        if pd.notna(r.get('% de CAPEX para o serviço')) and normalize_percentage(r.get('% de CAPEX para o serviço')) is None:
            errors.append((idx,'% de CAPEX para o serviço','Porcentagem inválida.'))
        for col in ['Data de início','Data final']:
            v = r.get(col)
            if pd.isna(v) or v == '':
                continue
            try:
                _ = pd.to_datetime(v, dayfirst=True)
            except Exception:
                errors.append((idx,col,'Data inválida.'))
    return pd.DataFrame(errors, columns=['linha','coluna','erro'])


def validate_acompanhamento(df02: pd.DataFrame, df01: pd.DataFrame) -> pd.DataFrame:
    errors = []
    key01_cols = ['Zona portuária','UF','Obj. de Concessão','Tipo de Serviço','Fase','Serviço','Descrição']
    if not set(key01_cols).issubset(df01.columns):
        return pd.DataFrame(columns=['linha','coluna','erro'])
    key01 = set(tuple(x) for x in df01[key01_cols].fillna('').values)
    for idx, r in df02.iterrows():
        k = tuple(r.get(c) for c in key01_cols)
        if any(pd.isna(x) or x == '' for x in k):
            continue
        if k not in key01:
            errors.append((idx,'chave (01)','Serviço (Tabela 01) não encontrado para o acompanhamento.'))
        val = r.get('% executada')
        if pd.notna(val):
            p = normalize_percentage(val)
            if p is None:
                errors.append((idx,'% executada','Porcentagem inválida.'))
        v = r.get('Data da atualização')
        if pd.notna(v) and str(v) != '':
            try:
                _ = pd.to_datetime(v, dayfirst=True)
            except Exception:
                errors.append((idx,'Data da atualização','Data inválida.'))
    return pd.DataFrame(errors, columns=['linha','coluna','erro'])
