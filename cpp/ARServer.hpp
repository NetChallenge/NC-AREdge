#pragma once
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <iostream>

using namespace std;

enum AR_SVR_ERR {
	MS_SVR_SUCCESS,
	MS_SVR_CREATE_SOCK_ERR,
	MS_SVR_BIND_SOCK_ERR,
	MS_SVR_LISTEN_SOCK_ERR,
	MS_SVR_ACCEPT_SOCK_ERR,
	MS_SVR_CLOSE_SOCK_ERR,
	MS_SVR_ALREADY_CLOSE_SOCK
};

class ARServer {
public:
	AR_SVR_ERR init(int port);
	AR_SVR_ERR acceptClient();
	AR_SVR_ERR closeClient();
	int readPkt(unsigned char* buf, int size);
	int writePkt(unsigned char* buf, int size);
private:
	int serverSockFd;
	int clientSockFd;
};
