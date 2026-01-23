"""
Script ETL para processar planilhas Excel de concessões portuárias.
Estrutura baseada na especificação técnica real do sistema.
"""
import pandas as pd
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from pathlib import Path
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models_portuarios import (
    Base, ZonaPortuaria, Concessao, TipoServico, 
    Servico, Acompanhamento, Risco, AcompanhamentoRisco
)

# Mapeamento das abas da planilha
MAPEAMENTO_ABAS = {
    "tabela 0 - cadastro": "cadastro",
    "tabela 01 - serviços": "servicos", 
    "tabela 02: acompanhamento": "acompanhamento",
    "tabela 0 - cadastro": "cadastro",
    "tabela 01 - serviços": "servicos",
    "tabela 02: acompanhamento": "acompanhamento",
    "cadastro": "cadastro",
    "serviços": "servicos",
    "acompanhamento": "acompanhamento"
}

# Normalização de colunas por aba
COLUNAS_CADASTRO = {
    "zona portuária": "zona_portuaria",
    "zona_portuaria": "zona_portuaria", 
    "uf": "uf",
    "obj. de concessão": "objeto_concessao",
    "objeto_de_concessao": "objeto_concessao",
    "objeto de concessão": "objeto_concessao",
    "tipo": "tipo",
    "capex total": "capex_total",
    "capex_total": "capex_total",
    "data de assinatura do contrato": "data_assinatura",
    "data_assinatura": "data_assinatura",
    "descrição": "descricao",
    "descricao": "descricao",
    "coordenada e (utm)": "coord_e",
    "coord_e": "coord_e",
    "coordenada s (utm)": "coord_s",
    "coord_s": "coord_s",
    "fuso": "fuso"
}

COLUNAS_SERVICOS = {
    "obj. de concessão": "objeto_concessao", 
    "objeto_de_concessao": "objeto_concessao",
    "objeto de concessão": "objeto_concessao",
    "tipo de serviço": "tipo_servico",
    "tipo_servico": "tipo_servico",
    "fase": "fase",
    "serviço": "servico",
    "servico": "servico",
    "descrição do serviço": "descricao",
    "descricao_do_servico": "descricao",
    "prazo início (anos)": "prazo_inicio_anos",
    "prazo_inicio_anos": "prazo_inicio_anos",
    "data de início": "data_inicio",
    "data_inicio": "data_inicio",
    "prazo final (anos)": "prazo_final_anos",
    "prazo_final_anos": "prazo_final_anos",
    "data final": "data_final",
    "data_final": "data_final",
    "fonte (prazo)": "fonte_prazo",
    "fonte_prazo": "fonte_prazo",
    "% de capex para o serviço": "percentual_capex",
    "percentual_capex": "percentual_capex",
    "capex do serviço": "capex_servico",
    "capex_servico": "capex_servico",
    "fonte (% do capex)": "fonte_percentual",
    "fonte_percentual": "fonte_percentual"
}

COLUNAS_ACOMPANHAMENTO = {
    "zona portuária": "zona_portuaria",
    "zona_portuaria": "zona_portuaria",
    "uf": "uf",
    "obj. de concessão": "objeto_concessao", 
    "objeto_de_concessao": "objeto_concessao",
    "objeto de concessão": "objeto_concessao",
    "tipo de serviço": "tipo_servico",
    "tipo_servico": "tipo_servico",
    "fase": "fase",
    "serviço": "servico",
    "servico": "servico",
    "descrição": "descricao",
    "% executada": "percentual_executado",
    "percentual_executado": "percentual_executado",
    "capex (reaj.)": "capex_reajustado",
    "capex_reajustado": "capex_reajustado",
    "valor executado": "valor_executado",
    "valor_executado": "valor_executado",
    "data da atualização": "data_atualizacao",
    "data_atualizacao": "data_atualizacao",
    "responsável": "responsavel",
    "responsavel": "responsavel",
    "cargo": "cargo",
    "setor": "setor",
    "riscos relacionados (tipo)": "riscos_tipo",
    "riscos_tipo": "riscos_tipo",
    "riscos relacionados (descrição)": "riscos_descricao",
    "riscos_descricao": "riscos_descricao"
}

def normalizar_nome_coluna(coluna: str, aba: str) -> str:
    """Normaliza o nome da coluna conforme a aba"""
    coluna = coluna.lower().strip()
    coluna = re.sub(r'\s+', '_', coluna)
    coluna = coluna.replace("º", "")
    coluna = coluna.replace("ç", "c")
    coluna = coluna.replace("ã", "a")
    coluna = coluna.replace("á", "a")
    coluna = coluna.replace("é", "e")
    coluna = coluna.replace("í", "i")
    coluna = coluna.replace("ó", "o")
    coluna = coluna.replace("ú", "u")
    
    # Mapear para nomes padronizados por aba
    if aba == "cadastro":
        mapeamento = COLUNAS_CADASTRO
    elif aba == "servicos":
        mapeamento = COLUNAS_SERVICOS
    elif aba == "acompanhamento":
        mapeamento = COLUNAS_ACOMPANHAMENTO
    else:
        return coluna
    
    return mapeamento.get(coluna, coluna)

def processar_data(data) -> Optional[str]:
    """Processa data de diferentes formatos"""
    if pd.isna(data) or data == "":
        return None
    
    try:
        if isinstance(data, datetime):
            return data.strftime("%Y-%m-%d")
        
        data_str = str(data).strip()
        # Formato brasileiro
        if "/" in data_str:
            partes = data_str.split("/")
            if len(partes) == 3:
                dia, mes, ano = partes
                return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
        
        # Formato ISO
        return pd.to_datetime(data_str).strftime("%Y-%m-%d")
    except:
        return None

def normalizar_valor_numerico(valor) -> Decimal:
    """Normaliza valores numéricos e monetários"""
    if pd.isna(valor) or valor == "" or valor == "nan":
        return Decimal("0")
    
    try:
        valor_str = str(valor).strip()
        
        # Se já é Decimal, retornar
        if isinstance(valor, Decimal):
            return valor
        
        # Remover símbolos monetários e espaços
        valor_str = re.sub(r'[R$\s]', '', valor_str)
        valor_str = valor_str.replace(".", "").replace(",", ".")
        
        # Se está vazio após limpeza
        if not valor_str or valor_str == "":
            return Decimal("0")
        
        # Converter para Decimal
        return Decimal(valor_str)
    except (ValueError, TypeError, InvalidOperation):
        print(f"Erro ao converter valor '{valor}' para Decimal: {str(e)}")
        return Decimal("0")

def criar_ou_obter_zona_portuaria(db: Session, nome: str, uf: str) -> ZonaPortuaria:
    """Cria ou retorna uma zona portuária existente"""
    zona = db.query(ZonaPortuaria).filter(
        ZonaPortuaria.nome == nome.strip(),
        ZonaPortuaria.uf == uf.strip()
    ).first()
    
    if not zona:
        zona = ZonaPortuaria(
            nome=nome.strip(),
            uf=uf.strip()
        )
        db.add(zona)
        db.commit()
        db.refresh(zona)
    
    return zona

def criar_ou_obter_tipo_servico(db: Session, nome: str) -> TipoServico:
    """Cria ou retorna um tipo de serviço existente"""
    tipo = db.query(TipoServico).filter(
        TipoServico.nome == nome.strip()
    ).first()
    
    if not tipo:
        tipo = TipoServico(nome=nome.strip())
        db.add(tipo)
        db.commit()
        db.refresh(tipo)
    
    return tipo

def criar_ou_obter_risco(db: Session, tipo: str, descricao: str = None) -> Risco:
    """Cria ou retorna um risco existente"""
    risco = db.query(Risco).filter(
        Risco.tipo == tipo.strip()
    ).first()
    
    if not risco:
        risco = Risco(
            tipo=tipo.strip(),
            descricao=descricao.strip() if descricao else None
        )
        db.add(risco)
        db.commit()
        db.refresh(risco)
    
    return risco

def identificar_concessao(db: Session, zona_portuaria: str, uf: str, objeto_concessao: str) -> Optional[Concessao]:
    """Identifica uma concessão existente"""
    return db.query(Concessao).join(ZonaPortuaria).filter(
        ZonaPortuaria.nome == zona_portuaria.strip(),
        ZonaPortuaria.uf == uf.strip(),
        Concessao.objeto_concessao == objeto_concessao.strip()
    ).first()

def identificar_servico(db: Session, zona_portuaria: str, uf: str, objeto_concessao: str, nome_servico: str) -> Optional[Servico]:
    """Identifica um serviço existente"""
    return db.query(Servico).join(Concessao).join(ZonaPortuaria).filter(
        ZonaPortuaria.nome == zona_portuaria.strip(),
        ZonaPortuaria.uf == uf.strip(),
        Concessao.objeto_concessao == objeto_concessao.strip(),
        Servico.nome == nome_servico.strip()
    ).first()

def processar_aba_cadastro(df: pd.DataFrame, db: Session) -> Dict[str, int]:
    """Processa a aba de cadastro (concessões)"""
    print(f"  [CADASTRO] Processando aba de Cadastro - {len(df)} linhas")
    
    processados = 0
    erros = 0
    
    for idx, row in df.iterrows():
        try:
            zona_portuaria = str(row.get("zona_portuaria", "")).strip()
            uf = str(row.get("uf", "")).strip()
            objeto_concessao = str(row.get("objeto_concessao", "")).strip()
            
            if not all([zona_portuaria, uf, objeto_concessao]) or zona_portuaria == "nan":
                continue
            
            # Verificar se já existe
            existente = identificar_concessao(db, zona_portuaria, uf, objeto_concessao)
            if existente:
                print(f"    [INFO] Concessão já existe: {zona_portuaria} - {uf} - {objeto_concessao}")
                processados += 1
                continue
            
            # Criar zona portuária
            zona = criar_ou_obter_zona_portuaria(db, zona_portuaria, uf)
            
            # Criar concessão
            concessao_data = {
                "zona_portuaria_id": zona.id,
                "objeto_concessao": objeto_concessao,
                "tipo": str(row.get("tipo", "")).strip() or "Concessão",
                "capex_total": normalizar_valor_numerico(row.get("capex_total")),
                "data_assinatura": processar_data(row.get("data_assinatura")),
                "descricao": str(row.get("descricao", "")).strip() or None,
                "coord_e": normalizar_valor_numerico(row.get("coord_e")),
                "coord_s": normalizar_valor_numerico(row.get("coord_s")),
                "fuso": int(row.get("fuso")) if pd.notna(row.get("fuso")) else None,
            }
            
            # Validar tipo
            tipo = concessao_data["tipo"]
            if tipo not in ["Concessão", "Arrendamento", "Autorização"]:
                print(f"    [WARN] Tipo inválido: {tipo}. Usando 'Concessão' como padrão.")
                concessao_data["tipo"] = "Concessão"
            
            # Validar CAPEX
            if concessao_data["capex_total"] <= 0:
                print(f"    [WARN] CAPEX inválido: {concessao_data['capex_total']}. Pulando linha.")
                continue
            
            concessao = Concessao(**concessao_data)
            db.add(concessao)
            db.commit()
            db.refresh(concessao)
            
            print(f"    [OK] Concessão criada: {zona_portuaria} - {uf} - {objeto_concessao}")
            processados += 1
            
        except Exception as e:
            print(f"    [ERRO] Erro ao processar linha {idx + 1}: {e}")
            print(f"       Dados: {dict(row)}")
            erros += 1
            db.rollback()
            continue
    
    return {"processados": processados, "erros": erros}

def processar_aba_servicos(df: pd.DataFrame, db: Session) -> Dict[str, int]:
    """Processa a aba de serviços"""
    print(f"  [SERVICOS] Processando aba de Serviços - {len(df)} linhas")
    
    processados = 0
    erros = 0
    
    for idx, row in df.iterrows():
        try:
            zona_portuaria = str(row.get("zona_portuaria", "")).strip()
            uf = str(row.get("uf", "")).strip()
            objeto_concessao = str(row.get("objeto_concessao", "")).strip()
            tipo_servico = str(row.get("tipo_servico", "")).strip()
            fase = str(row.get("fase", "")).strip()
            nome_servico = str(row.get("servico", "")).strip()
            
            if not all([zona_portuaria, uf, objeto_concessao, tipo_servico, fase, nome_servico]):
                continue
            
            # Verificar se já existe
            existente = identificar_servico(db, zona_portuaria, uf, objeto_concessao, nome_servico)
            if existente:
                print(f"    [INFO] Serviço já existe: {zona_portuaria} - {uf} - {objeto_concessao} - {nome_servico}")
                processados += 1
                continue
            
            # Obter concessão
            concessao = identificar_concessao(db, zona_portuaria, uf, objeto_concessao)
            if not concessao:
                print(f"    [WARN] Concessão não encontrada: {zona_portuaria} - {uf} - {objeto_concessao}")
                erros += 1
                continue
            
            # Obter ou criar tipo de serviço
            tipo_servico_obj = criar_ou_obter_tipo_servico(db, tipo_servico)
            
            # Criar serviço
            servico_data = {
                "concessao_id": concessao.id,
                "tipo_servico_id": tipo_servico_obj.id,
                "fase": fase,
                "nome": nome_servico,
                "descricao": str(row.get("descricao", "")).strip() or None,
                "prazo_inicio_anos": int(row.get("prazo_inicio_anos")) if pd.notna(row.get("prazo_inicio_anos")) else None,
                "data_inicio": processar_data(row.get("data_inicio")),
                "prazo_final_anos": int(row.get("prazo_final_anos")) if pd.notna(row.get("prazo_final_anos")) else None,
                "data_final": processar_data(row.get("data_final")),
                "fonte_prazo": str(row.get("fonte_prazo", "")).strip() or None,
                "percentual_capex": float(row.get("percentual_capex")) if pd.notna(row.get("percentual_capex")) else 0,
                "capex_servico": normalizar_valor_numerico(row.get("capex_servico")),
                "fonte_percentual": str(row.get("fonte_percentual", "")).strip() or None,
            }
            
            servico = Servico(**servico_data)
            db.add(servico)
            db.commit()
            db.refresh(servico)
            
            print(f"    [OK] Serviço criado: {zona_portuaria} - {uf} - {objeto_concessao} - {nome_servico}")
            processados += 1
            
        except Exception as e:
            print(f"    [ERRO] Erro ao processar linha {idx + 1}: {e}")
            erros += 1
            db.rollback()
            continue
    
    return {"processados": processados, "erros": erros}

def processar_aba_acompanhamento(df: pd.DataFrame, db: Session) -> Dict[str, int]:
    """Processa a aba de acompanhamento"""
    print(f"  [ACOMPANHAMENTO] Processando aba de Acompanhamento - {len(df)} linhas")
    
    processados = 0
    erros = 0
    
    for idx, row in df.iterrows():
        try:
            objeto_concessao = str(row.get("objeto_concessao", "")).strip()
            nome_servico = str(row.get("servico", "")).strip()
            
            if not all([objeto_concessao, nome_servico]) or objeto_concessao == "nan":
                continue
            
            # Buscar serviço
            servico = db.query(Servico).join(Concessao).filter(
                Concessao.objeto_concessao == objeto_concessao.strip(),
                Servico.nome == nome_servico.strip()
            ).first()
            
            if not servico:
                print(f"    [WARN] Serviço não encontrado: {nome_servico}")
                erros += 1
                continue
            
            # Criar acompanhamento
            acompanhamento_data = {
                "servico_id": servico.id,
                "percentual_executado": normalizar_valor_numerico(row.get("percentual_executado")),
                "capex_reajustado": normalizar_valor_numerico(row.get("capex_reajustado")),
                "valor_executado": normalizar_valor_numerico(row.get("valor_executado")),
                "data_atualizacao": processar_data(row.get("data_atualizacao")),
                "responsavel": str(row.get("responsavel", "")).strip(),
                "cargo": str(row.get("cargo", "")).strip(),
                "setor": str(row.get("setor", "")).strip(),
            }
            
            acompanhamento = Acompanhamento(**acompanhamento_data)
            db.add(acompanhamento)
            db.commit()
            db.refresh(acompanhamento)
            
            # Processar riscos relacionados
            riscos_tipo = str(row.get("riscos_tipo", "")).strip()
            riscos_descricao = str(row.get("riscos_descricao", "")).strip()
            
            if riscos_tipo and riscos_tipo != "nan":
                risco = criar_ou_obter_risco(db, riscos_tipo, riscos_descricao)
                associacao = AcompanhamentoRisco(
                    acompanhamento_id=acompanhamento.id,
                    risco_id=risco.id
                )
                db.add(associacao)
                db.commit()
            
            print(f"    [OK] Acompanhamento criado: {nome_servico}")
            processados += 1
            
        except Exception as e:
            print(f"    [ERRO] Erro ao processar linha {idx + 1}: {e}")
            erros += 1
            db.rollback()
            continue
    
    return {"processados": processados, "erros": erros}

def processar_planilha(arquivo: str, db: Session):
    """Processa uma planilha Excel de concessões portuárias"""
    print(f"[ETL] Iniciando processamento do arquivo: {arquivo}")
    
    try:
        excel_file = pd.ExcelFile(arquivo)
        print(f"[ETL] Abas encontradas: {list(excel_file.sheet_names)}")
    except Exception as e:
        print(f"[ETL] Erro ao ler arquivo: {e}")
        return {"processados": 0, "erros": 1}
    
    total_processados = 0
    total_erros = 0
    
    for nome_aba in excel_file.sheet_names:
        print(f"\nProcessando aba: {nome_aba}")
        
        # Identificar tipo da aba
        tipo_aba = MAPEAMENTO_ABAS.get(nome_aba.strip().lower(), nome_aba.strip().lower())
        
        if not tipo_aba:
            print(f"  [WARN] Aba não reconhecida: '{nome_aba}'. Pulando...")
            continue
        
        # Ler dados da aba
        try:
            df = pd.read_excel(excel_file, sheet_name=nome_aba)
            print(f"  [INFO] Linhas na aba: {len(df)}")
        except Exception as e:
            print(f"  [ERRO] Erro ao ler aba: {e}")
            total_erros += 1
            continue
        
        if df.empty:
            print(f"  [WARN] Aba vazia. Pulando...")
            continue
        
        # Normalizar nomes de colunas
        df.columns = [normalizar_nome_coluna(col, tipo_aba) for col in df.columns]
        print(f"  [INFO] Colunas: {', '.join(df.columns[:10])}")
        
        # Processar conforme tipo da aba
        if tipo_aba == "cadastro":
            resultado = processar_aba_cadastro(df, db)
        elif tipo_aba == "servicos":
            resultado = processar_aba_servicos(df, db)
        elif tipo_aba == "acompanhamento":
            resultado = processar_aba_acompanhamento(df, db)
        else:
            print(f"  [WARN] Tipo de aba não implementado: {tipo_aba}")
            continue
        
        total_processados += resultado["processados"]
        total_erros += resultado["erros"]
    
    print(f"\n{'='*50}")
    print(f"[OK] Processamento concluído!")
    print(f"   Total processados: {total_processados}")
    print(f"   Total erros: {total_erros}")
    print(f"{'='*50}")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python process_excel_portuarios.py <caminho_para_planilha.xlsx>")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    
    if not os.path.exists(arquivo):
        print(f"[ERRO] Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    
    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    # Conectar ao banco
    db = SessionLocal()
    
    try:
        processar_planilha(arquivo, db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
