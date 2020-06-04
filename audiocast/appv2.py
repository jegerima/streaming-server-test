from flask import Flask, Response,render_template
import wave
import pyaudio
from playsound import playsound
import datetime as dt

app = Flask(__name__)


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

p = pyaudio.PyAudio()
#wf = wave.open(r'blinding-lights.wav', 'rb')

songTime = None
songChunks = {};
songs = {
    'blinding-lights': {'src':'blinding-lights.wav'},
}


def printMediaInfo(wf):
    print('=================================')

    print('FileSize: ' + str(wf.getsampwidth() * wf.getnchannels() * wf.getnframes()) + ' Bytes')
    print('FrameSize: ' + str(wf.getsampwidth() * wf.getnchannels()) + ' bytes')
    print('FrameRate: '+ str(wf.getframerate()) + ' Hz')
    print('Channels: ' + str(wf.getnchannels()))
    print('AudioLength: ' + str(wf.getnframes()/wf.getframerate()) + ' seconds')

    print('=================================')

@app.route('/getCurrentTime')
def getCurrentTime():

    if(songs['blinding-lights'].get('ini')==None):
        return {'current': dt.datetime.now(), 'secs': 1.0, 'error': 'No audio file'}
    else: 
        songTime = songs['blinding-lights']['ini'];
        milisecs =  (dt.datetime.now()-songTime).microseconds/1000;
        offset = 0
        if(milisecs<250):
            offset = 0.0
        elif(milisecs<750):
            offset = 0.5
        else:
            offset = 1.0

        return {    'songtime': songTime, 
                    'current': dt.datetime.now(), 
                    'secs': (dt.datetime.now()-songTime).seconds/1.0, 
                    'milisecs': milisecs, 
                    'offset': offset,
                    'song': 'Blinding Lights' }

@app.route('/generate')
def playAudio():
    # blinding lights => 3:22 => 202 segundos 
    wf = wave.open(songs['blinding-lights']['src'], 'rb')
    printMediaInfo(wf)
    songTime = dt.datetime.now()
    songs['blinding-lights']['ini'] = songTime;
    
    lastChunkKey = 0
    lastChunkValue = 0
    CHUNK = int(wf.getframerate()/2)

    lastChunkValue = wf.readframes(CHUNK)
    lastChunkKey = lastChunkKey + CHUNK
    
    while len(lastChunkValue) > 0:
        songChunks[lastChunkKey] = lastChunkValue
        lastChunkValue = wf.readframes(CHUNK)
        lastChunkKey = lastChunkKey + CHUNK

    print(str(list(songChunks.keys())[0:20]) + '... chunks:' + str(len(songChunks.keys())))

    wf.close()
    
    return {'message': 'Ready for '+ str(len(songChunks)) + ' chunks', 'date': songTime }


@app.route('/newaudio/<second>')
def newaudio(second):
    def newsound(second):
        wf = wave.open(songs['blinding-lights']['src'], 'rb')
        secs = float(second)

        CHUNK = wf.getframerate()
        print('From '+ str(second) + ' sec. Chunk: '+ str(secs*CHUNK))

        first_run = True
        wav_header = genHeader(wf.getframerate(), wf.getsampwidth()*8, wf.getnchannels())
        data = wav_header + songChunks.get(int(secs*CHUNK))
        
        offset = 0.5;

        while len(data) > 0:

            if first_run:
                first_run = False
            else:
                data = songChunks.get(int((secs+offset)*CHUNK))
                offset = offset + 0.5
            yield(data)

        wf.close()

    return Response(newsound(second))


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('indexv2.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)

# https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask
# https://people.csail.mit.edu/hubert/pyaudio/docs/
# https://nbviewer.jupyter.org/github/mgeier/python-audio/blob/master/audio-files/audio-files-with-wave.ipynb