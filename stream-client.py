import gtk
import pygst
pygst.require("0.10")
import gst

# Simple streaming client for the robot webcam built during
# the STPLN Hackathon, quick hack by Joel Larsson (@tilljoel)

TEXT_START = "Start streaming"
TEXT_STOP = "Stop streaming"
PORT = 1234


class GTK_Main:

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Hackathon stream viewer")
        window.set_default_size(800, 600)
        window.connect("destroy", gtk.main_quit, "WM destroy")
        vbox = gtk.VBox()
        window.add(vbox)
        self.movie_window = gtk.DrawingArea()
        vbox.add(self.movie_window)
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False)
        hbox.set_border_width(10)
        hbox.pack_start(gtk.Label())
        self.button = gtk.Button(TEXT_START)
        self.button.connect("clicked", self.start_stop)
        hbox.pack_start(self.button, False)
        self.button2 = gtk.Button("Quit")
        self.button2.connect("clicked", self.exit)
        hbox.pack_start(self.button2, False)
        hbox.add(gtk.Label())
        window.show_all()

        cmdline = 'udpsrc port=%d ! capsfilter caps="application/x-rtp,' \
                  'media=(string)video,clock-rate=(int)90000,encoding-name=' \
                  '(string)MP4V-ES,payload=96" ! rtpmp4vdepay ! ffdec_mpeg4' \
                  ' ! xvimagesink' % PORT
        self.player = gst.parse_launch(cmdline)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def start_stop(self, w):
        if self.button.get_label() == TEXT_START:
            self.button.set_label(TEXT_STOP)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label(TEXT_START)

    def exit(self, widget, data=None):
        gtk.main_quit()

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            print "*** EOS msg on bus"
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label(TEXT_START)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "*** Error on bus: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label(TEXT_START)

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            print "Assign to viewport"
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            gtk.gdk.threads_enter()
            imagesink.set_xwindow_id(self.movie_window.window.xid)
            gtk.gdk.threads_leave()

GTK_Main()
gtk.gdk.threads_init()
gtk.main()
