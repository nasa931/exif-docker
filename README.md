Docker EXIF

(image) troy@Troys-MacBook-Pro NTC % pip list
Package    Version
---------- -------
exif       1.0.4
pip        20.3.1
plum-py    0.3.1
setuptools 40.8.0


docker build -t exif .

docker images

docker run -it --mount type=bind,source=/Users/troy/NTC/image/images,target=/images --name exif exif

docker start -i exif

docker exec exif ./exiftool -s /images/x_0000-00-00_T00-00-00\ Carries_visitation_June_18_2008_054.jpg

docker exec exif ./exiftool -CreateDate="2018:06:18 00:00:00" /images/x_0000-00-00_T00-00-00\ Carries_visitation_June_18_2008_054.jpg


docker run -d --rm --mount type=bind,source=/Users/troy/NTC/image/images,target=/images --name exif exif ./exiftool -CreateDate="2018:06:18 00:00:00" /images/x_0000-00-00_T00-00-00\ Carries_visitation_June_18_2008_054.jpg

docker run -d --rm --mount type=bind,source=/Users/troy/NTC/image/images,target=/images --name exif exif ./exiftool -alldates="2018:06:18 00:00:00" /images/x_0000-00-00_T00-00-00\ Carries_visitation_June_18_2008_054.jpg

