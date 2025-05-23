# import os
# from flask import Flask, render_template, request, send_from_directory
# from pydub import AudioSegment

# app = Flask(__name__)
# UPLOAD_FOLDER = 'cortes'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def time_to_milliseconds(t):
#     """Converte mm:ss em milissegundos"""
#     minutes, seconds = map(int, t.split(':'))
#     return (minutes * 60 + seconds) * 1000

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     cortes_salvos = []

#     if request.method == 'POST':
#         audio_file = request.files['audio']
#         start = request.form['inicio']
#         end = request.form['fim']

#         if audio_file:
#             audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
#             audio_file.save(audio_path)

#             audio = AudioSegment.from_mp3(audio_path)
#             ini_ms = time_to_milliseconds(start)
#             fim_ms = time_to_milliseconds(end)

#             corte = audio[ini_ms:fim_ms]
#             filename = f"corte_{len(os.listdir(UPLOAD_FOLDER)) + 1}.mp3"
#             corte_path = os.path.join(UPLOAD_FOLDER, filename)
#             corte.export(corte_path, format="mp3")

#     Lista todos os cortes da pasta
#     cortes_salvos = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".mp3")]
#     cortes_salvos.sort()

#     return render_template('index.html', cortes=cortes_salvos)


# @app.route('/cortes/<filename>')
# def download(filename):
#     return send_from_directory(UPLOAD_FOLDER, filename)

# if __name__ == '__main__':
#     app.run(debug=True)
import os
import whisper
from flask import Flask, render_template, request, send_from_directory, jsonify
from pydub import AudioSegment

app = Flask(__name__)
UPLOAD_FOLDER = 'cortes'
GRAVACOES_FOLDER = 'gravacoes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRAVACOES_FOLDER, exist_ok=True)

model = whisper.load_model("base")

def time_to_milliseconds(t):
    minutes, seconds = map(int, t.split(':'))
    return (minutes * 60 + seconds) * 1000

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_file = request.files['audio']
        start = request.form['inicio']
        end = request.form['fim']

        if audio_file:
            audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
            audio_file.save(audio_path)

            audio = AudioSegment.from_mp3(audio_path)
            ini_ms = time_to_milliseconds(start)
            fim_ms = time_to_milliseconds(end)

            corte = audio[ini_ms:fim_ms]
            filename = f"corte_{len(os.listdir(UPLOAD_FOLDER)) + 1}.mp3"
            corte_path = os.path.join(UPLOAD_FOLDER, filename)
            corte.export(corte_path, format="mp3")

    cortes_salvos = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".mp3")]
    cortes_salvos.sort()
    return render_template('index.html', cortes=cortes_salvos)

@app.route('/cortes/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/validar', methods=['POST'])
def validar_pronuncia():
    import whisper
    from pydub import AudioSegment
    from tempfile import NamedTemporaryFile

    audio = request.files.get('audio')
    audio_id = request.form.get('audio_id')

    if not audio or not audio_id:
        return "Erro: áudio ou ID não recebido", 400

    # Salva temporariamente o áudio recebido
    with NamedTemporaryFile(delete=False, suffix=".webm") as temp:
        audio.save(temp.name)
        temp_path = temp.name

    # Converte e transcreve com Whisper
    model = whisper.load_model("base")
    try:
        result_usuario = model.transcribe(temp_path)
    except Exception as e:
        print("Erro ao transcrever:", e)
        return "Erro na transcrição", 500

    # Transcrição do usuário
    transcricao_usuario = result_usuario['text'].strip().lower()
    print(f"🎧 Usuário disse: {transcricao_usuario}")

    # Carrega o corte original
    corte_path = os.path.join(UPLOAD_FOLDER, audio_id)
    result_original = model.transcribe(corte_path)
    transcricao_original = result_original['text'].strip().lower()
    print(f"🎼 Original: {transcricao_original}")

    # Comparação
    if transcricao_usuario in transcricao_original or transcricao_original in transcricao_usuario:
        print("✅ Pronúncia correta")
        return '<div style="color:green;font-weight:bold;">✅ OK</div>'
    else:
        print("❌ Pronúncia incorreta")
        return '<div style="color:red;font-weight:bold;">❌ Tente novamente</div>'


if __name__ == '__main__':
    app.run(debug=True)