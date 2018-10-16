#include "ARServer.hpp"
#include "VideoHandler.hpp"
#include "AudioHandler.hpp"
#include <new>

extern "C" {
	void* ar_server_new() { return new(std::nothrow) ARServer; }
	void ar_server_init(void* ptr, int port) {
		ARServer* server = reinterpret_cast<ARServer*>(ptr);
		server->init(port);
	}
	void ar_server_accept(void* ptr) {
		ARServer* server = reinterpret_cast<ARServer*>(ptr);
		server->acceptClient();
        }
	int ar_server_read(void* ptr, unsigned char* buf, int size) {
		ARServer* server = reinterpret_cast<ARServer*>(ptr);
		return server->readPkt(buf, size);
	}
	int ar_server_write(void* ptr, unsigned char* buf, int size) {
		ARServer* server = reinterpret_cast<ARServer*>(ptr);
		return server->writePkt(buf, size);
	}
	void ar_server_close(void* ptr) {
		ARServer* server = reinterpret_cast<ARServer*>(ptr);
		server->closeClient();
		delete server;
	}

	void* audio_handler_new() {
		return new(std::nothrow) AudioHandler;
	}
	void audio_handler_init(void* ptr) {
		AudioHandler* handler = reinterpret_cast<AudioHandler*>(ptr);
		handler->init(AV_CODEC_ID_WAVPACK, AV_CODEC_ID_AAC, 64000, 16000, 1, AV_SAMPLE_FMT_S16, 1024);
	}
	void audio_handler_get_decoded_pkt(void* ptr, unsigned char* buf, int readLen, unsigned char** data) {
		AudioHandler* handler = reinterpret_cast<AudioHandler*>(ptr);
		handler->getDecodedPkt(buf, readLen, data);
	}
	void audio_free_decoded_pkt(unsigned char** data) {
		delete *data;
	}

	void audio_handler_release(void* ptr) {
		AudioHandler* handler = reinterpret_cast<AudioHandler*>(ptr);
		handler->release();
		delete handler;
	}

	void* video_handler_new() {
		return new(std::nothrow) VideoHandler;
	}
	void video_handler_init(void* ptr) {
		VideoHandler* handler = reinterpret_cast<VideoHandler*>(ptr);
		handler->init(AV_CODEC_ID_H264, 640, 480);
	}
	bool video_handler_get_decoded_pkt(void* ptr, unsigned char* buf, int readLen, unsigned char** data) {
		VideoHandler* handler = reinterpret_cast<VideoHandler*>(ptr);
		int ret = handler->getDecodedPkt(buf, readLen, data);
		if(ret == VIDEO_SUCCESS)
			return true;
		if(ret == VIDEO_DEC_NOT_YET)
			return false;
	}
	void video_free_decoded_pkt(unsigned char** data) {
		delete *data;
	}
	void video_handler_release(void* ptr) {
		VideoHandler* handler = reinterpret_cast<VideoHandler*>(ptr);
		handler->release();
		delete handler;
	}

	void pkt_check(unsigned char* buf, int len, int& flag, unsigned char*& pkt_buf, int& pkt_len) {
		if(buf[0] == 0x00)
			flag = 0;
		else if(buf[0] == 0x01)
			flag = 1;
		
		pkt_buf = buf + 1;
		pkt_len = len - 1;
	}
}
