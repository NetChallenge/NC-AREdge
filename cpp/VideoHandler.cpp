#include "VideoHandler.hpp"

VIDEO_HDR_ERR VideoHandler::init(AVCodecID decoderCodec, int videoWidth, int videoHeight) {
	//for decoder
	decCodec = avcodec_find_decoder(decoderCodec);
	if(!decCodec)
		return VIDEO_DEC_FIND_ERR;

	decCodecCtx = avcodec_alloc_context3(decCodec);
	if(!decCodecCtx)
		return VIDEO_DEC_ALLOC_CTX_ERR;

	if(avcodec_open2(decCodecCtx, decCodec, NULL) < 0)
		return VIDEO_DEC_OPEN_CODEC_ERR;

	decPkt = av_packet_alloc();
	if(!decPkt)
		return VIDEO_DEC_PKT_ALLOC_ERR;

	decFrame = av_frame_alloc();
	if(!decFrame)
		return VIDEO_DEC_FRAME_ALLOC_ERR;

	width = videoWidth;
	height = videoHeight;

	return VIDEO_SUCCESS;
}

VIDEO_HDR_ERR VideoHandler::getDecodedPkt(uint8_t* buf, int size, uint8_t** data) {
        decPkt->data = buf;
        decPkt->size = size;

        int ret = avcodec_send_packet(decCodecCtx, decPkt);
	if(ret < 0) {
		return VIDEO_DEC_NOT_YET;
		//MSLOG::printErrorFFmpeg("logFile.log", "send packet", ret);
                //exit(1);
        }

	ret = avcodec_receive_frame(decCodecCtx, decFrame);
	if(ret == AVERROR(EAGAIN) || ret == AVERROR_EOF)
		return VIDEO_DEC_NOT_YET;
	else if(ret < 0) {
		MSLOG::printError("logFile.log", "decoding video");
		exit(1);
	}

	memcpy(*data, decFrame->data[0], width * height);
	memcpy(*data + width * height, decFrame->data[2], width * height / 4);
	memcpy(*data + width * height * 5 / 4, decFrame->data[1], width * height / 4);

	return VIDEO_SUCCESS;
}

void VideoHandler::freeDecodedPkt(uint8_t** data) {
	delete *data;
}

void VideoHandler::release() {
	//for decoder
	if(decCodecCtx)
		avcodec_free_context(&decCodecCtx);
	if(!decFrame)
		av_frame_free(&decFrame);
	if(!decPkt)
		av_packet_free(&decPkt);
}

