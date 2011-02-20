#!/usr/bin/python
import gst
import gobject

# Simple video4linux streaming server for the robot webcam built
# during the STPLN Hackathon, quick hack by Joel Larsson (@tilljoel)

HOST = '127.0.0.1'
PORT = 1234
WIDTH = 640
HEIGHT = 480

def on_message(bus, message):
    t = message.type
    if t == gst.MESSAGE_EOS:
        player.set_state(gst.STATE_NULL)
        print ("*** got EOS on bus, stop")
    elif t == gst.MESSAGE_ERROR:
        err, debug = message.parse_error()
        player.set_state(gst.STATE_NULL)
        print "*** got error on bus: %s" % err, debug


def go():
    print "Setting gstreamer pipeline to PLAYING"
    player.set_state(gst.STATE_PLAYING)
    mainloop = gobject.MainLoop()
    mainloop.run()

print "Start streaming server, %dx%d to %s:%d" % (WIDTH, HEIGHT, HOST, PORT)
cmdline = 'v4l2src ! capsfilter caps="video/x-raw-yuv,width=%d,height=%d" !' \
          ' ffmpegcolorspace ! ffenc_mpeg4 ! rtpmp4vpay send-config=true !' \
          ' udpsink host=%s port=%d' % (WIDTH, HEIGHT, HOST, PORT)
player = gst.parse_launch(cmdline)

bus = player.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message)

go()
