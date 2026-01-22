"""
Script ETL para processar planilhas Excel e importar dados para o banco.
"""
import pandas as pd
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Processo, Situacao, Meta, Indicador
from schemas import ProcessoCreate, SituacaoCreate

# Normalização de nomes de colunas
COLUNAS_NORMALIZADAS = {
    "nº processo": "numero_processo",
    "numero processo": "numero_processo",
    "numero_processo": "numero_processo",
    "n processo": "numero_processo",
    "data do protocolo": "data_protocolo",
    "data_protocolo": "data_protocolo",
    "data protocolo": "data_protocolo",
    "licenca": "licenca",
    "licença": "licenca",
    "situação geral": "situacao_geral",
    "situacao geral": "situacao_geral",
    "situacao_geral": "situacao_geral",
}

# Normalização de situações
NORMALIZACAO_SITUACOES = {
    "pedido revisão de projeto em fase de obra - rpfo": "OUTROS",
    "interferência total": "INTERFERÊNCIA TOTAL",
    "interferencia total": "INTERFERÊNCIA TOTAL",
    "em execução": "EM EXECUÇÃO",
    "em execucao": "EM EXECUÇÃO",
    "concluído": "CONCLUÍDO",
    "concluido": "CONCLUÍDO",
    "licenciado": "LICENCIADO",
    "em análise": "EM ANÁLISE",
    "em analise": "EM ANÁLISE",
}

# Colunas de indicadores esperadas
COLUNAS_INDICADORES = [
    "tipo_intervencao",
    "financeiro_planejado",
    "financeiro_executado",
    "km_planejado",
    "km_executado",
    "extensao_km",
]


def normalizar_nome_coluna(coluna: str) -> str:
    """Normaliza o nome da coluna para snake_case"""
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
    
    # Mapear para nomes padronizados
    if coluna in COLUNAS_NORMALIZADAS:
        return COLUNAS_NORMALIZADAS[coluna]
    
    return coluna


def normalizar_situacao(situacao: str) -> str:
    """Normaliza o valor da situação"""
    if pd.isna(situacao) or situacao == "":
        return "NÃO INFORMADO"
    
    situacao_str = str(situacao).lower().strip()
    
    # Buscar normalização
    for key, value in NORMALIZACAO_SITUACOES.items():
        if key in situacao_str:
            return value
    
    return situacao_str.upper()


def normalizar_valor_numerico(valor) -> Decimal:
    """Normaliza valores numéricos"""
    if pd.isna(valor) or valor == "":
        return Decimal("0")
    
    try:
        # Converter para string e remover formatação
        valor_str = str(valor).replace(",", ".").replace(" ", "")
        return Decimal(valor_str)
    except:
        return Decimal("0")


def processar_data(data) -> Optional[str]:
    """Processa data de diferentes formatos"""
    if pd.isna(data):
        return None
    
    try:
        # Tentar parsear como datetime
        if isinstance(data, datetime):
            return data.strftime("%Y-%m-%d")
        
        # Tentar parsear string
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


def extrair_ano_da_aba(nome_aba: str) -> Optional[int]:
    """Extrai o ano do nome da aba"""
    match = re.search(r'\b(20\d{2})\b', nome_aba)
    if match:
        return int(match.group(1))
    return None


def criar_ou_obter_situacao(db: Session, nome_situacao: str) -> Situacao:
    """Cria ou retorna uma situação existente"""
    situacao_normalizada = normalizar_situacao(nome_situacao)
    
    situacao = db.query(Situacao).filter(
        Situacao.nome == situacao_normalizada
    ).first()
    
    if not situacao:
        situacao = Situacao(nome=situacao_normalizada)
        db.add(situacao)
        db.commit()
        db.refresh(situacao)
    
    return situacao


def processar_planilha(arquivo: str, db: Session):
    """Processa uma planilha Excel e importa os dados"""
    print(f"Processando arquivo: {arquivo}")
    
    # Ler todas as abas
    try:
        excel_file = pd.ExcelFile(arquivo)
        print(f"Abas encontradas: {list(excel_file.sheet_names)}")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    total_processados = 0
    total_erros = 0
    
    for nome_aba in excel_file.sheet_names:
        print(f"\nProcessando aba: {nome_aba}")
        
        # Extrair ano da aba
        ano = extrair_ano_da_aba(nome_aba)
        if not ano:
            print(f"  ⚠️  Não foi possível extrair o ano da aba '{nome_aba}'. Pulando...")
            continue
        
        print(f"  📅 Ano identificado: {ano}")
        
        # Ler dados da aba
        try:
            df = pd.read_excel(excel_file, sheet_name=nome_aba)
            print(f"  📊 Linhas na aba: {len(df)}")
        except Exception as e:
            print(f"  ❌ Erro ao ler aba: {e}")
            total_erros += 1
            continue
        
        if df.empty:
            print(f"  ⚠️  Aba vazia. Pulando...")
            continue
        
        # Normalizar nomes de colunas
        df.columns = [normalizar_nome_coluna(col) for col in df.columns]
        print(f"  📋 Colunas: {', '.join(df.columns[:10])}")
        
        # Processar cada linha
        for idx, row in df.iterrows():
            try:
                # Criar ou obter processo
                numero_processo = str(row.get("numero_processo", "")).strip()
                if not numero_processo or numero_processo == "nan":
                    continue
                
                # Verificar se processo já existe
                processo = db.query(Processo).filter(
                    Processo.numero_processo == numero_processo
                ).first()
                
                if not processo:
                    # Criar novo processo
                    situacao_nome = row.get("situacao_geral", "")
                    situacao = criar_ou_obter_situacao(db, situacao_nome)
                    
                    processo_data = {
                        "numero_processo": numero_processo,
                        "data_protocolo": processar_data(row.get("data_protocolo")),
                        "licenca": str(row.get("licenca", "")).strip() or None,
                        "situacao_geral_id": situacao.id,
                    }
                    
                    processo = Processo(**processo_data)
                    db.add(processo)
                    db.commit()
                    db.refresh(processo)
                    print(f"  ✅ Processo criado: {numero_processo}")
                else:
                    print(f"  ℹ️  Processo já existe: {numero_processo}")
                
                # Criar ou obter meta
                meta = db.query(Meta).filter(
                    Meta.processo_id == processo.id,
                    Meta.ano == ano
                ).first()
                
                if not meta:
                    meta = Meta(processo_id=processo.id, ano=ano)
                    db.add(meta)
                    db.commit()
                    db.refresh(meta)
                    print(f"    ✅ Meta criada: Ano {ano}")
                
                # Criar indicadores (se houver colunas relevantes)
                # Buscar colunas que podem ser indicadores
                for col in df.columns:
                    if any(keyword in col for keyword in ["financeiro", "km", "extensao", "intervencao"]):
                        # Aqui você pode adicionar lógica específica para processar indicadores
                        # Por enquanto, vamos criar um indicador genérico se necessário
                        pass
                
                total_processados += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao processar linha {idx + 1}: {e}")
                total_erros += 1
                db.rollback()
                continue
    
    print(f"\n{'='*50}")
    print(f"✅ Processamento concluído!")
    print(f"   Total processados: {total_processados}")
    print(f"   Total erros: {total_erros}")
    print(f"{'='*50}")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python process_excel.py <caminho_para_planilha.xlsx>")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
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
