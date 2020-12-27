import logging
from imageio.core.functions import mimwrite

#libraries for homeassistant setup service
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

#libraries need for custom code
from PIL import Image
import os
import time
import datetime
import imageio

DOMAIN ='snaptogif'

_LOGGER = logging.getLogger(__name__)

SERVICE_START = 'start'

SERVICE_PARAM_SOURCE='sourcepath'
SERVICE_PARAM_DESTINATION='destinationpath'
SERVICE_PARAM_FILENAME='filename'
SERVICE_PARAM_FORMAT='format'
SERVICE_PARAM_EXCLUDE='excludelist'
SERVICE_PARAM_BEGINTIME='begintimestamp'
SERVCE_PARAM_ENDTIME='endtimestamp'

SNAPTOGIF_START_SCHEMA = vol.Schema(			
    {
        vol.Required(SERVICE_PARAM_SOURCE): cv.isdir,
		vol.Required(SERVICE_PARAM_DESTINATION): cv.isdir,
		vol.Optional(SERVICE_PARAM_FILENAME,default='latest'):cv.matches_regex(r'^[^<>:;,.?"*|/\\]+$'),
		vol.Optional(SERVICE_PARAM_FORMAT,default='gif'):vol.In(['gif','mp4']),
		vol.Optional(SERVICE_PARAM_EXCLUDE,default=[]):cv.ensure_list_csv,
		vol.Optional(SERVICE_PARAM_BEGINTIME,default=''):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(SERVCE_PARAM_ENDTIME,default=''):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
    }
	)

def setup(hass, config):
    #Set up is called when Home Assistant is loading our component.
    
	def validateTimestamp(date_text):
		try:
			datetime.datetime.strptime(date_text, '%d/%m/%Y %H:%M:%S')
		except ValueError:
			raise ValueError("Incorrect data format, should be DD/MM/YYYY HH:MM:SS")
		return date_text

	def GetTimestampFile(path,file):
		return (os.path.getmtime(os.path.join(path, file)))

	
	def SnapToGIF(call):
		
		#get files in source path
		folder=call.data[SERVICE_PARAM_SOURCE]
		files=os.listdir(folder)
		fpout=call.data[SERVICE_PARAM_DESTINATION]
		#only jpg files and filter out latest
		files=[file for file in files if ".jpg" in file and file not in call.data[SERVICE_PARAM_EXCLUDE]]
		
		#convert timestrings to epoch time
		if call.data[SERVICE_PARAM_BEGINTIME]!="":
			BeginTimestamp=time.mktime(datetime.datetime.strptime(call.data[SERVICE_PARAM_BEGINTIME], "%d/%m/%Y %H:%M:%S").timetuple())
		if 	call.data[SERVCE_PARAM_ENDTIME]!="":
			EndTimeStamp=time.mktime(datetime.datetime.strptime(call.data[SERVCE_PARAM_ENDTIME], "%d/%m/%Y %H:%M:%S").timetuple())
			
		#filter files with specified time filters		
		#Begin en End is given
		if call.data[SERVICE_PARAM_BEGINTIME]!='' and call.data[SERVCE_PARAM_ENDTIME]!='':
			files=[file for file in files if GetTimestampFile(folder,file)>=BeginTimestamp and GetTimestampFile(folder,file)<=EndTimeStamp ]
		#Only begintimestamp is given
		if call.data[SERVICE_PARAM_BEGINTIME]!='' and call.data[SERVCE_PARAM_ENDTIME]=='':
			files=[file for file in files if GetTimestampFile(folder,file)>=BeginTimestamp]
		#Only endtimestamp is given
		if call.data[SERVICE_PARAM_BEGINTIME]=='' and call.data[SERVCE_PARAM_ENDTIME]!='':
			files=[file for file in files if GetTimestampFile(folder,file)<=EndTimeStamp ]
		
		_LOGGER.debug(f'No of images found for snapshot {len(files)}')
		
		if len(files)>0:		
			#convert selected range to selected format
			outputfile=f'{call.data[SERVICE_PARAM_FILENAME]}.{call.data[SERVICE_PARAM_FORMAT]}'
			try:
				
				#sort images on modified date
				files.sort(key=lambda x:os.path.getmtime(os.path.join(folder, x)))
				#convert frames to destination format (GIF/MP3)
				writer = imageio.get_writer(os.path.join(fpout,outputfile),mode='I',fps=1)
				for file in files:
					writer.append_data(imageio.imread(os.path.join(folder,file)))
				writer.close()	

				_LOGGER.info(f'{outputfile} succesfully generated in: {fpout}')
				eventdata={ 'Type': 'gif_created',
							'file': outputfile,
							'Path': fpout,
							'BeginTimeStamp': call.data[SERVICE_PARAM_BEGINTIME],
							'EndTimeStamp': call.data[SERVCE_PARAM_ENDTIME],
							'NoComposedImages': len(files),
							'sourcepath': folder,
							'sourcefiles': files
            				}
				hass.bus.fire(DOMAIN, eventdata)			
			except Exception as e:
				_LOGGER.warning(f"Not able to store {outputfile} on given destination: {fpout} error:{str(e)}")
		else:
			_LOGGER.warning(f"No files found in the specified time range: [{call.data[SERVICE_PARAM_BEGINTIME]} , {call.data[SERVCE_PARAM_ENDTIME]}] in :{folder}")		

	#register service to homeassistant
	hass.services.register(
		DOMAIN, SERVICE_START, SnapToGIF,
		schema=SNAPTOGIF_START_SCHEMA)
	# Return boolean to indicate that initialization was successfully.
	return True
