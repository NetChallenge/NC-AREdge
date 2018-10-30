import ctypes
from ctypes import cdll
import sys
import face_recognition
import numpy as np
import cv2
import os
import json
import audio_server
import my_mysql
import my_cpp_lib
import requests
import datetime
from PIL import Image
from io import BytesIO
import paho.mqtt.client as paho
from functools import partial

def stt_transcript_callback(client, topic, data):
	print("topic: " + topic + ", message: " + data)
	client.publish(topic, data)

def start_ar_server(mysql_client, mqtt_client, mqtt_topic, loaded_face_names, loaded_face_encodings, room_id, user_email, edge_port, width, height, sdf, lib, CHUNK, traffic_duration):
	ar_server = lib.ar_server_new()
	video_handler = lib.video_handler_new()
	audio_handler = lib.audio_handler_new()

	lib.ar_server_init(ar_server, int(edge_port))
	lib.video_handler_init(video_handler, width, height)
	lib.audio_handler_init(audio_handler)

	buf = (ctypes.c_ubyte * CHUNK)()
	buf = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

	flag = ctypes.c_int()
        
	pkt_buf = ctypes.POINTER(ctypes.c_ubyte)()
	pkt_len = ctypes.c_int()

	testcount = 0
	while True:
		lib.ar_server_accept(ar_server)
		#start manager
		stream = audio_server.AudioStream()
		manager = audio_server.STTManager(stream, partial(stt_transcript_callback, mqtt_client, mqtt_topic))
		manager.run()

		traffic_start_time = datetime.datetime.now()
		traffic = 0
		while True:
			read_len = lib.ar_server_read(ar_server, buf, CHUNK)
			#check traffic
			if datetime.datetime.now() - traffic_start_time >= datetime.timedelta(seconds=traffic_duration):
				mysql_client.pymysql_commit_query('INSERT INTO room_traffic(room_id, user_email, traffic) VALUES ('+room_id+',"'+user_email+'",'+str(traffic)+')')
				traffic_start_time = datetime.datetime.now()
				traffic = 0
			traffic += read_len

			if read_len < 0:
				print("ar_server_read error. read len is " + str(read_len))
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
				np_video_decoded = np.zeros(int(width * height * 3 / 2), dtype=np.uint8)
				video_decoded = np_video_decoded.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
				if lib.video_handler_get_decoded_pkt(video_handler, pkt_buf, pkt_len, ctypes.byref(video_decoded)) == True:
					#json_face_names = face_recognition_in_video(np_video_decoded, width, height, testcount)
					#testcount+=1
					#if json_face_names is not None:
					#	json_face_names_p = ctypes.cast(json_face_names, ctypes.POINTER(ctypes.c_ubyte))
					#	lib.ar_server_write(ar_server, json_face_names_p, len(json_face_names))
					pass
				else :
					print("video packet not yet")
			elif flag.value == 1:
				np_audio_decoded = np.zeros(sdf, dtype=np.uint8)
				audio_decoded = np_audio_decoded.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
				if lib.audio_handler_get_decoded_pkt(audio_handler, pkt_buf, pkt_len, ctypes.byref(audio_decoded), True) == True:
					stream.put(np_audio_decoded)
				else :
					print("audio packet not yes")
				#speaker_recognition(np_audio_decoded)

		stream.close()
		manager.join()

def face_recognition_in_video(yuv_frame, width, height, testcount):
	yuv_frame = yuv_frame.reshape((int)(height * 3 / 2), width)
	#print(yuv_frame.shape)
	rgb_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV420p2RGB)
	cv2.imwrite("testimage/test"+str(testcount)+".jpg", rgb_frame)
	#print(rgb_frame)
	rgb_small_frame = cv2.resize(rgb_frame, (0,0), fx=0.25, fy=0.25)

	face_locations = face_recognition.face_locations(rgb_small_frame)
	if not face_locations:
		return None

	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
	if not face_encodings:
		return None
	
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
	rows = my_mysql.pymysql_fetch_query('SELECT image_url, user_name FROM face WHERE user_email=(SELECT user_email FROM room_user WHERE room_id='+room_id+');')

	for image_url, user_name in rows:
		img_string = requests.get(image_url).content
		img = Image.open(BytesIO(img_string))
		np_img = np.array(img)

		loaded_face_names.append(user_name)
		loaded_face_encodings.append(face_recognition.face_encodings(np_img)[0])

		'''
		a = datetime.datetime.now()
		loaded_face_encodings.append(face_recognition.face_encodings(npImg)[0])
		b = datetime.datetime.now()
		print(b-a)

		a = datetime.datetime.now()
		locations = face_recognition.face_locations(npImg)
		print(locations)
		b = datetime.datetime.now()
		print(b-a)

		w, h = img.size
		print(w, h)
		a = datetime.datetime.now()
		cropEncodings = face_recognition.face_encodings(npImg, locations)[0]
		print(face_recognition.compare_faces(loaded_face_encodings,cropEncodings))
		b = datetime.datetime.now()
		print(b-a)
		'''

def initialize():
	room_id = os.environ.get('ROOM_ID', None)
	user_email = os.environ.get('USER_EMAIL', None)
	edge_port = os.environ.get('EDGE_PORT', None)
	#we need to initialize this values
	width = int(1280)
	height = int(720)
	sdf = int(1024)
	#get cpp libraries and chunk size
	lib = my_cpp_lib.get_lib()
	CHUNK = my_cpp_lib.CHUNK
	#traffic duration
	traffic_duration = 2

	#load mysql
	mysql_client = my_mysql.MyMysql(os.environ.get('MYSQL_HOST', None), os.environ.get('MYSQL_USER', None), os.environ.get('MYSQL_PWD', None), os.environ.get('MYSQL_DB', None))
        #load mqtt info
	mqtt_client = paho.Client(os.environ.get('MQTT_ID', None))
	mqtt_client.connect(os.environ.get('MQTT_IP', None), int(os.environ.get('MQTT_PORT', None)))
	mqtt_topic = os.environ.get('MQTT_TOPIC', None)

	#load face image
	rows = mysql_client.pymysql_fetch_query('SELECT image_url, user_name FROM face WHERE user_email=(SELECT user_email FROM room_user WHERE room_id='+room_id+');')

	loaded_face_names = []
	loaded_face_encodings = []
	for image_url, user_name in rows:
		img_string = requests.get(image_url).content
		img = Image.open(BytesIO(img_string))
		np_img = np.array(img)

		loaded_face_names.append(user_name)
		loaded_face_encodings.append(face_recognition.face_encodings(np_img)[0])

	return mysql_client, mqtt_client, mqtt_topic, loaded_face_names, loaded_face_encodings, room_id, user_email, edge_port, width, height, sdf, lib, CHUNK, traffic_duration

def main():
	mysql_client, mqtt_client, mqtt_topic, loaded_face_names, loaded_face_encodings, room_id, user_email, edge_port, width, height, sdf, lib, CHUNK, traffic_duration = initialize()
	start_ar_server(mysql_client, mqtt_client, mqtt_topic, loaded_face_names, loaded_face_encodings, room_id, user_email, edge_port, width, height, sdf, lib, CHUNK, traffic_duration)

if __name__ == "__main__":
	main()
