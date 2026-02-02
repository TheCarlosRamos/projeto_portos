# 🚢 Gestão de Concessões Portuárias - Versão Estática

## 🌐 Demonstração Online

**GitHub Pages**: https://thecarlosramos.github.io/projeto_portos/

## 📋 Sobre

Versão estática do sistema de gestão de concessões portuárias, otimizada para GitHub Pages. Todos os dados são embutidos diretamente no HTML, garantindo carregamento instantâneo e funcionamento offline.

## ✅ Vantagens da Versão Estática

- 🚀 **Carregamento instantâneo** - Sem chamadas de API
- 📱 **Funciona offline** - Dados embutidos no HTML
- 🔒 **Seguro** - Sem backend para expor
- 💰 **Gratuito** - Hospedado no GitHub Pages
- ⚡ **Rápido** - CDN global do GitHub
- 📊 **Completo** - Todos os 6 projetos com dados completos

## 🗺️ Funcionalidades

- ✅ **Mapa interativo** com marcadores para todos os projetos
- ✅ **Cards informativos** com UF, Obj. de Concessão e Descrição
- ✅ **Filtros** por UF, tipo, status
- ✅ **Modal detalhado** para cada projeto
- ✅ **Responsivo** - Funciona em desktop e mobile
- ✅ **Progresso visual** dos investimentos

## 📁 Estrutura

```
projeto_portos/
├── index.html              # HTML estático principal (gerado automaticamente)
├── app/present_tela/
│   ├── portos.html         # Template original
│   ├── planilha_portos.json # Dados fonte
│   └── gerar_html_estatico.py # Script gerador
└── .github/workflows/
    └── github-pages.yml    # CI/CD para deploy automático
```

## 🔄 Atualização dos Dados

1. **Atualize** o arquivo `app/present_tela/planilha_portos.json`
2. **Commit** as mudanças: `git add . && git commit -m "Atualizar dados"`
3. **Push**: `git push origin main`
4. **Pronto!** O GitHub Pages atualiza automaticamente

## 🚀 Deploy Automático

O site é atualizado automaticamente sempre que há um push na branch `main` através do GitHub Actions.

## 📊 Projetos Incluídos

- **TECON 10** - Porto de Santos (SP)
- **Hidrovia do Paraguai** - MT/MS
- **TPM Macéio** - Porto de Maceió (AL)
- **RDJ07** - Porto do Rio de Janeiro (RJ)
- E mais...

## 🛠️ Tecnologias

- **HTML5** - Estrutura semântica
- **Tailwind CSS** - Estilos responsivos
- **JavaScript** - Interações e mapa
- **Leaflet** - Mapa interativo
- **Chart.js** - Gráficos
- **GitHub Pages** - Hospedagem

## 📱 Acesso

- **Desktop**: https://thecarlosramos.github.io/projeto_portos/
- **Mobile**: Mesma URL, responsiva
- **Offline**: Salve a página para uso offline

---

🎉 **Desenvolvido com ❤️ para gestão portuária brasileira**
