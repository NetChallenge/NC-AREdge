#include "AudioHandler.hpp"

AUDIO_HDR_ERR AudioHandler::init(AVCodecID rawCodecID, AVCodecID decCodecID, int bitRate, int sampleRate, int channels, AVSampleFormat sampleFmt, int samplesPerFrame) {
        //for raw
        rawOutFmtCtx = avformat_alloc_context();
        //avformat_alloc_output_context2(&rawOutFmtCtx, NULL, NULL, NULL);
        if(!rawOutFmtCtx)
                return AUDIO_RAW_ALLOC_OUTPUT_CTX_ERR;

        rawCodec = avcodec_find_encoder(rawCodecID);
        if(!rawCodec)
                return AUDIO_RAW_FIND_ERR;

        rawStream = avformat_new_stream(rawOutFmtCtx, NULL);
        if(!rawStream)
                return AUDIO_RAW_NEW_STREAM_ERR;

        rawCodecCtx = avcodec_alloc_context3(rawCodec);
        if(!rawCodecCtx)
                return AUDIO_RAW_ALLOC_CTX_ERR;
        rawCodecCtx->sample_rate = sampleRate;
        rawCodecCtx->time_base = (AVRational){1, sampleRate};
        rawStream->time_base = rawCodecCtx->time_base;
        rawCodecCtx->channels = channels;
        rawCodecCtx->channel_layout = av_get_default_channel_layout(channels);
        rawCodecCtx->sample_fmt = sampleFmt;

        if(avcodec_open2(rawCodecCtx, rawCodec, NULL) < 0)
                return AUDIO_RAW_OPEN_CODEC_ERR;

        if(avcodec_parameters_from_context(rawStream->codecpar, rawCodecCtx) < 0)
                return AUDIO_RAW_PARAM_FROM_CTX_ERR;

        if(avformat_write_header(rawOutFmtCtx, NULL) < 0)
		return AUDIO_RAW_WRITE_HEADER_ERR;

	rawPkt = av_packet_alloc();
	if(!rawPkt)
		return AUDIO_RAW_PKT_ALLOC_ERR;	

	//for decoder
	decCodec = avcodec_find_decoder(decCodecID);
	if(!decCodec)
		return AUDIO_DEC_FIND_ERR;

	decCodecCtx = avcodec_alloc_context3(decCodec);
	if(!decCodecCtx)
		return AUDIO_DEC_ALLOC_CTX_ERR;
	decCodecCtx->sample_rate = sampleRate;
	decCodecCtx->time_base = (AVRational){1, sampleRate};
	decCodecCtx->channels = channels;
	decCodecCtx->channel_layout = av_get_default_channel_layout(channels);
	decCodecCtx->sample_fmt = sampleFmt;

	if(avcodec_open2(decCodecCtx, decCodec, NULL) < 0)
		return AUDIO_DEC_OPEN_CODEC_ERR;

	decPkt = av_packet_alloc();
	if(!decPkt)
		return AUDIO_DEC_PKT_ALLOC_ERR;

	decFrame = av_frame_alloc();
	if(!decFrame)
		return AUDIO_DEC_FRAME_ALLOC_ERR;

	audioPts = 0;
	spf = samplesPerFrame;
	return AUDIO_SUCCESS;
}

AUDIO_HDR_ERR AudioHandler::getDecodedPkt(uint8_t* buf, int size, uint8_t** data) {
	decPkt->data = buf;
        decPkt->size = size;
        decPkt->duration = spf * 1000 / decCodecCtx->sample_rate;
        decPkt->pts = decPkt->dts = audioPts;

        //add pts
        audioPts += spf;

        int ret = avcodec_send_packet(decCodecCtx, decPkt);
        if(ret < 0) {
		return AUDIO_DEC_NOT_YET;
                //MSLOG::printErrorFFmpeg("logFile.log", "send packet", ret);
                //exit(1);
        }

        while(ret >= 0) {
                ret = avcodec_receive_frame(decCodecCtx, decFrame);
                if(ret == AVERROR(EAGAIN) || ret == AVERROR_EOF)
                        break;
                else if(ret < 0) {
                        MSLOG::printError("logFile.log", "decoding audio");
                        exit(1);
                }
	
		/*
                rawPkt->data = decFrame->data[0];
                rawPkt->size = decFrame->linesize[0];
                if(av_write_frame(rawOutFmtCtx, rawPkt) < 0)
                        return MS_RAW_WRITE_FRAME_ERR;
		*/

		memcpy(*data, rawPkt->data, spf);
		break;
        }
	return AUDIO_SUCCESS;
}

void AudioHandler::freeDecodedPkt(uint8_t** data) {
	delete *data;
}

void AudioHandler::release() {
	//for raw
        if(!rawOutFmtCtx)
                av_write_trailer(rawOutFmtCtx);
        if(!rawCodecCtx)
                avcodec_free_context(&rawCodecCtx);
        if(!rawOutFmtCtx && !rawOutFmtCtx->pb)
                avio_closep(&rawOutFmtCtx->pb);
        if(!rawOutFmtCtx)
                avformat_free_context(rawOutFmtCtx);
	if(!rawPkt)
		av_packet_free(&rawPkt);

	//for decoder
	if(decCodecCtx)
		avcodec_free_context(&decCodecCtx);
	if(!decFrame)
		av_frame_free(&decFrame);
	if(!decPkt)
		av_packet_free(&decPkt);

	audioPts = 0;
	spf = 0;
}

