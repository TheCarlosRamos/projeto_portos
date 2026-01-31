"""
Entry point para Vercel Serverless Functions
"""
from main import app

# Vercel espera uma variável chamada 'app' ou 'handler'
handler = app
