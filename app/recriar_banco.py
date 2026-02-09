#!/usr/bin/env python3
"""Script para recriar o banco de dados com o novo schema"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import db

if __name__ == "__main__":
    print("🔄 Recriando banco de dados com novo schema...")
    
    # Remover arquivo do banco se existir
    if db.DB_PATH.exists():
        try:
            os.remove(db.DB_PATH)
            print("✅ Arquivo do banco removido")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
            sys.exit(1)
    
    # Recriar banco com novo schema
    try:
        db.init_db()
        print("✅ Banco de dados recriado com sucesso!")
        print("📊 Novas colunas disponíveis:")
        print("   - Tabela 00: Setor, Local, UF, Obj. de Concessão, Tipo, CAPEX Total, Data de assinatura do contrato, Descrição, Latitude, Longitude")
        print("   - Tabela 01: Setor, Local, UF, Obj. de Concessão, Tipo de Serviço, Fase, Serviço, Descrição do serviço, Prazo início (anos), Data de início, Prazo final (anos), Data final, Fonte (Prazo), % de CAPEX para o serviço, CAPEX do Serviço, Fonte (% do CAPEX)")
        print("   - Tabela 02: Setor, Local, UF, Obj. de Concessão, Tipo de Serviço, Fase, Serviço, Descrição, % executada, CAPEX (Reaj.), Valor executado, Data da atualização, Responsável, Cargo, Setor2, Riscos Relacionados (Tipo), Riscos Relacionados (Descrição)")
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
