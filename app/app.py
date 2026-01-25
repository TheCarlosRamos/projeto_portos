from __future__ import annotations
import os
from io import BytesIO
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import io_utils as iox
import services as svc
import db as dbx
load_dotenv()
DB_URL=os.environ.get('DB_URL','postgresql+psycopg2://app:app@db:5432/portos')
st.set_page_config(page_title='Gestão de Concessões Portuárias', layout='wide')
st.title('Gestão de Concessões Portuárias – Planilha 00/01/02 + Banco (PostgreSQL)')
if 'df00' not in st.session_state:
    st.session_state.df00=pd.DataFrame(columns=iox.COLS_00)
    st.session_state.df01=pd.DataFrame(columns=iox.COLS_01)
    st.session_state.df02=pd.DataFrame(columns=iox.COLS_02)
@st.cache_resource(show_spinner=False)
def get_engine():
    engine=dbx.get_engine(DB_URL); dbx.create_schema(engine); return engine
engine=get_engine()
st.sidebar.header('Entrada de dados')
upload=st.sidebar.file_uploader('Selecione o arquivo .xlsx', type=['xlsx'])
st.sidebar.header('Banco de Dados')
col1,col2=st.sidebar.columns(2)
if col1.button('Carregar do Banco'):
    st.session_state.df00, st.session_state.df01, st.session_state.df02 = dbx.db_to_df(engine)
    st.sidebar.success('Dados carregados do banco.')
if col2.button('Salvar no Banco'):
    e0=svc.validate_cadastro(st.session_state.df00)
    e1=svc.validate_servicos(st.session_state.df01, st.session_state.df00)
    e2=svc.validate_acompanhamento(st.session_state.df02, st.session_state.df01)
    if not e0.empty or not e1.empty or not e2.empty:
        st.sidebar.error('Há erros de validação. Corrija antes de salvar.')
    else:
        dbx.df_to_db(engine, st.session_state.df00, st.session_state.df01, st.session_state.df02)
        st.sidebar.success('Dados salvos no banco.')
if st.sidebar.button('Importar Excel → Banco'):
    if not upload:
        st.sidebar.warning('Envie um arquivo .xlsx acima.')
    else:
        df00,df01,df02=iox.read_excel(upload)
        e0=svc.validate_cadastro(df00); e1=svc.validate_servicos(df01, df00); e2=svc.validate_acompanhamento(df02, df01)
        if not e0.empty or not e1.empty or not e2.empty:
            st.sidebar.error('Erros de validação no arquivo. Corrija e tente novamente.')
        else:
            dbx.df_to_db(engine, df00, df01, df02)
            st.sidebar.success('Arquivo importado e salvo no banco.')
if st.sidebar.button('Exportar do Banco → Excel'):
    df00,df01,df02=dbx.db_to_df(engine)
    buf=BytesIO(); iox.write_excel(buf, df00, df01, df02); buf.seek(0)
    st.sidebar.download_button('Baixar Excel do Banco', data=buf, file_name='portos_concessoes_db.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
aba_cad, aba_srv, aba_mon, aba_exp = st.tabs(['Cadastro (00)','Serviços (01)','Acompanhamento (02)','Exportar'])
with aba_cad:
    st.subheader('Tabela 00 - Cadastro')
    edited=st.data_editor(st.session_state.df00, use_container_width=True, num_rows='dynamic', column_config={
        'Tipo': st.column_config.SelectboxColumn(options=svc.TIPO_LIST, required=False),
        'UF': st.column_config.TextColumn(help='Use ";" para múltiplas UFs (ex.: MT; MS)'),
        'CAPEX Total': st.column_config.NumberColumn(format='%.2f'),
        'Data de assinatura do contrato': st.column_config.DateColumn(format='DD/MM/YYYY'),
        'Coordenada E (UTM)': st.column_config.NumberColumn(),
        'Coordenada S (UTM)': st.column_config.NumberColumn(),
        'Fuso': st.column_config.NumberColumn(),
    }, hide_index=True)
    if st.button('Validar cadastro'):
        errs=svc.validate_cadastro(edited)
        if errs.empty:
            st.success('Cadastro válido.'); st.session_state.df00=edited
        else:
            st.error('Foram encontrados erros:'); st.dataframe(errs, use_container_width=True)
with aba_srv:
    st.subheader('Tabela 01 - Serviços')
    with st.expander('Novo serviço (assistido)'):
        if st.session_state.df00.empty:
            st.info('Cadastre ao menos um objeto na Tabela 00 para vincular serviços.')
        else:
            cad_keys=st.session_state.df00[['Zona portuária','UF','Obj. de Concessão']].astype(str)
            cad_keys['key']=cad_keys['Zona portuária']+' | '+cad_keys['UF']+' | '+cad_keys['Obj. de Concessão']
            key2row={row['key']:(row['Zona portuária'],row['UF'],row['Obj. de Concessão']) for _,row in cad_keys.iterrows()}
            chosen=st.selectbox('Vincular ao cadastro', list(key2row.keys()))
            c1,c2,c3=st.columns(3)
            tipo_srv=c1.text_input('Tipo de Serviço'); fase=c2.text_input('Fase'); serv=c3.text_input('Serviço')
            desc_srv=st.text_input('Descrição do serviço')
            d1,d2=st.columns(2); prazo_i=d1.number_input('Prazo início (anos)', min_value=0, step=1); prazo_f=d2.number_input('Prazo final (anos)', min_value=0, step=1)
            e1,e2=st.columns(2); fonte_prazo=e1.text_input('Fonte (Prazo)', value='Estimado'); perc_capex=e2.number_input('% de CAPEX para o serviço', min_value=0.0, max_value=100.0, value=10.0)
            e3,_=st.columns(2); fonte_perc=e3.text_input('Fonte (% do CAPEX)', value='Estimado')
            if st.button('Adicionar serviço'):
                z,uf,obj=key2row[chosen]
                new={c:None for c in iox.COLS_01}; new.update({'Zona portuária':z,'UF':uf,'Obj. de Concessão':obj,'Tipo de Serviço':tipo_srv,'Fase':fase,'Serviço':serv,'Descrição do serviço':desc_srv,'Prazo início (anos)':int(prazo_i),'Prazo final (anos)':int(prazo_f),'Fonte (Prazo)':fonte_prazo,'% de CAPEX para o serviço':perc_capex,'Fonte (% do CAPEX)':fonte_perc})
                row=pd.Series(new); row=svc.compute_service_fields(row, st.session_state.df00)
                st.session_state.df01=pd.concat([st.session_state.df01, pd.DataFrame([row])], ignore_index=True)
                st.success('Serviço adicionado com sucesso.')
    edited01=st.data_editor(st.session_state.df01, use_container_width=True, num_rows='dynamic', column_config={
        '% de CAPEX para o serviço': st.column_config.NumberColumn(format='%.4f'),
        'CAPEX do Serviço': st.column_config.NumberColumn(format='%.2f', disabled=True),
        'Data de início': st.column_config.DateColumn(format='DD/MM/YYYY'),
        'Data final': st.column_config.DateColumn(format='DD/MM/YYYY'),
    }, hide_index=True)
    ca,cb=st.columns(2)
    if ca.button('Recalcular datas e CAPEX (todas)'):
        df=edited01.copy(); df=df.apply(lambda r: svc.compute_service_fields(r, st.session_state.df00), axis=1); st.session_state.df01=df; st.success('Recalculado.')
    if cb.button('Validar serviços'):
        errs=svc.validate_servicos(edited01, st.session_state.df00)
        if errs.empty:
            st.success('Serviços válidos.'); st.session_state.df01=edited01
        else:
            st.error('Erros encontrados:'); st.dataframe(errs, use_container_width=True)
with aba_mon:
    st.subheader('Tabela 02 - Acompanhamento')
    edited02=st.data_editor(st.session_state.df02, use_container_width=True, num_rows='dynamic', column_config={
        '% executada': st.column_config.NumberColumn(format='%.4f'),
        'CAPEX (Reaj.)': st.column_config.NumberColumn(format='%.2f'),
        'Valor executado': st.column_config.NumberColumn(format='%.2f'),
        'Data da atualização': st.column_config.DateColumn(format='DD/MM/YYYY'),
    }, hide_index=True)
    if st.button('Validar acompanhamento'):
        errs=svc.validate_acompanhamento(edited02, st.session_state.df01)
        if errs.empty:
            st.success('Acompanhamento válido.'); st.session_state.df02=edited02
        else:
            st.error('Erros encontrados:'); st.dataframe(errs, use_container_width=True)
with aba_exp:
    st.subheader('Exportar Excel (UI)')
    df01=st.session_state.df01.copy(); df01['% de CAPEX para o serviço']=df01['% de CAPEX para o serviço'].apply(svc.normalize_percentage)
    df02=st.session_state.df02.copy(); df02['% executada']=df02['% executada'].apply(svc.normalize_percentage)
    buf=BytesIO(); iox.write_excel(buf, st.session_state.df00, df01, df02); buf.seek(0)
    st.download_button('Baixar planilha .xlsx', data=buf, file_name='portos_concessoes.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
