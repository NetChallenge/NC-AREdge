import ctypes
from ctypes import cdll
import sys
import face_recognition
import numpy as np
import cv2
from os import listdir
from os.path import isfile, join, basename
import json
import audio_server

CHUNK = 1000000
lib = cdll.LoadLibrary("/usr/local/lib/libavutil.so")
lib = cdll.LoadLibrary("/usr/local/lib/libavcodec.so")
lib = cdll.LoadLibrary("/usr/local/lib/libavformat.so")
lib = cdll.LoadLibrary("../cpp/libarserver.so")

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
lib.audio_handler_get_decoded_pkt.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte))]
lib.audio_free_decoded_pkt.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte))]
lib.audio_handler_release.argtypes = [ctypes.c_void_p]

#
lib.pkt_check.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.POINTER(ctypes.c_int)]

#face recognition
face_path="faces"
loaded_face_encodings = []
loaded_face_names = []
face_locations = []

#temporary variables
width = 640
height = 480
sdf = 1024

def start_ar_server():
	ar_server = lib.ar_server_new()
	video_handler = lib.video_handler_new()
	audio_handler = lib.audio_handler_new()

	lib.ar_server_init(ar_server, 5678)
	lib.video_handler_init(video_handler)
	lib.audio_handler_init(audio_handler)

	buf = (ctypes.c_ubyte * CHUNK)()
	buf = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

	flag = ctypes.c_int()
	pkt_buf = ctypes.POINTER(ctypes.c_ubyte)()
	pkt_len = ctypes.c_int()

	np_video_decoded = np.zeros(width * height * 3 / 2, dtype=np.uint8)
	video_decoded = np_video_decoded.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
	np_audio_decoded = np.zeros(sdf, dtype=np.uint8)
	audio_decoded = np_audio_decoded.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

	#initialize stt
	stream = AudioStream()
	manager = STTManager(conn, conn_list, addr, stream)
	manager.run()

	while True:
		lib.ar_server_accept(ar_server)
		while True:
			read_len = lib.ar_server_read(ar_server, buf, CHUNK)
			if read_len < 0:
				print("ar_server_read error")
				break
			#print("read packet. packet size is ", read_len, ", packet type is ", "video" if buf[0] == 0 else "audio")

			#print("buf:")
			#print(buf[1294])
			#print(read_len)
			lib.pkt_check(buf, read_len, ctypes.byref(flag), ctypes.byref(pkt_buf), ctypes.byref(pkt_len))
			if flag.value == 0:
				#print("start_buf:")
				#print(pkt_buf[1293])
				#print(pkt_len.value)
				if lib.video_handler_get_decoded_pkt(video_handler, pkt_buf, pkt_len, ctypes.byref(video_decoded)) == True:
					json_face_names = face_recognition_in_video(np_video_decoded, width, height)
					json_face_names_p = ctypes.cast(json_face_names, ctypes.POINTER(ctypes.c_ubyte))
					if json_face_names is not None:
						lib.ar_server_write(ar_server, json_face_names_p, len(json_face_names))
				else :
					print("video packet not yet")
			elif flag.value == 1:
				lib.audio_handler_get_decoded_pkt(audio_handler, pkt_buf, pkt_len, ctypes.byref(audio_decoded))
				speaker_recognition(np_audio_decoded)

	stream.close()
	manager.join()

def face_recognition_in_video(yuv_frame, width, height):
	yuv_frame = yuv_frame.reshape(height * 3 / 2, width)
	#print(yuv_frame.shape)
	rgb_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV420sp2RGB)
	#print(rgb_frame)
	rgb_small_frame = cv2.resize(rgb_frame, (0,0), fx=0.25, fy=0.25)

	face_locations = face_recognition.face_locations(rgb_small_frame)
	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)	
	print(face_locations)
	print(face_encodings)

	face_names = []
	for idx, face_encoding in enumerate(face_encodings):
		matches = face_recognition.compare_faces(loaded_face_encodings, face_encoding)
		name = "Unknown"

		if True in matches:
			first_mach_index = matches.index(True)
			name = loaded_face_names[first_match_index]
			print(name+"\n")
			face_names.append([name, face_locations[idx]])

	if not face_names:
		return None

	json_face_names = json.dump(face_names)
	print(json_face_names)
	return json_face_names

def speaker_recognition(arr):
	stream.put()	

def load_face_image():
	face_path_list = [img for img in listdir(face_path+"/img") if isfile(join(face_path+"/img", img))]
	loaded_face_names = [basename(f) for f in face_path_list]
	#print(face_path_list)
	#a = face_recognition.load_image_file(face_path+"/img/"+face_path_list[0])
	#print(face_recognition.face_locations(a))
	#locations = face_recognition.face_locations(a)
	#encodings = face_recognition.face_encodings(a, locations)
	#print(locations)
	#print(encodings)
	loaded_face_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(face_path+"/img/"+f))[0] for f in face_path_list]
	#print(loaded_face_names)
	#print(loaded_face_encodings)
	#flags = [i for i in dir(cv2) if i.startswith('COLOR_')]
	#print(flags)

def main():
	load_face_image()
	#start_ar_server()

if __name__ == "__main__":
	main()
