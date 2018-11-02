import ctypes
from ctypes import cdll

#load library
CHUNK = 100000
lib = cdll.LoadLibrary("/usr/local/lib/libavutil.so")
lib = cdll.LoadLibrary("/usr/local/lib/libavcodec.so")
lib = cdll.LoadLibrary("/usr/local/lib/libavformat.so")
lib = cdll.LoadLibrary("/root/ar-server/cpp/libarserver.so")

#ar server
lib.ar_server_new.restype = ctypes.c_void_p
lib.ar_server_new.argtypes = []
lib.ar_server_init.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.ar_server_accept.argtypes = [ctypes.c_void_p]
lib.ar_server_read.restype = ctypes.c_int
lib.ar_server_read.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
lib.ar_server_write.restype = ctypes.c_int
lib.ar_server_write.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
lib.ar_server_close.argtypes = [ctypes.c_void_p]

#video handler
lib.video_handler_new.restype = ctypes.c_void_p
lib.video_handler_new.argtypes = []
lib.video_handler_init.argtypes = [ctypes.c_void_p]
lib.video_handler_get_decoded_pkt.restype = ctypes.c_bool
lib.video_handler_get_decoded_pkt.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte))]
lib.video_free_decoded_pkt.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte))]
lib.video_handler_release.argtypes = [ctypes.c_void_p]

#audio handler
lib.audio_handler_new.restype = ctypes.c_void_p
lib.audio_handler_new.argtypes = []
lib.audio_handler_init.argtypes = [ctypes.c_void_p]
lib.audio_handler_get_decoded_pkt.restype = ctypes.c_bool
lib.audio_handler_get_decoded_pkt.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.c_bool]
lib.audio_free_decoded_pkt.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte))]
lib.audio_handler_release.argtypes = [ctypes.c_void_p]

#
lib.pkt_check.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.POINTER(ctypes.c_int)]

def get_lib():
	return lib
