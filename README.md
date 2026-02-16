# Portal do Aluno — Consulta de Notas

Este é um pequeno portal (Flask) para os alunos consultarem **apenas** as suas notas, usando como base a planilha Excel **Controle de Notas 1 BIM.xlsx**.

## Como rodar localmente
1. Tenha o **Python 3.10+** instalado.
2. Em um terminal, dentro da pasta do projeto, execute:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt  # (Windows: .venv\Scripts\pip install -r requirements.txt)
   .venv/bin/python app.py                    # (Windows: .venv\Scripts\python app.py)
   ```
3. Acesse http://localhost:5000 no navegador.

## Como atualizar as notas
- Substitua o arquivo em `aluno_notas_portal/data/Controle de Notas 1 BIM.xlsx` pela nova planilha.
- (Opcional) Acesse `/recarregar` para recarregar os dados sem reiniciar o servidor.

## Credenciais
- **Login:** nome completo do aluno (como na planilha). Não diferencia acentos/maiúsculas.
- **Senha:** código do aluno (coluna **CÓDIGO** da planilha).

## Observações
- Este projeto faz o *parse* automático das quatro planilhas (9B, 9C, 1A, 1B, 1C). Ele localiza a linha de cabeçalho onde constam as colunas **CÓDIGO** e **ALUNO** e lê tudo que estiver abaixo, ignorando a seção "Anotações" se existir.
- Não há criação de contas; a autenticação compara diretamente o nome completo e o código presentes na planilha.
- Por ser um app simples, não use em ambiente público sem proteção adicional (HTTPS, senha de admin, rate limit, logs, etc.).
