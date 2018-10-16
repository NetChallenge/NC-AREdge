import io
import os
import datetime
# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import socket
from six.moves import queue
import threading
from google.api_core import exceptions
import datetime

SOCK_MAX_SIZE = 4

class AudioStream(object):
    def __init__(self):
        self.queue = queue.Queue()
        self.closed = False

    def put(self, data):
        self.queue.put(data)

    def generator(self):
        while not self.closed:
            chunk = self.queue.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self.queue.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
    
    def close(self):
        self.closed = True
        self.queue.put(None)

class STTManager(object):
    client = speech.SpeechClient()

    def __init__(self, conn, conn_list, addr, stream):
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US')
        self.streaming_config = types.StreamingRecognitionConfig(
            config=self.config,
            single_utterance=False,
            interim_results=False)
        self.conn = conn
        self.conn_list = conn_list
        self.addr = addr
        self.stream = stream

    def process_stt(self):
        while True:
            print("test")
            generator = self.stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content) for content in generator)
            responses = self.client.streaming_recognize(self.streaming_config, requests)

            try:
                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]
                    if not result.alternatives:
                        continue
 
                    transcript = result.alternatives[0].transcript
                    print(datetime.datetime.now(), ":", self.addr, ",", transcript)
                    #print(result.is_final)
                    
                    binary_transcript = transcript.encode()
                    for con in self.conn_list:
                        con.send(binary_transcript)
                
                break
            except (exceptions.OutOfRange, exceptions.InvalidArgument) as e:
                if not ('maximum allowed stream duration' in e.message or 'deadline too short' in e.message):
                    raise
                print("resume!!")

        self.conn_list.remove(self.conn)
           

    def run(self):
        self.thread = threading.Thread(target=self.process_stt)
        self.thread.start()

    def join(self):
        self.thread.join()

def process(conn, conn_list, addr):
    stream = AudioStream()
    manager = STTManager(conn, conn_list, addr, stream)
    manager.run()

    while 1:
        try:
            msg = conn.recv(8192)
            if len(msg) == 0:
                print(addr, " disconnected.")
                break

            stream.put(msg)
        except socket.error as e:
            print("Error receiving data: ", e)
            break

    stream.close()
    manager.join()

def run_audio_stt(port=9091):
    host = '0.0.0.0'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setblocking(True)
        s.bind((host, port))
        s.listen(SOCK_MAX_SIZE)
        conn_list = []

        while 1:
            conn, addr = s.accept()
            conn_list.append(conn)
            print(addr, " connected.")
            thread = threading.Thread(target=process, args=(conn, conn_list, addr))
            thread.start()
'''
if __name__=='__main__':
     run_server()
'''
