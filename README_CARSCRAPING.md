# Car Scraping Project

## 📋 Sobre

Este projeto é uma cópia independente do **RentalPriceTrackerPerDay**, criado em 9 de Janeiro de 2026.

Contém todo o sistema de scraping de carros de aluguer da Carjet e outros fornecedores.

## 🚀 Características

- ✅ Scraping otimizado da Carjet (~25 segundos para 1.401 carros)
- ✅ Suporte para múltiplos fornecedores (Discover Cars, etc.)
- ✅ Sistema de categorização automática de carros
- ✅ Detecção de transmissão (Manual/Automática)
- ✅ Interface web completa
- ✅ API REST para integração
- ✅ Modo visual e headless

## 📊 Performance

- **Tempo de scraping:** ~25 segundos
- **Carros encontrados:** 1.401 (Faro Airport, 7 dias)
- **Otimização:** 95% mais rápido que versão anterior

## 🛠️ Tecnologias

- Python 3.9+
- FastAPI / Starlette
- Selenium WebDriver
- BeautifulSoup4
- SQLite / PostgreSQL

## 📦 Instalação

```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar servidor
python main.py
```

## 🌐 Uso

Servidor local: http://localhost:8000

### API Endpoints

- `GET /api/vehicles/search` - Buscar carros
- `POST /api/discovercars-search` - Scraping Discover Cars
- `GET /api/vehicles/{name}/photo` - Foto do veículo

## 📝 Notas

- Projeto independente do RentalPriceTrackerPerDay
- Sem histórico Git (repositório limpo)
- Ambiente virtual removido (criar novo)
- Backups removidos

## 📅 Criado

9 de Janeiro de 2026

---

**Projeto original:** RentalPriceTrackerPerDay  
**Novo projeto:** CarScraping
