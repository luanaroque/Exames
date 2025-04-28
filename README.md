
# Transcritor de Exames

Aplicativo em Streamlit para extrair e resumir resultados de exames laboratoriais a partir de arquivos PDF.

---

## Funcionalidades

- Upload de PDF de exames.
- Extração automática dos exames com valores numéricos.
- Aplicação de abreviações padrão para exames comuns.
- Remoção de unidades de medida e informações irrelevantes (CRM, telefone, anvisa, etc.).
- Identificação automática do laboratório e da data de coleta (com opção de edição manual).
- Geração de resumo formatado em uma única linha.
- Botão para copiar o resumo para a área de transferência.

---

## Abreviações Utilizadas

| Exame                    | Abreviação         |
|---------------------------|--------------------|
| Hemoglobina               | Hb                 |
| Hematócrito               | Ht                 |
| Leucócitos                | Leuco              |
| Plaquetas                 | Plaq               |
| Creatinina                | Cr                 |
| Ureia                     | U                  |
| Glicose                   | Gj                 |
| Hemoglobina glicada       | HbA1c              |
| Colesterol total          | CT                 |
| HDL colesterol            | HDL                |
| LDL colesterol            | LDL                |
| VLDL                      | VLDL               |
| Triglicerídeos            | Tg                 |
| Sódio                     | Na                 |
| Potássio                  | K                  |
| Cálcio                    | Ca                 |
| Magnésio                  | Mg                 |
| Bilirrubina total         | BT                 |
| Bilirrubina direta        | BD                 |
| Bilirrubina indireta      | BI                 |
| Fosfatase alcalina        | FAL                |
| Gama GT                   | GGT                |
| Vitamina D                | Vit D              |
| Vitamina B12              | Vit B12            |
| PCR (Proteína C Reativa)  | PCR                |
| Ferritina                 | Ferritina          |
| Saturação transferrina    | Sat Transferrina   |

---

## Como instalar e rodar o projeto

1. Clone o repositório:

\`\`\`bash
git clone https://github.com/seu-usuario/transcritor-de-exames.git
cd transcritor-de-exames
\`\`\`

2. Crie um ambiente virtual (opcional, mas recomendado):

\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
\`\`\`

3. Instale as dependências:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Rode o aplicativo:

\`\`\`bash
streamlit run app.py
\`\`\`

---

## Tecnologias usadas

- [Streamlit](https://streamlit.io/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [pyperclip](https://pyperclip.readthedocs.io/en/latest/)

---

## Observações

- O aplicativo foi desenvolvido para facilitar a transcrição de exames médicos no prontuário eletrônico.
- Caso o PDF esteja com layout muito diferente (ex.: imagens ou colunas complicadas), a extração pode não ser perfeita.

---
