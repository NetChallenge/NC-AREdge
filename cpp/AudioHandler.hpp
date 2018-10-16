#pragma once
#include <iostream>
#include "mslog.hpp"
extern "C" {
#include <libavutil/avutil.h>
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
}
using namespace std;

enum AUDIO_HDR_ERR {
	AUDIO_SUCCESS,
        AUDIO_RAW_ALLOC_OUTPUT_CTX_ERR,
        AUDIO_RAW_FIND_ERR,
        AUDIO_RAW_NEW_STREAM_ERR,
        AUDIO_RAW_ALLOC_CTX_ERR,
        AUDIO_RAW_OPEN_CODEC_ERR,
        AUDIO_RAW_PARAM_FROM_CTX_ERR,
        AUDIO_RAW_OPEN_AVIO_ERR,
        AUDIO_RAW_WRITE_HEADER_ERR,
	AUDIO_RAW_PKT_ALLOC_ERR,
	AUDIO_RAW_WRITE_FRAME_ERR,
	AUDIO_DEC_FIND_ERR,
	AUDIO_DEC_ALLOC_CTX_ERR,
	AUDIO_DEC_OPEN_CODEC_ERR,
	AUDIO_DEC_PKT_ALLOC_ERR,
	AUDIO_DEC_FRAME_ALLOC_ERR
};

class AudioHandler {
public:
	AUDIO_HDR_ERR init(AVCodecID rawCodecID, AVCodecID decCodecID, int bitRate, int sampleRate, int channels, AVSampleFormat sampleFmt, int samplesPerFrame);
	AUDIO_HDR_ERR getDecodedPkt(uint8_t* buf, int size, uint8_t** data);
	void freeDecodedPkt(uint8_t** data);
	void release();

private:
        //for raw
        AVFormatContext* rawOutFmtCtx;
        AVCodec* rawCodec;
        AVStream* rawStream;
        AVCodecContext* rawCodecCtx;
	AVPacket* rawPkt;
	
	//for decoder
	AVCodec* decCodec;
	AVCodecContext* decCodecCtx;
	AVPacket* decPkt;
	AVFrame* decFrame;

	int audioPts;
	int spf; //samples per frame
};
