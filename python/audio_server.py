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

    def __init__(self, stream, callback = None):
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='ko-KR')
        self.streaming_config = types.StreamingRecognitionConfig(
            config=self.config,
            single_utterance=False,
            interim_results=False)
        self.stream = stream
        self.callback = callback

    def process_stt(self):
        while True:
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
                    print(datetime.datetime.now(), ":", transcript)
                    #print(result.is_final)
                    
                    #need to write listener
                    if self.callback:
                        self.callback(transcript)
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
