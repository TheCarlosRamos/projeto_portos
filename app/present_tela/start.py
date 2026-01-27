#!/usr/bin/env python3
"""
Script para iniciar a aplicação completa de gestão portuária
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import flask_cors
        import pandas
        print("✅ Dependências já instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Instalando dependências...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False

def start_server():
    """Inicia o servidor Flask"""
    try:
        print("🚀 Iniciando servidor Flask...")
        print("📍 Acesse: http://localhost:5000")
        print("📊 API: http://localhost:5000/api/projects")
        print("🔄 Para parar: Ctrl+C")
        
        # Importa e inicia a aplicação
        import app
        app.app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    print("🏗️  Sistema de Gestão de Concessões Portuárias")
    print("=" * 50)
    
    # Verifica dependências
    if not check_requirements():
        sys.exit(1)
    
    # Inicia servidor
    start_server()
