import logging

#libraries for homeassistant setup service
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

#libraries need for custom code
from PIL import Image
import os
import shutil
import time
import datetime
import imageio

DOMAIN ='snaptogif'

_LOGGER = logging.getLogger(__name__)

SERVICE_START = 'start'
SERVICE_DEL= 'delete'
SERVICE_MOVE= 'move'

SERVICE_PARAM_SOURCE='sourcepath'
SERVICE_PARAM_DESTINATION='destinationpath'
SERVICE_PARAM_FILENAME='filename'
SERVICE_PARAM_FORMAT='format'
SERVICE_PARAM_EXCLUDE='excludelist'
SERVICE_PARAM_BEGINTIME='begintimestamp'
SERVCE_PARAM_ENDTIME='endtimestamp'
EPOCH_START='01/01/1970 00:00:00'

SNAPTOGIF_START_SCHEMA = vol.Schema(			
    {
        vol.Required(SERVICE_PARAM_SOURCE): cv.isdir,
		vol.Required(SERVICE_PARAM_DESTINATION): cv.isdir,
		vol.Optional(SERVICE_PARAM_FILENAME,default='latest'):cv.matches_regex(r'^[^<>:;,.?"*|/\\]+$'),
		vol.Optional(SERVICE_PARAM_FORMAT,default='gif'):vol.In(['gif','mp4']),
		vol.Optional(SERVICE_PARAM_EXCLUDE,default=[]):cv.ensure_list_csv,
		vol.Optional(SERVICE_PARAM_BEGINTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(SERVCE_PARAM_ENDTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
    }
	)

SNAPTOGIF_DEL_SCHEMA = vol.Schema(			
    {
        vol.Required(SERVICE_PARAM_SOURCE): cv.isdir,
		vol.Optional(SERVICE_PARAM_EXCLUDE,default=[]):cv.ensure_list_csv,
		vol.Optional(SERVICE_PARAM_BEGINTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(SERVCE_PARAM_ENDTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
    }
	)
SNAPTOGIF_MOVE_SCHEMA = vol.Schema(			
    {
        vol.Required(SERVICE_PARAM_SOURCE): cv.isdir,
		vol.Required(SERVICE_PARAM_DESTINATION): cv.string,
		vol.Optional(SERVICE_PARAM_EXCLUDE,default=[]):cv.ensure_list_csv,
		vol.Optional(SERVICE_PARAM_BEGINTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(SERVCE_PARAM_ENDTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
    }
	)

def createOutputfile(hass,call,files):
	#convert selected range to selected format
			inputfolder=call.data[SERVICE_PARAM_SOURCE]
			outputfile=f'{call.data[SERVICE_PARAM_FILENAME]}.{call.data[SERVICE_PARAM_FORMAT]}'
			outputfolder=call.data[SERVICE_PARAM_DESTINATION]
			try:
				#sort images on modified date
				files.sort(key=lambda x:os.path.getmtime(os.path.join(inputfolder, x)))
				#convert frames to destination format (GIF/MP3)
				writer = imageio.get_writer(os.path.join(outputfolder,outputfile),mode='I',fps=1)
				for file in files:
					writer.append_data(imageio.imread(os.path.join(inputfolder,file)))
				writer.close()	

				_LOGGER.info(f'{outputfile} succesfully generated in: {outputfolder}')
				eventdata={ 'type': SERVICE_START,
							'file': outputfile,
							'path': outputfolder,
							'beginTimeStamp': call.data[SERVICE_PARAM_BEGINTIME],
							'endTimeStamp': call.data[SERVCE_PARAM_ENDTIME],
							'no_files': len(files),
							'sourcepath': inputfolder,
							'sourcefiles': files
            				}
				hass.bus.fire(DOMAIN, eventdata)			
			except Exception as e:
				_LOGGER.warning(f"Not able to store {outputfile} on given destination: {outputfolder} error:{str(e)}")

def deletefiles(hass,call,files):
	#remove selected files
	inputfolder=call.data[SERVICE_PARAM_SOURCE]
	try: 
		for file in files:
		  os.remove(os.path.join(inputfolder,file))
		_LOGGER.info(f'Files succesfully removed from: {inputfolder}')
		eventdata={ 'type': SERVICE_DEL,
					'beginTimeStamp': call.data[SERVICE_PARAM_BEGINTIME],
					'endTimeStamp': call.data[SERVCE_PARAM_ENDTIME],
					'no_files': len(files),
					'sourcepath': inputfolder,
					'sourcefiles': files
   				}
		hass.bus.fire(DOMAIN, eventdata)
	except Exception as e:
		_LOGGER.warning(f"Error deleting selected files on given destination: {inputfolder}\nerror:{str(e)}")

def movefiles(hass,call,files):
	#move selected files
	inputfolder=call.data[SERVICE_PARAM_SOURCE]
	outputfolder=call.data[SERVICE_PARAM_DESTINATION]
	try: 
		#create directory if not exist
		if not os.path.exists(outputfolder):
			os.makedirs(outputfolder)
		for file in files:
		  shutil.move(os.path.join(inputfolder,file),outputfolder)
		_LOGGER.info(f'Files succesfully moved from: {inputfolder} to {outputfolder}')
		eventdata={ 'type': SERVICE_MOVE,
					'beginTimeStamp': call.data[SERVICE_PARAM_BEGINTIME],
					'endTimeStamp': call.data[SERVCE_PARAM_ENDTIME],
					'no_files': len(files),
					'sourcepath': inputfolder,
					'destinationpath': outputfolder,
					'sourcefiles': files
   				}
		hass.bus.fire(DOMAIN, eventdata)
	except Exception as e:
		_LOGGER.warning(f"Error moveing selected files on given source: {inputfolder}  to destination: {outputfolder}\nerror:{str(e)}")

def setup(hass, config):
    #Set up is called when Home Assistant is loading our component.
    	
	def GetTimestampFile(path,file):
		return (os.path.getmtime(os.path.join(path, file)))
	
	def SnapToGIF(call):
		
		#get files in source path
		folder=call.data[SERVICE_PARAM_SOURCE]
		files=os.listdir(folder)
		
		#only jpg files and filter out latest
		files=[file for file in files if ".jpg" in file and file not in call.data[SERVICE_PARAM_EXCLUDE]]
		
		#convert timestrings to epoch time
		BeginTimestamp=0
		EndTimeStamp=0
		if call.data[SERVICE_PARAM_BEGINTIME]!=EPOCH_START:
			BeginTimestamp=time.mktime(datetime.datetime.strptime(call.data[SERVICE_PARAM_BEGINTIME], "%d/%m/%Y %H:%M:%S").timetuple())
		if 	call.data[SERVCE_PARAM_ENDTIME]!=EPOCH_START:
			EndTimeStamp=time.mktime(datetime.datetime.strptime(call.data[SERVCE_PARAM_ENDTIME], "%d/%m/%Y %H:%M:%S").timetuple())
			
		#filter files with specified time filters		
		#Begin en End is given
		if call.data[SERVICE_PARAM_BEGINTIME]!=EPOCH_START and call.data[SERVCE_PARAM_ENDTIME]!=EPOCH_START:
			files=[file for file in files if GetTimestampFile(folder,file)>=BeginTimestamp and GetTimestampFile(folder,file)<=EndTimeStamp ]
		#Only begintimestamp is given
		if call.data[SERVICE_PARAM_BEGINTIME]!=EPOCH_START and call.data[SERVCE_PARAM_ENDTIME]==EPOCH_START:
			files=[file for file in files if GetTimestampFile(folder,file)>=BeginTimestamp]
		#Only endtimestamp is given
		if call.data[SERVICE_PARAM_BEGINTIME]==EPOCH_START and call.data[SERVCE_PARAM_ENDTIME]!=EPOCH_START:
			files=[file for file in files if GetTimestampFile(folder,file)<=EndTimeStamp ]
		
		_LOGGER.debug(f'No of images found for snapshot {len(files)}')
		
		#Call the corresponding service
		if len(files)>0:		
			if call.service==SERVICE_START:
			  createOutputfile(hass,call,files)
			elif call.service==SERVICE_DEL:
			  deletefiles(hass,call,files)  
			elif call.service==SERVICE_MOVE:
			  movefiles(hass,call,files)  
		else:
			_LOGGER.warning(f"No files found in the specified time range: [{call.data[SERVICE_PARAM_BEGINTIME]} , {call.data[SERVCE_PARAM_ENDTIME]}] in :{folder}")		

	#register services to homeassistant
	hass.services.register(
		DOMAIN, SERVICE_START, SnapToGIF,
		schema=SNAPTOGIF_START_SCHEMA)
	hass.services.register(
		DOMAIN, SERVICE_DEL, SnapToGIF,
		schema=SNAPTOGIF_DEL_SCHEMA)	
	hass.services.register(
		DOMAIN, SERVICE_MOVE, SnapToGIF,
		schema=SNAPTOGIF_MOVE_SCHEMA)		
	# Return boolean to indicate that initialization was successfully.
	return True
