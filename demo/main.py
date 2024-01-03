from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, TextIteratorStreamer
from threading import Thread
import time

tokenizer = AutoTokenizer.from_pretrained("./checkpoint")
model = AutoModelForCausalLM.from_pretrained("./checkpoint")

('bốn chữ', 'năm chữ', 'sáu chữ', 'bảy chữ',
 'tám chữ', 'lục bát', 'song thất lục bát')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
@cross_origin()
def say_hello():
    return '<h1>Hello World</h1>'


@app.route('/chat', methods=['POST'])
@cross_origin()
def generate_text():
    data = request.json
    start_word = data['start_word']
    gender = data['gender']
    prompt = f"{tokenizer.bos_token}{gender}{tokenizer.sep_token}{start_word}"
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    streamer = TextIteratorStreamer(tokenizer)
    generation_kwargs = dict(inputs=input_ids, streamer=streamer, max_new_tokens=70,
                             pad_token_id=tokenizer.eos_token_id, do_sample=True, top_k=4, no_repeat_ngram_size=2)
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    cont = True
    for new_text in streamer:
        if tokenizer.sep_token in new_text and cont:
            new_text = new_text[new_text.index(tokenizer.sep_token):]
            cont = False
        if cont:
            continue
        text = new_text.replace("<|startoftext|>", "").replace(
            gender, "").replace("<|sep|>", "\n").replace("<|endoftext|>", "\n")

        if "\n\n" in text:
            index = text.find("\n\n")
            socketio.emit('chat', text[:index])
            print(text[:index])
            break
        else:
            if text.startswith('\n'):
                text = text.replace('\n', '').capitalize()
            if '\n' in text:
                t = text.split('\n')
                u = t[1].capitalize()
                text = '\n'.join([t[0], u])
            socketio.emit('chat', text)
            print(text, end="")
    return 'ok', 200


@socketio.on('connect')
def ok():
    print("connect")


if __name__ == '__main__':
    socketio.run(app, debug=True)