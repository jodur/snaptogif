# snaptogif
Homeassistant custom component for converting snapshots (jpg) to a gif or mp4
****
This component is developed by my need of creating a GIF of MP4 file from snapshot images that are created by the deepstack custom component. The component is designed for general use of converting snapshot to GIF or MP4, so it is useful for everyone who has to handle or deal with snapshots created by cameras of image processing software.

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
|  format |  `gif` or `mp4` | optional, default='gif'   |
| excludelist  |  list of files to exclude in conversion |optional   |
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
| sourcepath:  |  /config/snapshots/oprit |
| destinationpath:  | /config/www  |
| filename:   |latest_oprit   |
| excludelist: | deepstack_object_camera_oprit_latest.jpg  |
| begintimestamp | '25-12-2020 23:24:24'  |
| endtimestamp: | '25-12-2020 23:24:40  |

### Events

When the service is called an event will be triggerd after **succesful** creation of the output file. This event could be used for example for notifications to the mobile app.

The event to listen for is: `snaptogif`

This could also be easily explored with the developers tool event viewer, were you can listen to this event. 

The event data contains information about the "build" of the created output file.

```json
{
    "event_type": "snaptogif",
    "data": {
        "Type": "gif_created",
        "file": "mylatest.gif",
        "Path": "/config/www",
        "BeginTimeStamp": "26/12/2020 14:17:00",
        "EndTimeStamp": "26/12/2020 14:17:59",
        "NoComposedImages": 9,
        "sourcepath": "/config/snapshots/achtertuin",
        "sourcefiles": [
            "deepstack_object_achtertuin_2020-12-26_14-17-02.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-03.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-04.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-06.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-07.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-08.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-14.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-15.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-16.jpg"
        ]
    },
    "origin": "LOCAL",
    "time_fired": "2020-12-26T21:37:36.411617+00:00",
    "context": {
        "id": "a3340e0c0b66813d7a18ac93effaa0da",
        "parent_id": null,
        "user_id": null
    }
}
