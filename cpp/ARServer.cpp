#include "ARServer.hpp"

AR_SVR_ERR ARServer::init(int port) {
	serverSockFd = socket(AF_INET, SOCK_STREAM, 0);
	if(serverSockFd < 0)
		return MS_SVR_CREATE_SOCK_ERR;

	struct sockaddr_in serverAddr;
	bzero(&serverAddr, sizeof(serverAddr));
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	serverAddr.sin_port = htons(port);
	
	int state = bind(serverSockFd, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
	if(state == -1)
		return MS_SVR_BIND_SOCK_ERR;

	state = listen(serverSockFd, 20);
	if(state == -1)
		return MS_SVR_LISTEN_SOCK_ERR;

	clientSockFd = -1;	
	cout << "server initialize success. port is " << port << endl;	
	return MS_SVR_SUCCESS;
}

AR_SVR_ERR ARServer::acceptClient() {
	cout << "wait..." << endl;
	struct sockaddr_in clientAddr;
	int clientLen;
	clientSockFd = accept(serverSockFd, (struct sockaddr*)&clientAddr, (socklen_t*)&clientLen);
	if(clientSockFd == -1)
		return MS_SVR_ACCEPT_SOCK_ERR;
	cout << "client accepted. " << clientSockFd << endl;

	return MS_SVR_SUCCESS;
}

AR_SVR_ERR ARServer::closeClient() {
	if(clientSockFd == -1) {
		int state = close(clientSockFd);
		if(state == -1)
			return MS_SVR_CLOSE_SOCK_ERR;
		else
			return MS_SVR_SUCCESS;
	}
	else
		return MS_SVR_ALREADY_CLOSE_SOCK;
}

int ARServer::readPkt(unsigned char* buf, int size) {
	int readLen = 0;
	while(readLen < 4) {
		int readSize = read(clientSockFd, buf + readLen, 4 - readLen);
		if(readSize < 0)
			return -1;
		
		readLen += readSize;
	}

	readLen = 0;
	int pktLength = int(buf[3] |
			buf[2] << 8 |
			buf[1] << 16 |
			buf[0] << 24);

	//cout << "pktLength: " << pktLength << endl;
	if(pktLength > size)
		return -1;

	while(readLen < pktLength) {
		int readSize = read(clientSockFd, buf + readLen, pktLength - readLen);
		if(readSize < 0)
			return -1;

		readLen += readSize;
	}

	return pktLength;
}

int ARServer::writePkt(unsigned char* buf, int size) {
	int writeLen = 0;
	while(writeLen < size) {
		int writeSize = write(clientSockFd, buf + writeLen, size - writeLen);
		if(writeSize < 0)
			return -1;
		
		writeLen += writeSize;
	}

	return writeLen;
}
