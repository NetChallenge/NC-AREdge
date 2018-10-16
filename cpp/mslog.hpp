#pragma once
#include <iostream>
#include <fstream>
extern "C" {
#include <libavutil/avutil.h>
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
}
using namespace std;

namespace MSLOG {
	enum LOG_TYPE {
		PRINT,
		WARNING,
		ERROR
	};
	
	inline string makeMsg(string msg, int type) {
		char printBuf[200];

		int idx=0;
		time_t timeVal = time(NULL);
		struct tm tm = *localtime(&timeVal);

		idx += sprintf(printBuf, "[%d-%d-%d %d:%d:%d]",
		tm.tm_year + 1900,
		tm.tm_mon + 1,
		tm.tm_mday,
		tm.tm_hour,
		tm.tm_min,
		tm.tm_sec);

		switch(type) {
		case PRINT:
			sprintf(printBuf+idx, " : %s\n", msg.c_str());
			break;
		case WARNING:
			sprintf(printBuf+idx, " WARNING: %s\n", msg.c_str());
			break;
		case ERROR:
			sprintf(printBuf+idx, " ERROR: %s\n", msg.c_str());//, strerror(errno));
			break;
		}

		return string(printBuf);
	}
	
	inline void printError(string filename, string msg) {
		string output = makeMsg(msg, ERROR);
#ifndef LOG
		ofstream outf(filename);
		outf << output << endl;
		outf.close();
#endif
		cout << output << endl;
	}

	inline void printWarning(string filename, string msg) {
		string output = makeMsg(msg, WARNING);
#ifndef LOG
		ofstream outf(filename);
		outf << output << endl;
		outf.close();
#endif
		cout << output << endl;
	}

	inline void printErrorFFmpeg(string filename, string msg, int num) {
		char errBuf[128];

		string output = makeMsg(msg, ERROR);
		av_strerror(num, errBuf, sizeof(errBuf));

#ifndef LOG
		ofstream outf(filename);
		outf << output << " " << errBuf << endl;
		outf.close();
#endif
		cout << output << " " << errBuf << endl;
	}

	inline void printWarningFFmpeg(string filename, string msg, int num) {
		char errBuf[128];
		
		string output = makeMsg(msg, WARNING);
		av_strerror(num, errBuf, sizeof(errBuf));

#ifndef LOG
		ofstream outf(filename);
		outf << output << " " << errBuf << endl;
		outf.close();
#endif
		cout << output << " " << errBuf << endl;
	}

	inline void printConsole(string msg) {
#ifndef DEBUG
		makeMsg(msg, PRINT);
		cout << msg;
#endif
	}
}
