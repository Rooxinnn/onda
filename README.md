# YouTube → OGG

Estrutura pronta com frontend simples e backend Flask + yt-dlp.

## Arquivos
- `index.html`: frontend.
- `backend/main.py`: API Flask.
- `backend/download.py`: processamento com yt-dlp.
- `backend/requirements.txt`: dependências Python.
- `render.yaml`: configuração opcional para o Render.
- `backend/downloads/`: pasta de saída.

## Antes de usar
No `index.html`, substitua:

`https://seu-site-no-render.onrender.com`

pela URL real do seu Web Service.

## Render
Build command:
`pip install -r backend/requirements.txt`

Start command:
`cd backend && python main.py`

O ambiente do servidor também precisa ter FFmpeg instalado para a conversão para OGG funcionar.

Use apenas conteúdo que você tenha direito/permissão para baixar.
