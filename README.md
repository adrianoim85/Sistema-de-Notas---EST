# Sistema de Notas — Portal do Aluno (Flask)

Este repositório está pronto para **deploy na Railway** (camada gratuita).

## Estrutura
- `app.py`: aplicação Flask (expondo `app`)
- `requirements.txt`: dependências (Flask, gunicorn, pandas, openpyxl)
- `templates/` e `static/`: UI do portal
- `data/Controle de Notas 1 BIM.xlsx`: planilha com as notas

## Executar localmente
```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
# macOS/Linux
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```
Abra http://localhost:5000

## Deploy na Railway
1. Crie um projeto **New Project → Deploy from GitHub** e selecione este repo.
2. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. Em **Variables/Secrets**, crie `FLASK_SECRET_KEY` com um valor aleatório longo.
4. Aguarde o build e acesse a **URL pública** gerada.

> Observação: Em produção, usamos **Gunicorn** como servidor WSGI (recomendação do Flask) e a Railway injeta a porta via `PORT` automaticamente.
