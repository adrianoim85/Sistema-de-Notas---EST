import os
import unicodedata
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd

# ---------- Config ----------
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'mude-esta-chave-para-uma-secreta')
EXCEL_PATH = os.environ.get('EXCEL_PATH', os.path.join(os.path.dirname(__file__), 'data', 'Controle de Notas 1 BIM.xlsx'))

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------- Utilidades ----------
def strip_accents(s: str):
    if not isinstance(s, str):
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').strip()

def norm_name(s: str):
    return ' '.join(strip_accents(s).upper().split())

# Detect header row by the presence of both 'Código' and 'ALUNO'

def parse_sheet(df_raw: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    # Find header row index
    header_idx = None
    for i in range(min(len(df_raw), 50)):  # only scan top 50 rows
        row_values = df_raw.iloc[i].astype(str).str.strip().tolist()
        if any(v.lower() == 'código' or v.lower() == 'codigo' for v in row_values) and any(v.lower() == 'aluno' for v in row_values):
            header_idx = i
            break
    if header_idx is None:
        return pd.DataFrame()

    header = df_raw.iloc[header_idx].astype(str).str.strip().tolist()
    df = df_raw.iloc[header_idx+1:].copy()
    df.columns = header[:len(df.columns)]

    # Drop rows after 'Anotações' marker if present
    if 'Anotações' in df.columns:
        # Sometimes 'Anotações' appears as a column header; if so, we just drop that column later
        pass
    # Also handle row label 'Anotações' in first column
    for idx in df.index:
        first_val = str(df.loc[idx].iloc[0]).strip()
        if first_val.lower() in ('anotações','anotacoes'):
            # slice up to the row just before the label 'Anotações' using positional index
            pos = df.index.get_loc(idx)
            df = df.iloc[:pos, :]
            break

    # Keep only rows with Código and ALUNO
    # Find actual column names (could be variations)
    cols_lower = {c.lower(): c for c in df.columns.astype(str)}
    cod_col = cols_lower.get('código') or cols_lower.get('codigo')
    aluno_col = cols_lower.get('aluno')
    if cod_col is None or aluno_col is None:
        return pd.DataFrame()

    df = df[~df[cod_col].isna() & ~df[aluno_col].isna()].copy()

    # Clean values
    # Normalize code to string without trailing .0
    df[cod_col] = df[cod_col].astype(str).str.replace('.0', '', regex=False).str.strip()
    df[aluno_col] = df[aluno_col].astype(str).str.strip()

    # Drop fully empty columns
    df = df.dropna(axis=1, how='all')

    # Add turma (sheet)
    df.insert(0, 'Turma', sheet_name)

    # Also store normalized name for login matching
    df['__aluno_norm__'] = df[aluno_col].map(norm_name)

    # Rename key columns to fixed names
    df = df.rename(columns={aluno_col: 'ALUNO', cod_col: 'CÓDIGO'})

    return df


def load_data():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Arquivo Excel não encontrado: {EXCEL_PATH}")
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    frames = []
    for sheet in xls.sheet_names:
        df_raw = pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=None, engine='openpyxl')
        parsed = parse_sheet(df_raw, sheet)
        if not parsed.empty:
            frames.append(parsed)
    if not frames:
        raise ValueError('Nenhuma planilha com colunas CÓDIGO e ALUNO foi encontrada.')
    df_all = pd.concat(frames, ignore_index=True)

    # Ensure uniqueness of (norm_name, code)
    df_all['__key__'] = df_all['__aluno_norm__'] + '|' + df_all['CÓDIGO'].astype(str)

    # Build lookup dict
    lookup = {}
    for _, row in df_all.iterrows():
        key = row['__key__']
        # Convert row to dict excluding helper columns
        data = row.drop(labels=[c for c in row.index if c.startswith('__')]).to_dict()
        lookup[key] = data

    # Also keep list of columns for display
    display_cols = [c for c in df_all.columns if c not in ('__aluno_norm__', '__key__')]
    return lookup, display_cols

# Cache
LOOKUP, DISPLAY_COLS = load_data()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        codigo = request.form.get('codigo', '')
        key = f"{norm_name(nome)}|{str(codigo).strip()}"
        student = LOOKUP.get(key)
        if student:
            session['auth'] = True
            session['student_key'] = key
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Verifique o nome completo (como na chamada) e o código do aluno.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('auth'):
        return redirect(url_for('login'))
    student = LOOKUP.get(session.get('student_key'))
    if not student:
        flash('Sessão expirada. Faça login novamente.')
        return redirect(url_for('login'))
    # Prepare items to display (skip Turma, ALUNO, CÓDIGO)
    core = {k: student[k] for k in ['Turma', 'ALUNO', 'CÓDIGO'] if k in student}
    scores = [(k, v) for k, v in student.items() if k not in core]
    return render_template('dashboard.html', core=core, scores=scores)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/recarregar')
def recarregar():
    # Admin endpoint: recarregar dados a partir do Excel (hot-reload)
    global LOOKUP, DISPLAY_COLS
    LOOKUP, DISPLAY_COLS = load_data()
    flash('Dados recarregados com sucesso.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
