import vlc
from time import sleep
import parse_config
from threading import Thread
from datetime import datetime
import pyaudio
from struct import unpack
from math import sqrt
import os

configuration = parse_config.ConfPacket()
streamings = configuration.load_config('DEFAULT')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root

print("Carregando DLLS...")
try:
    VLC_DIR = os.path.join(ROOT_DIR, 'VLC\\')        
    os.add_dll_directory(r'{}'.format(VLC_DIR))
except Exception as Err:
    pass

class Streaming:
    def __init__(self, radio_name, audio_link, output_dev, name, device_index):
        self.radio_name = radio_name
        self.audio_link = audio_link
        self.output_dev = output_dev
        self.name = name
        self.index = device_index
        self.i = None
        self.player = None
        while 1:       
            print('Iniciando player...')
            self.listen()
        
    def get_rms(self, block ):
        count = len(block)/2
        format = "%dh"%(count)
        shorts = unpack( format, block )
        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0/32768.0)
            sum_squares += n*n
        return sqrt( sum_squares / count )
 
    def iniciar_streaming(self):
        self.i = vlc.Instance('--verbose -1')
        self.player = self.i.media_player_new()
        media = self.i.media_new(self.audio_link)
        media.get_mrl()
        self.player.audio_output_set('waveout')
        self.player.audio_output_device_set('waveout', self.output_dev)
        self.player.audio_output_set('waveout')
        self.player.audio_output_device_set('waveout', self.output_dev)
        self.player.set_media(media)
        self.player.play()

    def open_mic_stream(self):
        pa = pyaudio.PyAudio()
        self.INPUT_FRAMES_PER_BLOCK = int(44100*5)
        stream = pa.open(   format = pyaudio.paInt16 ,
                                    channels = 2,
                                    rate = 44100,
                                    input = True,
                                    input_device_index = self.index,
                                    frames_per_buffer = self.INPUT_FRAMES_PER_BLOCK)
        return stream
    
    def listen(self):
        try:
            self.iniciar_streaming()
            amplitude = 1
            while amplitude > 0.001:
                stream = self.open_mic_stream()
                block = stream.read(self.INPUT_FRAMES_PER_BLOCK)
                amplitude = self.get_rms( block )
                print('Audio level '+self.name+': ', amplitude)
                sleep(0.1)
            self.player.stop()
            sleep(1)
            print('finalizado')
        except IOError:
            pass

def nova_target(radio_name, audio_link, output_dev, streamings, rec_idx):
    print('Starting threading: ', radio_name, audio_link, output_dev, streamings, rec_idx)
    Streaming(radio_name, audio_link, output_dev, streamings, rec_idx)

t=[]
for idx, item in enumerate(streamings['DEFAULT']):
    configs = configuration.load_config(streamings['DEFAULT'][item])
    radio_name = configs[streamings['DEFAULT'][item]]['radio_name']
    audio_link = configs[streamings['DEFAULT'][item]]['audio_link']
    output_dev = configs[streamings['DEFAULT'][item]]['output_dev']
    rec_dev_index = int(configs[streamings['DEFAULT'][item]]['rec_dev_index'])
    print(radio_name)
    t.append (Thread(target=nova_target, args=(radio_name, audio_link, output_dev, streamings['DEFAULT'][item], rec_dev_index)))
    t[idx].start()
    sleep(3)
   