#!/usr/bin/env python
# exif-patch.py
import os, sys, re, pathlib, datetime
from exif import Image

MONTH_DICT = {'jan': '01', 'feb': '02', 'mar': '03', 'apr':'04', 'may':'05', 'jun':'06', 'jul': '07', 'aug':'08', 'sep':'09', 'oct':'10', 'nov':'11', 'dec':'12'}


def getExif(filePath):
  # This function will open the image file at filePath and determine if it has usable EXIF data
  # if it does, it will return the datetime string, else if will return None
  with open(filePath, 'rb') as image_file:
    my_image = Image(image_file)
  # in an image was loaded, check if it includes exif data for datetime
  if ((my_image != None) and hasattr(my_image, 'has_exif') and (my_image.has_exif) and hasattr(my_image, 'datetime')):
    return my_image.datetime
  else:
    return None


def writeExif(fullpath, new_exif, filename):
    # encoded exif data was not found, but it was parsed from the filename
  # attempt to write it to the file
  cmd = f'docker run --rm --mount type=bind,source={fullpath},target=/images exif ./exiftool -alldates="{new_exif}" "/images/{filename}"'
  stream = os.popen(cmd)
  output = stream.read()
  print(f'\t\t{output}')
  #cmd = 'docker run --rm --mount type=bind,source=' + fullpath + f',target=/images exif ./exiftool -DateTimeOriginal "/images/{filename}"'
  #stream = os.popen(cmd)
  #output = stream.read()
  #print(f'\t\t\t{output}')


def renameFile(dirName, orig_filename, new_file_prefix):
  # initialize and strip unwanted characters
  new_filename = orig_filename.replace('=','-').replace("'", '').replace('#', '').replace('&','').replace(',', '_').replace(' ', '_')
  # consolidate multiple underscores to single underscore
  new_filename = new_file_prefix + ' ' + '_'.join(filter(None,new_filename.split('_')))
  orig_path = os.path.join(dirName, orig_filename)
  new_path = os.path.join(dirName, new_filename)
  os.rename(orig_path, new_path)
  return new_filename


def parseDate(filename):
  # this function will scan the filename string and attempt to extract usable date info
  # at a minimum, a year value must be found
  # if a year is found, it will attempt to add a month
  # when both year and month are found, then a day of the month will be looked for, only between the month and year values
  # attempts will be made to look for various combinations of upper case, lower case, and various delimeters

  # look for Month Day Year combination in the filename string
  fz = re.search('[_ .0123456789-](jan|feb|mar|march|apr|april|may|jun|june|jul|july|aug|sep|sept|oct|nov|dec)[_ -.]([0-3]?[0-9])[_ -.](19[0-9][0-9]|20[0-1][0-9])[ _.-]', filename.lower())
  cz = re.search('c(19[0-9][0-9]|20[0-1][0-9])_([0-1]?[0-9])_([0-3]?[0-9])', filename.lower())

  if fz:
    # it was found in format month, day, year - extract the values
    month_val = fz.groups()[0][0:3]
    if (len(fz.groups()[1]) > 1): day_val = fz.groups()[1]
    else: day_val = '0' + fz.groups()[1]
    year_val = fz.groups()[2]
  elif cz:
    # it was found in the format year, month, day - extract the values
    year_val = cz.groups()[0]
    if (len(cz.groups()[1]) > 1): month_val = cz.groups()[1]
    else: month_val = '0' + cz.groups()[1]
    if (len(cz.groups()[2]) > 1): day_val = cz.groups()[2]
    else: day_val = '0' + cz.groups()[2]
  else:
    # if not, we'll never find the day, but will keep looking for year and month, each independently
    day_val = None

    # look for the month string
    mz = re.search('[_ .0123456789-](jan|feb|mar|march|apr|april|may|jun|june|jul|july|aug|sep|sept|oct|nov|dec)[ _.0123456789-]', filename.lower())
    if mz: month_val = mz.groups()[0][0:3]
    else: month_val = None

    # look for the year string
    yz = re.search('[_ .-](19[0-9][0-9]|20[0-1][0-9])[ _.-]', filename)
    if yz: year_val = yz.groups()[0]
    else: year_val = None

  # if a month was found, then convert it to a two digit string value of the month number
  if ((month_val != None) and
      ((fz != None) or (cz == None))): month_val = MONTH_DICT[month_val]

  # return the values, be them what they may - each may be None or be a string value
  return year_val, month_val, day_val


def subDate(filepath, filename):
  # SECOND CHOICE: Try to parse the date from the filename
  # THIRD CHOICE: Try to mash up the date from the filename and OS file creation date, if they align
  # grab the OS datetime stamp the file was created
  fname = pathlib.Path(filepath)
  mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
#  ct_yr = str(mtime.year)
#  ct_mo = str(mtime.month)
#  ct_dy = str(mtime.day)
  ct_yr = f'{mtime.year:04d}'
  ct_mo = f'{mtime.month:02d}'
  ct_dy = f'{mtime.day:02d}'

  yr, mo, dy = parseDate(filename) 
  if (yr == None):
    # no usable date info found in filename string, use the OS file date
    new_file_prefix = f'f_{ct_yr}-{ct_mo}-{ct_dy}_T00-00-00'
    new_exif = f'{ct_yr}:{ct_mo}:{ct_dy} 00:00:00'

  else:
    # filename at least had a year, mash up month and day with OS file create if necessary
    if (mo != None):
      # year and month info found in filename, use it
      mo_filename = mo
      mo_exif = mo
    elif (yr == ct_yr):
      # year was found in filename but month was not
      # and filename year matches OS file create year, so use the OS file create month
      mo_filename = ct_mo
      mo_exif = ct_mo
    else:
      # year was found in filename but month was not
      # and worse yet, filename year does not match OS file create year, punt
      mo_filename = '00'
      mo_exif = '01'

    if (dy != None):
      # year and day info found in filename, use it
      dy_filename = dy
      dy_exif = dy
    elif ((yr == ct_yr) and (mo == ct_mo)):
      # year was found in filename but day was not
      # and filename year matches OS file create year, so use the OS file create day
      dy_filename = ct_dy
      dy_exif = ct_dy
    else:
      # year was found in filename but month or day was not
      # and worse yet, filename year does not match OS file create year, or filename month does not match OS file year, so punt
      dy_filename = '00'
      dy_exif = '01'

    # craft the new file prefix from the parsed year, month and day. Set midnight time placeholders
    new_file_prefix = 'n_' + f'{yr}-{mo_filename}-{dy_filename}_T00-00-00'
    new_exif = f'{yr}:{mo_exif}:{dy_exif} 00:00:00'

  return new_file_prefix, new_exif


def tagExif(parentFolder):
  # this function will make every attempt to tag exif datetime within the exif data and in the filename
  # FIRST, it looks to see if exif data is already encoded, if so then that data is used to rename the file
  # SECOND, if no exif data is encoded, then it attempts to parse the date time from the filename
  #         if datetime data is found in the filename, then it is encoded into the file exif data
  # FINALLY, all files are append with the best available date-time prefix info
  #         files that had exif data are prefixed with x_YYYY-MM-DD_THH:MM:SS
  #         without exif data, filename is parsed and prefixed with n_YYYY-MM-DD_T00:00:00

  for dirName, subdirs, fileList in os.walk(parentFolder):

    fullpath = os.path.abspath(dirName)
    for filename in fileList:

      # skip this file if it has already been processed
      if ((len(filename)<2) or (filename[0:2] in ['x_', 'n_', 'f_'])): continue

      # skip this file if it doesn't have a supported file extension
      sp = filename.split('.')
      if ((len(sp) < 2) or not (sp[-1].lower() in ['jpg'])): continue

      # FIRST CHOICE, see if the file already contains encoded exif date and time
      print("Checking: %s" %filename)
      filepath = os.path.join(dirName, filename)
      exif_datetime = getExif(filepath)

      if (exif_datetime != None):
        # exif datetime was found
        new_file_prefix = 'x_' + exif_datetime.replace(':','-').replace(' ', '_T')

      else:
        # get a mashup of date from filename and OS file timestamp
        new_file_prefix, new_exif = subDate(filepath, filename)
        # encode substitute exif data into the file
        writeExif(fullpath, new_exif, filename)

      # append the new prefix in front of the existing filename
      new_name = renameFile(dirName, filename, new_file_prefix)
      print (f'\t{new_name}')
    # end For Filename
  # end For parentFolder
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