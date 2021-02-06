#!/usr/bin/env python
# tag-exif.py
import os, sys, time
from exif import Image

def tagExif(parentFolder):
  for dirName, subdirs, fileList in os.walk(parentFolder):
    for filename in fileList:

      if ((len(filename)>1) and (filename[0:2]=='x_')):
        print("SKIPPING %s" %filename)
        continue

      sp =filename.split('.')
      if (len(sp) < 2):
        print("NO EXT for %s" %filename)
        continue

      ext = sp[-1].lower()
      if not (ext in ['jpg']):
        print("SKIP EXT %s for %s" % (ext, filename))
        continue

      path = os.path.join(dirName, filename)
      with open(path, 'rb') as image_file:
        my_image = Image(image_file)

      if (hasattr(my_image, 'has_exif') and my_image.has_exif and hasattr(my_image, 'datetime')):
        dt = my_image.datetime.replace(':','-').replace(' ', '_T')
      else:
        dt = '0000-00-00_T00-00-00'

      # initialize and strip unwanted characters
      new_filename = filename.replace('=','-').replace("'", '').replace('#', '').replace('&','').replace(',', '_').replace(' ', '_')
      # consolidate multiple underscores to single underscore
      new_filename = 'x_' + dt + ' ' +'_'.join(filter(None,new_filename.split('_')))
      print(new_filename)
      new_path = os.path.join(dirName, new_filename)
      os.rename(path, new_path)

  return

if __name__ == '__main__':
    if len(sys.argv) > 1:
        folders = sys.argv[1:]
        for i in folders:
            # Iterate the folders given
            if os.path.exists(i):
                # Find the duplicated files and append them to the dups
                tagExif(i)
            else:
                print('%s is not a valid path, please verify' % i)
                sys.exit()
    else:
        print('Usage: python exif-tag.py folder or python exif-tag.py folder1 folder2 folder3')