#pragma once
#include <iostream>
#include "mslog.hpp"
extern "C" {
#include <libavutil/avutil.h>
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
}
using namespace std;

enum VIDEO_HDR_ERR {
	VIDEO_SUCCESS,
	VIDEO_DEC_FIND_ERR,
	VIDEO_DEC_ALLOC_CTX_ERR,
	VIDEO_DEC_OPEN_CODEC_ERR,
	VIDEO_DEC_PKT_ALLOC_ERR,
	VIDEO_DEC_FRAME_ALLOC_ERR,
	VIDEO_DEC_NOT_YET
};

class VideoHandler {
public:
	VIDEO_HDR_ERR init(AVCodecID decoderCodec, int videoWidth, int videoHeight);
	VIDEO_HDR_ERR getDecodedPkt(uint8_t* buf, int size, uint8_t** data);
	void freeDecodedPkt(uint8_t** data);
	void release();

private:
	//for decoder
	AVCodec* decCodec;
	AVCodecContext* decCodecCtx;
	AVPacket* decPkt;
	AVFrame* decFrame;

	int width;
	int height;
};
