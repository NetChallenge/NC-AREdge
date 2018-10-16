apt-get -y update <br />
apt-get insatll git vim g++ yasm make  <br />
cd /root <br />
git clone https://github.com/FFmpeg/FFmpeg.git <br />
cd FFmpeg <br />
./configure --enable-shared --disable-static --disable-everything --enable-muxer=wav,adts --enable-encoder=pcm_s16le --enable-decoder=aac --enable-decoder=h264 <br />
make -j100 <br />
make install <br />
cd .. <br />
rm -rf FFmpeg <br />
