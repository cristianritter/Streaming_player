import vlc
import time
import parse_config
from threading import Thread


restart = False

@vlc.CallbackDecorators.LogCb
def log_callback(data, level, ctx, fmt, args):
    # Do something interesting
    if "HTTP connection failure" in fmt.decode():
        global restart
        restart = True
        time.sleep(5)
        pass

def nova_instancia(radio_name, audio_link, output_dev):
    good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
    i = vlc.Instance('--verbose 0')
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
    while 1:
        global restart
        if str(player.get_state()) in good_states and not restart:
            time.sleep(5)
            print('{} - Stream is working. Current state = {}'.format(radio_name, player.get_state()))
        else:
            restart = False 
            print('Stream is not working. Current state = {}'.format(player.get_state()))
            time.sleep(10)
            i = vlc.Instance('--verbose 0')
            player = i.media_player_new()
            media = i.media_new(audio_link)
            media.get_mrl()
            time.sleep(0.5)
            player.audio_output_set('waveout')
            player.audio_output_device_set('waveout', output_dev)
            player.set_media(media)
            time.sleep(0.5)
            player.play()
      
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

