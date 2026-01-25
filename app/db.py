from __future__ import annotations
from typing import Tuple, Dict
from contextlib import contextmanager
from datetime import date

import pandas as pd
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Numeric, Date,
    ForeignKey, UniqueConstraint, CheckConstraint, select, insert, delete
)

from services import normalize_percentage, _parse_date, compute_service_fields

# ---------- Engine & Session helpers ----------

def get_engine(db_url: str):
    return create_engine(db_url, future=True)

@contextmanager
def begin_conn(engine):
    with engine.begin() as conn:
        yield conn

# ---------- Schema ----------

def get_tables():
    meta = MetaData()
    cadastro = Table("cadastro", meta,
        Column("id", Integer, primary_key=True),
        Column("zona_portuaria", String, nullable=False),
        Column("uf", String, nullable=False),
        Column("obj_concessao", String, nullable=False),
        Column("tipo", String, CheckConstraint("tipo IN ('Concessão','Arrendamento','Autorização')")),
        Column("capex_total", Numeric),
        Column("data_ass_contrato", Date),
        Column("descricao", String),
        Column("coord_e_utm", Numeric),
        Column("coord_s_utm", Numeric),
        Column("fuso", Numeric),
        UniqueConstraint("zona_portuaria","uf","obj_concessao")
    )
    servico = Table("servico", meta,
        Column("id", Integer, primary_key=True),
        Column("cadastro_id", Integer, ForeignKey("cadastro.id", ondelete="CASCADE"), nullable=False),
        Column("tipo_servico", String),
        Column("fase", String),
        Column("servico", String),
        Column("descricao_servico", String),
        Column("prazo_inicio_anos", Integer),
        Column("data_inicio", Date),
        Column("prazo_final_anos", Integer),
        Column("data_final", Date),
        Column("fonte_prazo", String),
        Column("perc_capex", Numeric),
        Column("capex_servico", Numeric),
        Column("fonte_perc_capex", String),
        UniqueConstraint("cadastro_id","tipo_servico","fase","servico","descricao_servico")
    )
    acompanhamento = Table("acompanhamento", meta,
        Column("id", Integer, primary_key=True),
        Column("servico_id", Integer, ForeignKey("servico.id", ondelete="CASCADE"), nullable=False),
        Column("descricao", String),
        Column("perc_executada", Numeric),
        Column("capex_reaj", Numeric),
        Column("valor_executado", Numeric),
        Column("data_atualizacao", Date),
        Column("responsavel", String),
        Column("cargo", String),
        Column("setor", String),
        Column("risco_tipo", String),
        Column("risco_descricao", String)
    )
    return meta, cadastro, servico, acompanhamento


def create_schema(engine):
    meta, cadastro, servico, acompanhamento = get_tables()
    meta.create_all(engine)

# ---------- Helpers ----------

KEY00 = ['Zona portuária','UF','Obj. de Concessão']
KEY01 = ['Zona portuária','UF','Obj. de Concessão','Tipo de Serviço','Fase','Serviço','Descrição do serviço']

# ---------- Import/Export ----------

def clear_all(engine):
    meta, cadastro, servico, acompanhamento = get_tables()
    with begin_conn(engine) as conn:
        conn.execute(delete(acompanhamento))
        conn.execute(delete(servico))
        conn.execute(delete(cadastro))


def df_to_db(engine, df00: pd.DataFrame, df01: pd.DataFrame, df02: pd.DataFrame):
    """Substitui o conteúdo do banco pelos DataFrames fornecidos."""
    meta, cadastro, servico, acompanhamento = get_tables()

    # normalizações
    df01n = df01.copy()
    df01n['% de CAPEX para o serviço'] = df01n['% de CAPEX para o serviço'].apply(normalize_percentage)

    df02n = df02.copy()
    df02n['% executada'] = df02n['% executada'].apply(normalize_percentage)

    with begin_conn(engine) as conn:
        # limpa
        conn.execute(delete(acompanhamento))
        conn.execute(delete(servico))
        conn.execute(delete(cadastro))

        # --- cadastro (00)
        for _, r in df00.iterrows():
            ins = insert(cadastro).values(
                zona_portuaria=r.get('Zona portuária'),
                uf=r.get('UF'),
                obj_concessao=r.get('Obj. de Concessão'),
                tipo=r.get('Tipo'),
                capex_total=r.get('CAPEX Total'),
                data_ass_contrato=_parse_date(r.get('Data de assinatura do contrato')),
                descricao=r.get('Descrição'),
                coord_e_utm=r.get('Coordenada E (UTM')) if 'Coordenada E (UTM' in df00.columns else r.get('Coordenada E (UTM)'),
                coord_s_utm=r.get('Coordenada S (UTM')) if 'Coordenada S (UTM' in df00.columns else r.get('Coordenada S (UTM)'),
                fuso=r.get('Fuso')
            )
            conn.execute(ins)

        # mapa natural->id
        rows = conn.execute(select(cadastro.c.id, cadastro.c.zona_portuaria, cadastro.c.uf, cadastro.c.obj_concessao)).all()
        cad_map: Dict[tuple, int] = {(z,u,o): i for i,z,u,o in rows}

        # --- servico (01)
        # Recomputa campos derivados para garantir integridade
        df01calc = df01n.apply(lambda row: compute_service_fields(row, df00), axis=1)
        for _, r in df01calc.iterrows():
            k = (r.get('Zona portuária'), r.get('UF'), r.get('Obj. de Concessão'))
            cad_id = cad_map.get(k)
            if not cad_id:
                continue  # ou levantar erro
            ins = insert(servico).values(
                cadastro_id=cad_id,
                tipo_servico=r.get('Tipo de Serviço'),
                fase=r.get('Fase'),
                servico=r.get('Serviço'),
                descricao_servico=r.get('Descrição do serviço'),
                prazo_inicio_anos=r.get('Prazo início (anos)'),
                data_inicio=_parse_date(r.get('Data de início')),
                prazo_final_anos=r.get('Prazo final (anos)'),
                data_final=_parse_date(r.get('Data final')),
                fonte_prazo=r.get('Fonte (Prazo)'),
                perc_capex=r.get('% de CAPEX para o serviço'),
                capex_servico=r.get('CAPEX do Serviço'),
                fonte_perc_capex=r.get('Fonte (% do CAPEX)')
            )
            conn.execute(ins)

        # mapa serviço natural->id
        rows = conn.execute(select(
            servico.c.id, servico.c.cadastro_id, servico.c.tipo_servico, servico.c.fase, servico.c.servico, servico.c.descricao_servico
        )).all()
        # precisamos também relacionar cadastro_id a (zona, uf, obj)
        cad_rev = {v:k for k,v in cad_map.items()}
        srv_map: Dict[tuple, int] = {}
        for i, cad_id, tipo_s, fase, srv, desc in rows:
            z,u,o = cad_rev[cad_id]
            srv_map[(z,u,o,tipo_s,fase,srv,desc)] = i

        # --- acompanhamento (02)
        for _, r in df02n.iterrows():
            k = (
                r.get('Zona portuária'), r.get('UF'), r.get('Obj. de Concessão'),
                r.get('Tipo de Serviço'), r.get('Fase'), r.get('Serviço'), r.get('Descrição')
            )
            srv_id = srv_map.get(k)
            if not srv_id:
                continue
            ins = insert(acompanhamento).values(
                servico_id=srv_id,
                descricao=r.get('Descrição'),
                perc_executada=r.get('% executada'),
                capex_reaj=r.get('CAPEX (Reaj.)'),
                valor_executado=r.get('Valor executado'),
                data_atualizacao=_parse_date(r.get('Data da atualização')),
                responsavel=r.get('Responsável'),
                cargo=r.get('Cargo'),
                setor=r.get('Setor'),
                risco_tipo=r.get('Riscos Relacionados (Tipo)'),
                risco_descricao=r.get('Riscos Relacionados (Descrição)')
            )
            conn.execute(ins)


def db_to_df(engine) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    meta, cadastro, servico, acompanhamento = get_tables()
    with begin_conn(engine) as conn:
        cad_rows = conn.execute(select(cadastro)).mappings().all()
        df00 = pd.DataFrame(cad_rows)
        if df00.empty:
            df00 = pd.DataFrame(columns=[
                'zona_portuaria','uf','obj_concessao','tipo','capex_total','data_ass_contrato','descricao','coord_e_utm','coord_s_utm','fuso'
            ])
        df00 = df00.rename(columns={
            'zona_portuaria':'Zona portuária',
            'uf':'UF',
            'obj_concessao':'Obj. de Concessão',
            'tipo':'Tipo',
            'capex_total':'CAPEX Total',
            'data_ass_contrato':'Data de assinatura do contrato',
            'descricao':'Descrição',
            'coord_e_utm':'Coordenada E (UTM)',
            'coord_s_utm':'Coordenada S (UTM)',
            'fuso':'Fuso'
        })

        # join servico + cadastro
        j = servico.join(cadastro, servico.c.cadastro_id==cadastro.c.id)
        srv_rows = conn.execute(select(
            cadastro.c.zona_portuaria.label('Zona portuária'),
            cadastro.c.uf.label('UF'),
            cadastro.c.obj_concessao.label('Obj. de Concessão'),
            servico.c.tipo_servico.label('Tipo de Serviço'),
            servico.c.fase.label('Fase'),
            servico.c.servico.label('Serviço'),
            servico.c.descricao_servico.label('Descrição do serviço'),
            servico.c.prazo_inicio_anos.label('Prazo início (anos)'),
            servico.c.data_inicio.label('Data de início'),
            servico.c.prazo_final_anos.label('Prazo final (anos)'),
            servico.c.data_final.label('Data final'),
            servico.c.fonte_prazo.label('Fonte (Prazo)'),
            servico.c.perc_capex.label('% de CAPEX para o serviço'),
            servico.c.capex_servico.label('CAPEX do Serviço'),
            servico.c.fonte_perc_capex.label('Fonte (% do CAPEX)')
        ).select_from(j)).mappings().all()
        df01 = pd.DataFrame(srv_rows)
        if df01.empty:
            df01 = pd.DataFrame(columns=[
                'Zona portuária','UF','Obj. de Concessão','Tipo de Serviço','Fase','Serviço','Descrição do serviço',
                'Prazo início (anos)','Data de início','Prazo final (anos)','Data final','Fonte (Prazo)','% de CAPEX para o serviço','CAPEX do Serviço','Fonte (% do CAPEX)'
            ])

        # join acompanhamento + servico + cadastro
        j2 = acompanhamento.join(servico, acompanhamento.c.servico_id==servico.c.id)                            .join(cadastro, servico.c.cadastro_id==cadastro.c.id)
        mon_rows = conn.execute(select(
            cadastro.c.zona_portuaria.label('Zona portuária'),
            cadastro.c.uf.label('UF'),
            cadastro.c.obj_concessao.label('Obj. de Concessão'),
            servico.c.tipo_servico.label('Tipo de Serviço'),
            servico.c.fase.label('Fase'),
            servico.c.servico.label('Serviço'),
            acompanhamento.c.descricao.label('Descrição'),
            acompanhamento.c.perc_executada.label('% executada'),
            acompanhamento.c.capex_reaj.label('CAPEX (Reaj.)'),
            acompanhamento.c.valor_executado.label('Valor executado'),
            acompanhamento.c.data_atualizacao.label('Data da atualização'),
            acompanhamento.c.responsavel.label('Responsável'),
            acompanhamento.c.cargo.label('Cargo'),
            acompanhamento.c.setor.label('Setor'),
            acompanhamento.c.risco_tipo.label('Riscos Relacionados (Tipo)'),
            acompanhamento.c.risco_descricao.label('Riscos Relacionados (Descrição)')
        ).select_from(j2)).mappings().all()
        df02 = pd.DataFrame(mon_rows)
        if df02.empty:
            df02 = pd.DataFrame(columns=[
                'Zona portuária','UF','Obj. de Concessão','Tipo de Serviço','Fase','Serviço','Descrição','% executada','CAPEX (Reaj.)','Valor executado','Data da atualização','Responsável','Cargo','Setor','Riscos Relacionados (Tipo)','Riscos Relacionados (Descrição)'
            ])

        return df00, df01, df02
