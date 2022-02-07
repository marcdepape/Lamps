from gi.repository import Gst

AMP_ELEMENT_NAME = 'lamps-audio-amplify'
RTSP_ELEMENT_NAME = 'lamps-rtsp-source'


class LampAudioStream(object):
    def __init__(self):
        pipeline_string = self._pipeline_template()

        self.pipeline = Gst.parse_launch(pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(AMP_ELEMENT_NAME)
        self.volume = 1

        print("pipeline:", pipeline_string)

    def start(self, host: str):
        url = "rtsp://{}:8554/mic".format(host)

        self.rtspsrc.set_property('location', url)
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.READY)

    @property
    def volume(self):
        """ volume of 1 is 100%, though you can go greater than that """
        return self.audioamplify.get_property('amplification')

    @volume.setter
    def volume(self, volume):
        self.audioamplify.set_property('amplification', volume)

    @staticmethod
    def _pipeline_template():
        return ("rtspsrc debug=TRUE latency=250 name={} ! "
                "queue ! "
                "rtpvorbisdepay ! "
                "vorbisdec ! "
                "audioamplify name={} ! "
                "audioconvert ! "
                "audio/x-raw,format=S16LE,channels=2 ! "
                "alsasink device=\"sysdefault:CARD=sndrpiwsp\""
                ).format(RTSP_ELEMENT_NAME, AMP_ELEMENT_NAME)
