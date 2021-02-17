import vlc
import time
import parse_config

configuration = parse_config.ConfPacket()
configs = configuration.load_config('STREAMING')
radio_name = configs['STREAMING']['radio_name']
audio_link = configs['STREAMING']['audio_link']
output_dev = configs['STREAMING']['output_dev']

i = vlc.Instance('--verbose 1')
player = i.media_player_new()
media = i.media_new(audio_link)
media.get_mrl()

#devices = (i.audio_output_enumerate_devices())
player.audio_output_set('waveout')
player.audio_output_device_set('waveout', output_dev)
player.stop()
player.set_media(media)
player.play()

good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
while str(player.get_state()) in good_states:
    time.sleep(5)
    print('{} - Stream is working. Current state = {}'.format(radio_name, player.get_state()))

print('Stream is not working. Current state = {}'.format(player.get_state()))
player.stop()