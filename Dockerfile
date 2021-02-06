FROM ubuntu
RUN apt-get update && apt-get install -y \
  gzip \
  make \
  perl \
  wget 
RUN wget https://exiftool.org/Image-ExifTool-12.12.tar.gz
RUN gzip -dc Image-ExifTool-12.12.tar.gz | tar -xf -
WORKDIR /Image-ExifTool-12.12
RUN perl Makefile.PL
RUN make test
RUN make install
VOLUME /images
CMD /bin/bash