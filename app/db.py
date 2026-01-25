from __future__ import annotations
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import io_utils as iox
import services as svc

DB_PATH = Path(__file__).parent / 'portos.db'

# Lista de UFs válidas
UF_LIST = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR',
    'PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
]

def _schema_atualizado(cursor) -> bool:
    """Verifica se o banco usa o schema novo (com servico_id em acompanhamento)."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='acompanhamento'"
    )
    if not cursor.fetchone():
        return True  # Tabela não existe → vamos criar do zero
    cursor.execute('PRAGMA table_info(acompanhamento)')
    colunas = [row[1] for row in cursor.fetchall()]
    return 'servico_id' in colunas


def init_db():
    """Inicializa o banco de dados criando as tabelas se não existirem."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Se o schema for antigo, dropar views e tabelas para recriar
    if not _schema_atualizado(cursor):
        cursor.execute('PRAGMA foreign_keys = OFF')
        cursor.execute('DROP VIEW IF EXISTS vw_tabela_02_acompanhamento')
        cursor.execute('DROP VIEW IF EXISTS vw_tabela_01_servicos')
        cursor.execute('DROP VIEW IF EXISTS vw_tabela_00_cadastro')
        cursor.execute('DROP TABLE IF EXISTS acompanhamento')
        cursor.execute('DROP TABLE IF EXISTS servico')
        cursor.execute('DROP TABLE IF EXISTS cadastro_uf')
        cursor.execute('DROP TABLE IF EXISTS cadastro')
        cursor.execute('DROP TABLE IF EXISTS uf')
        cursor.execute('PRAGMA foreign_keys = ON')
        conn.commit()
    
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # 1. Tabela de UFs (domínio controlado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uf (
            sigla CHAR(2) PRIMARY KEY
        )
    ''')
    
    # Popular lista de UFs
    for uf in UF_LIST:
        cursor.execute('INSERT OR IGNORE INTO uf(sigla) VALUES (?)', (uf,))
    
    # 2. Tabela 00 - Cadastro
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zona_portuaria TEXT NOT NULL,
            uf_texto TEXT,
            obj_concessao TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('Concessão', 'Arrendamento', 'Autorização') OR tipo IS NULL),
            capex_total REAL,
            data_ass_contrato TEXT,
            descricao TEXT,
            coord_e_utm REAL,
            coord_s_utm REAL,
            fuso INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(zona_portuaria, obj_concessao)
        )
    ''')
    
    # 2.1. Tabela de relacionamento N:N entre cadastro e UFs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_uf (
            cadastro_id INTEGER NOT NULL,
            uf_sigla CHAR(2) NOT NULL,
            PRIMARY KEY (cadastro_id, uf_sigla),
            FOREIGN KEY (cadastro_id) REFERENCES cadastro(id) ON DELETE CASCADE,
            FOREIGN KEY (uf_sigla) REFERENCES uf(sigla)
        )
    ''')
    
    # 3. Tabela 01 - Serviços (referencia cadastro por ID)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cadastro_id INTEGER NOT NULL,
            tipo_servico TEXT,
            fase TEXT,
            servico TEXT,
            descricao_servico TEXT,
            prazo_inicio_anos INTEGER,
            data_inicio TEXT,
            prazo_final_anos INTEGER,
            data_final TEXT,
            fonte_prazo TEXT,
            perc_capex REAL CHECK(perc_capex IS NULL OR (perc_capex >= 0 AND perc_capex <= 1)),
            capex_servico REAL,
            fonte_perc_capex TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cadastro_id) REFERENCES cadastro(id) ON DELETE CASCADE,
            UNIQUE(cadastro_id, tipo_servico, fase, servico, descricao_servico)
        )
    ''')
    
    # 4. Tabela 02 - Acompanhamento (referencia servico por ID)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acompanhamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico_id INTEGER NOT NULL,
            descricao TEXT,
            perc_executada REAL CHECK(perc_executada IS NULL OR (perc_executada >= 0 AND perc_executada <= 1)),
            capex_reaj REAL,
            valor_executado REAL,
            data_atualizacao TEXT,
            responsavel TEXT,
            cargo TEXT,
            setor TEXT,
            risco_tipo TEXT,
            risco_descricao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (servico_id) REFERENCES servico(id) ON DELETE CASCADE
        )
    ''')
    
    # Criar índices
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_cadastro_zona ON cadastro(zona_portuaria)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_cadastro_obj ON cadastro(obj_concessao)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_servico_cadastro ON servico(cadastro_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_servico_natural ON servico(tipo_servico, fase, servico)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_acomp_servico ON acompanhamento(servico_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_acomp_data ON acompanhamento(data_atualizacao)')
    
    # Criar views para exportação (compatíveis com planilhas)
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_tabela_00_cadastro AS
        SELECT
            c.id AS "ID",
            c.zona_portuaria AS "Zona portuária",
            c.uf_texto AS "UF",
            c.obj_concessao AS "Obj. de Concessão",
            c.tipo AS "Tipo",
            c.capex_total AS "CAPEX Total",
            c.data_ass_contrato AS "Data de assinatura do contrato",
            c.descricao AS "Descrição",
            c.coord_e_utm AS "Coordenada E (UTM)",
            c.coord_s_utm AS "Coordenada S (UTM)",
            c.fuso AS "Fuso"
        FROM cadastro c
    ''')
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_tabela_01_servicos AS
        SELECT
            s.id AS "ID",
            c.zona_portuaria AS "Zona portuária",
            c.uf_texto AS "UF",
            c.obj_concessao AS "Obj. de Concessão",
            s.tipo_servico AS "Tipo de Serviço",
            s.fase AS "Fase",
            s.servico AS "Serviço",
            s.descricao_servico AS "Descrição do serviço",
            s.prazo_inicio_anos AS "Prazo início (anos)",
            s.data_inicio AS "Data de início",
            s.prazo_final_anos AS "Prazo final (anos)",
            s.data_final AS "Data final",
            s.fonte_prazo AS "Fonte (Prazo)",
            s.perc_capex AS "% de CAPEX para o serviço",
            s.capex_servico AS "CAPEX do Serviço",
            s.fonte_perc_capex AS "Fonte (% do CAPEX)"
        FROM servico s
        JOIN cadastro c ON c.id = s.cadastro_id
    ''')
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_tabela_02_acompanhamento AS
        SELECT
            a.id AS "ID",
            c.zona_portuaria AS "Zona portuária",
            c.uf_texto AS "UF",
            c.obj_concessao AS "Obj. de Concessão",
            s.tipo_servico AS "Tipo de Serviço",
            s.fase AS "Fase",
            s.servico AS "Serviço",
            a.descricao AS "Descrição",
            a.perc_executada AS "% executada",
            a.capex_reaj AS "CAPEX (Reaj.)",
            a.valor_executado AS "Valor executado",
            a.data_atualizacao AS "Data da atualização",
            a.responsavel AS "Responsável",
            a.cargo AS "Cargo",
            a.setor AS "Setor",
            a.risco_tipo AS "Riscos Relacionados (Tipo)",
            a.risco_descricao AS "Riscos Relacionados (Descrição)"
        FROM acompanhamento a
        JOIN servico s ON s.id = a.servico_id
        JOIN cadastro c ON c.id = s.cadastro_id
    ''')
    
    conn.commit()
    conn.close()

def _parse_date(val):
    """Converte valor para string de data no formato YYYY-MM-DD."""
    if pd.isna(val) or val == '' or val is None:
        return None
    if isinstance(val, str):
        # Tentar converter formatos comuns
        from datetime import datetime
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                dt = datetime.strptime(val, fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                continue
    # Se for objeto date/datetime do pandas
    try:
        dt = pd.to_datetime(val)
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def _format_date(val):
    """Converte string de data do banco para formato da planilha."""
    if not val or val == '':
        return None
    try:
        dt = pd.to_datetime(val)
        return dt.date()
    except:
        return None

def _normalize_uf_texto(uf_texto: str) -> str:
    """Normaliza o texto de UF (ex: 'MT; MS' -> 'MT; MS')."""
    if pd.isna(uf_texto) or uf_texto == '':
        return None
    # Limpar e normalizar separadores
    uf_texto = str(uf_texto).replace(',', ';').strip()
    # Validar cada UF
    ufs = [u.strip() for u in uf_texto.split(';') if u.strip()]
    valid_ufs = [u for u in ufs if u in UF_LIST]
    return '; '.join(valid_ufs) if valid_ufs else None

def _df_to_db_cadastro(df: pd.DataFrame) -> list:
    """Converte DataFrame da Tabela 00 para formato do banco."""
    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row.get('Zona portuária', '')),
            _normalize_uf_texto(row.get('UF')),
            str(row.get('Obj. de Concessão', '')),
            str(row.get('Tipo', '')) if pd.notna(row.get('Tipo')) else None,
            float(row.get('CAPEX Total')) if pd.notna(row.get('CAPEX Total')) else None,
            _parse_date(row.get('Data de assinatura do contrato')),
            str(row.get('Descrição', '')) if pd.notna(row.get('Descrição')) else None,
            float(row.get('Coordenada E (UTM)')) if pd.notna(row.get('Coordenada E (UTM)')) else None,
            float(row.get('Coordenada S (UTM)')) if pd.notna(row.get('Coordenada S (UTM)')) else None,
            int(row.get('Fuso')) if pd.notna(row.get('Fuso')) else None,
        ))
    return rows

def _save_cadastro_ufs(conn, cadastro_id: int, uf_texto: str):
    """Salva relacionamento N:N entre cadastro e UFs."""
    if not uf_texto:
        return
    cursor = conn.cursor()
    # Limpar UFs existentes
    cursor.execute('DELETE FROM cadastro_uf WHERE cadastro_id = ?', (cadastro_id,))
    # Adicionar novas UFs
    ufs = [u.strip() for u in str(uf_texto).replace(',', ';').split(';') if u.strip() and u.strip() in UF_LIST]
    for uf in ufs:
        cursor.execute('INSERT OR IGNORE INTO cadastro_uf(cadastro_id, uf_sigla) VALUES (?, ?)', (cadastro_id, uf.strip()))

def save_cadastro(df: pd.DataFrame) -> bool:
    """Salva o cadastro (Tabela 00) no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # Limpar tabelas relacionadas primeiro (devido a CASCADE)
        cursor.execute('DELETE FROM cadastro_uf')
        cursor.execute('DELETE FROM cadastro')
        
        # Inserir novos dados
        rows = _df_to_db_cadastro(df)
        for row in rows:
            cursor.execute('''
                INSERT INTO cadastro 
                (zona_portuaria, uf_texto, obj_concessao, tipo, capex_total, 
                 data_ass_contrato, descricao, coord_e_utm, coord_s_utm, fuso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            cadastro_id = cursor.lastrowid
            # Salvar relacionamento com UFs
            if row[1]:  # uf_texto
                _save_cadastro_ufs(conn, cadastro_id, row[1])
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar cadastro: {e}")
        import traceback
        traceback.print_exc()
        return False

def _db_to_df_cadastro(rows: list) -> pd.DataFrame:
    """Converte dados do banco para DataFrame da Tabela 00."""
    if not rows:
        return pd.DataFrame(columns=iox.COLS_00)
    
    data = []
    for row in rows:
        data.append({
            'Zona portuária': row[1],
            'UF': row[2] if row[2] else None,
            'Obj. de Concessão': row[3],
            'Tipo': row[4] if row[4] else None,
            'CAPEX Total': row[5] if row[5] is not None else None,
            'Data de assinatura do contrato': _format_date(row[6]) if row[6] else None,
            'Descrição': row[7] if row[7] else None,
            'Coordenada E (UTM)': row[8] if row[8] is not None else None,
            'Coordenada S (UTM)': row[9] if row[9] is not None else None,
            'Fuso': row[10] if row[10] is not None else None,
        })
    df = pd.DataFrame(data)
    # Garantir todas as colunas
    for col in iox.COLS_00:
        if col not in df.columns:
            df[col] = None
    return df[iox.COLS_00]

def load_cadastro() -> pd.DataFrame:
    """Carrega o cadastro (Tabela 00) do banco de dados usando a view."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vw_tabela_00_cadastro ORDER BY "ID"')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return pd.DataFrame(columns=iox.COLS_00)
        
        # Converter da view para DataFrame
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        
        # Remover coluna ID se existir
        if 'ID' in df.columns:
            df = df.drop('ID', axis=1)
        
        # Garantir todas as colunas
        for col in iox.COLS_00:
            if col not in df.columns:
                df[col] = None
        
        return df[iox.COLS_00]
    except Exception as e:
        print(f"Erro ao carregar cadastro: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=iox.COLS_00)

def _df_to_db_servicos(df: pd.DataFrame) -> list:
    """Converte DataFrame da Tabela 01 para formato do banco."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        rows = []
        for _, row in df.iterrows():
            # Buscar cadastro_id pela chave natural
            cursor.execute('''
                SELECT id FROM cadastro 
                WHERE zona_portuaria = ? AND obj_concessao = ?
            ''', (
                str(row.get('Zona portuária', '')),
                str(row.get('Obj. de Concessão', ''))
            ))
            cad_result = cursor.fetchone()
            if not cad_result:
                continue  # Pular se não encontrar cadastro
            
            cadastro_id = cad_result[0]
            
            rows.append((
                cadastro_id,
                str(row.get('Tipo de Serviço', '')) if pd.notna(row.get('Tipo de Serviço')) else None,
                str(row.get('Fase', '')) if pd.notna(row.get('Fase')) else None,
                str(row.get('Serviço', '')) if pd.notna(row.get('Serviço')) else None,
                str(row.get('Descrição do serviço', '')) if pd.notna(row.get('Descrição do serviço')) else None,
                int(row.get('Prazo início (anos)')) if pd.notna(row.get('Prazo início (anos)')) else None,
                _parse_date(row.get('Data de início')),
                int(row.get('Prazo final (anos)')) if pd.notna(row.get('Prazo final (anos)')) else None,
                _parse_date(row.get('Data final')),
                str(row.get('Fonte (Prazo)', '')) if pd.notna(row.get('Fonte (Prazo)')) else None,
                svc.normalize_percentage(row.get('% de CAPEX para o serviço')) if pd.notna(row.get('% de CAPEX para o serviço')) else None,
                float(row.get('CAPEX do Serviço')) if pd.notna(row.get('CAPEX do Serviço')) else None,
                str(row.get('Fonte (% do CAPEX)', '')) if pd.notna(row.get('Fonte (% do CAPEX)')) else None,
            ))
        
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao converter serviços: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_servicos(df: pd.DataFrame) -> bool:
    """Salva os serviços (Tabela 01) no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # Limpar tabela
        cursor.execute('DELETE FROM acompanhamento')  # CASCADE não funciona em DELETE direto
        cursor.execute('DELETE FROM servico')
        
        # Inserir novos dados
        rows = _df_to_db_servicos(df)
        if rows:
            cursor.executemany('''
                INSERT INTO servico 
                (cadastro_id, tipo_servico, fase, servico, descricao_servico,
                 prazo_inicio_anos, data_inicio, prazo_final_anos, data_final,
                 fonte_prazo, perc_capex, capex_servico, fonte_perc_capex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar serviços: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_servicos() -> pd.DataFrame:
    """Carrega os serviços (Tabela 01) do banco de dados usando a view."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vw_tabela_01_servicos ORDER BY "ID"')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return pd.DataFrame(columns=iox.COLS_01)
        
        # Converter da view para DataFrame
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        
        # Remover coluna ID se existir
        if 'ID' in df.columns:
            df = df.drop('ID', axis=1)
        
        # Garantir todas as colunas
        for col in iox.COLS_01:
            if col not in df.columns:
                df[col] = None
        
        return df[iox.COLS_01]
    except Exception as e:
        print(f"Erro ao carregar serviços: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=iox.COLS_01)

def _df_to_db_acompanhamento(df: pd.DataFrame) -> list:
    """Converte DataFrame da Tabela 02 para formato do banco."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        rows = []
        for _, row in df.iterrows():
            # Buscar servico_id pela chave natural
            cursor.execute('''
                SELECT s.id FROM servico s
                JOIN cadastro c ON c.id = s.cadastro_id
                WHERE c.zona_portuaria = ? 
                  AND c.obj_concessao = ?
                  AND s.tipo_servico = ?
                  AND s.fase = ?
                  AND s.servico = ?
            ''', (
                str(row.get('Zona portuária', '')),
                str(row.get('Obj. de Concessão', '')),
                str(row.get('Tipo de Serviço', '')) if pd.notna(row.get('Tipo de Serviço')) else '',
                str(row.get('Fase', '')) if pd.notna(row.get('Fase')) else '',
                str(row.get('Serviço', '')) if pd.notna(row.get('Serviço')) else '',
            ))
            serv_result = cursor.fetchone()
            if not serv_result:
                continue  # Pular se não encontrar serviço
            
            servico_id = serv_result[0]
            
            rows.append((
                servico_id,
                str(row.get('Descrição', '')) if pd.notna(row.get('Descrição')) else None,
                svc.normalize_percentage(row.get('% executada')) if pd.notna(row.get('% executada')) else None,
                float(row.get('CAPEX (Reaj.)')) if pd.notna(row.get('CAPEX (Reaj.)')) else None,
                float(row.get('Valor executado')) if pd.notna(row.get('Valor executado')) else None,
                _parse_date(row.get('Data da atualização')),
                str(row.get('Responsável', '')) if pd.notna(row.get('Responsável')) else None,
                str(row.get('Cargo', '')) if pd.notna(row.get('Cargo')) else None,
                str(row.get('Setor', '')) if pd.notna(row.get('Setor')) else None,
                str(row.get('Riscos Relacionados (Tipo)', '')) if pd.notna(row.get('Riscos Relacionados (Tipo)')) else None,
                str(row.get('Riscos Relacionados (Descrição)', '')) if pd.notna(row.get('Riscos Relacionados (Descrição)')) else None,
            ))
        
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao converter acompanhamento: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_acompanhamento(df: pd.DataFrame) -> bool:
    """Salva o acompanhamento (Tabela 02) no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # Limpar tabela
        cursor.execute('DELETE FROM acompanhamento')
        
        # Inserir novos dados
        rows = _df_to_db_acompanhamento(df)
        if rows:
            cursor.executemany('''
                INSERT INTO acompanhamento 
                (servico_id, descricao, perc_executada, capex_reaj, valor_executado,
                 data_atualizacao, responsavel, cargo, setor, risco_tipo, risco_descricao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar acompanhamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_acompanhamento() -> pd.DataFrame:
    """Carrega o acompanhamento (Tabela 02) do banco de dados usando a view."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vw_tabela_02_acompanhamento ORDER BY "ID"')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return pd.DataFrame(columns=iox.COLS_02)
        
        # Converter da view para DataFrame
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        
        # Remover coluna ID se existir
        if 'ID' in df.columns:
            df = df.drop('ID', axis=1)
        
        # Garantir todas as colunas
        for col in iox.COLS_02:
            if col not in df.columns:
                df[col] = None
        
        return df[iox.COLS_02]
    except Exception as e:
        print(f"Erro ao carregar acompanhamento: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=iox.COLS_02)

def save_all(df00: pd.DataFrame, df01: pd.DataFrame, df02: pd.DataFrame) -> bool:
    """Salva todas as tabelas no banco de dados (na ordem correta devido a FK)."""
    success = True
    success = save_cadastro(df00) and success
    success = save_servicos(df01) and success
    success = save_acompanhamento(df02) and success
    return success

def load_all() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega todas as tabelas do banco de dados."""
    return load_cadastro(), load_servicos(), load_acompanhamento()
