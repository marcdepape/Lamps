#include <csignal>

#include <sstream>
#include <stdexcept>

#include <gst/gst.h>
#include <gst/rtsp-server/rtsp-server.h>

static GMainLoop * loop = NULL;

void quit_on_signal(int signal) {
	g_print("\nquitting\n");
	g_main_loop_quit(loop);
}

int main(int argc, char *argv[]) {
	gst_init(&argc, &argv);
	loop = g_main_loop_new(NULL, FALSE);

	GstRTSPServer * server = gst_rtsp_server_new();
	GstRTSPMountPoints * mounts = gst_rtsp_server_get_mount_points(server);
	GstRTSPMediaFactory * factory = gst_rtsp_media_factory_new();

	std::stringstream pipeline;

	// source
	pipeline << "alsasrc ! queue leaky=downstream max-size-buffers=16 ! ";

	// compressor
	//pipeline << "audiodynamic ratio=4 threshold=0.3 ! ";

	pipeline << "audioconvert ! queue !";

	// high-pass
	//pipeline << "audiowsinclimit cutoff=9000 ! ";

	// vorbis encoder (default quality is 0.3)
	pipeline << "vorbisenc quality=0.7 ! queue leaky=downstream max-size-buffers=16 ! ";
	pipeline << "rtpvorbispay name=pay0 pt=96";

	gst_rtsp_media_factory_set_shared(factory, TRUE);
	gst_rtsp_media_factory_set_launch(factory, pipeline.str().c_str());
	gst_rtsp_mount_points_add_factory(mounts, "/mic", factory);
	g_object_unref(mounts);

	if (gst_rtsp_server_attach(server, NULL) == 0) {
		throw std::runtime_error("couldn't attach server");
	}

	std::signal(SIGINT, quit_on_signal);
	std::signal(SIGTERM, quit_on_signal);

	g_main_loop_run(loop);
	g_main_loop_unref(loop);
	gst_deinit();

	return 0;
}
