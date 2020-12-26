# snaptogif
Homeassistant custom component for converting snapshots (jpg) to a gif or mp4
****
This component is developped by my need of creating a GIF of MP4 file from snapshot images that are created by the deepstack custom component. The component is designed for general use of converting snapshot to GIF or MP4, so it is useful for everyone who has to handle or deal with snapshots created by cameras of image processing software.

To use this component, copy the directory `snaptogif`and it contents to the `custom_components` directory of your homeassistant.

Add the following line in your `configuration.yaml:`
```yaml
snaptogif:
```
Restart home-assistant after this.

If the custom component is installed correctly you should have a service called : `snaptogif.start`

This could be easily found under the development tools, tab services.

###### Usage:

The service has to be called with the following calll-parameters:



| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath  |  	path of the directory where the snaphots are in | mandatory  |
|  destinationpath |  path of the directory where the GIF should be created |  mandatory |
|  filename |	Name for gif/mp3 file (without extension)   | optional, default=latest  |
|  format |  `gif` or `mp4` |   |
| excludelist  |  list of files to exclude in conversion |optional, default=`gif`   |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy'   |

# File selection
With the parameter `excludelist` you could **exclude** certain files that should not be added in the created output file (gif or mp4)
Most solutions create a timestamped snapshot file and also a snapshot file with a fixed filename.  I most cases you want to exclude such a file in the output file.

##### Time range selection
The begin and end timestamps are useful for selecting the snapshot files you want within a certain timeframe (**creation time of the file**). 
The combination of both timestamps will have a different filter behaviour

`begintimestamp` and `endtimestamp `defined:
Files with **creation time** within the give range  [`begintimestamp`,`endtimestamp`] wil be selected and proccesed for the output file.

Only `begintimestamp` is defined:
Files with **creation time** greate or equal then `begintimestamp`wil be selected and proccesed for the output file.

Only `endtimestamp` is defined:
Files with **creation time** less or equal then `endtimestamp`wil be selected and proccesed for the output file.

Example for usage:


| Parameter  |Value   |
| ------------ | ------------ |
| sourcepath:  |  \config\snapshots\oprit |
| destinationpath:  | \config\www  |
| gifname:   |latest_oprit   |
|  begintimestamp | '12-25-2020 23:24:24'  |
| endtimestamp: | '12-25-2020 23:24:40  |
