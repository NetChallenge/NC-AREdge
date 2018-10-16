g++ -c portingPython.cpp ARServer.cpp VideoHandler.cpp AudioHandler.cpp -std=c++11 -fPIC
g++ -shared -Wl,-soname,libarserver.so ARServer.o VideoHandler.o AudioHandler.o portingPython.o -lpthread -lavformat -lavcodec -lavutil -o libarserver.so
