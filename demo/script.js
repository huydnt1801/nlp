const buttonCallApi = document.getElementById('call-api')
const result = document.getElementById('result')
const text = document.getElementById('text')
const type = document.getElementById('type')

const d = {
    1: 'bốn chữ',
    2: 'năm chữ',
    3: 'sáu chữ',
    4: 'bảy chữ',
    5: 'tám chữ',
    6: 'lục bát',
    7: 'song thất lục bát'
}

buttonCallApi.onclick = async () => {
    const start_word = text.value ?? ''
    const gender = d[type.value]
    result.value = ''
    const res = await axios.post('http://localhost:5000/chat', { start_word: start_word, gender: gender })
    console.log(res);
}

const socket = io('http://localhost:5000')

socket.on('chat', (x) => {
    result.value = result.value + x
})