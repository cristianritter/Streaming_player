import vlc
import time
import parse_config
from threading import Thread
from datetime import date, datetime, timedelta

restart = False

@vlc.CallbackDecorators.LogCb
def log_callback(data, level, ctx, fmt, args):
    dataFormatada = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    # Do something interesting
    print(dataFormatada + "FMT: " + fmt.decode())
    if "HTTP" in fmt.decode() or 'pts_delay' in fmt.decode() or 'deactivating' in fmt.decode():
        global restart
        print("Falha detectada...\n\n\n")
        restart = True
        time.sleep(5)

def nova_instancia(radio_name, audio_link, output_dev):
    good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
    i = vlc.Instance('--verbose 1')
    i.log_set(log_callback, None)
    player = i.media_player_new()
    media = i.media_new(audio_link)
    media.get_mrl()
    player.audio_output_set('waveout')
    player.audio_output_device_set('waveout', output_dev)
    player.stop()
    player.set_media(media)
    time.sleep(0.5)
    player.play()
    time.sleep(1)
    while 1:
        global restart
        status = player.get_state()
        if not str(status) in good_states:
            print("ERRO DETECTADO: ", status)
            restart = True 
        if not restart:
            time.sleep(5)
            #print('{} - Stream is working. Current state = {}'.format(radio_name, player.get_state()))
        else:
            restart = False 
            print('Stream is not working. Current state = {}'.format(player.get_state()))
            print('Tentando reiniciar o serviço...')
            time.sleep(1)
            player.stop()
            time.sleep(1)
            i = vlc.Instance('--verbose 1')
            i.log_set(log_callback, None)
            player = i.media_player_new()
            media = i.media_new(audio_link)
            media.get_mrl()
            time.sleep(1)
            player.audio_output_set('waveout')
            time.sleep(1)
            player.audio_output_device_set('waveout', output_dev)
            time.sleep(1)
            player.set_media(media)
            time.sleep(1)
            player.play()
            time.sleep(10)
      
configuration = parse_config.ConfPacket()
streamings = configuration.load_config('DEFAULT')
t = []

for idx, item in enumerate(streamings['DEFAULT']):
    configs = configuration.load_config(streamings['DEFAULT'][item])
    radio_name = configs[streamings['DEFAULT'][item]]['radio_name']
    audio_link = configs[streamings['DEFAULT'][item]]['audio_link']
    output_dev = configs[streamings['DEFAULT'][item]]['output_dev']
    t.append( Thread(target=nova_instancia, args=[radio_name,audio_link,output_dev]) ) 
    t[idx].start()
    time.sleep(1)

