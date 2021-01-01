# snaptogif
Homeassistant custom component for converting snapshots (jpg) to a gif or mp4
****
This component is developed by my need of creating a GIF of MP4 file from snapshot images that are created by the deepstack custom component. The component is designed for general use of converting snapshot to GIF or MP4, so it is useful for everyone who has to handle or deal with snapshots created by cameras of image processing software. The component also has additional services to move or delete snapshots.

To use this component, copy the directory `snaptogif`and it contents to the `custom_components` directory of your homeassistant.

Add the following line in your `configuration.yaml:`
```yaml
snaptogif:
```
Restart home-assistant after this.

If the custom component is installed correctly you should have  the following services available:
`snaptogif.start`
`snaptogif.move`
`snaptogif.delete`

This could be easily found under the development tools, tab services.

###### Service Usage:

The services have to be called with the following calll-parameters:



| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath  |  	path of the directory where the snaphots are in | mandatory, directory must exist  |
|  destinationpath |  path of the directory where the GIF should be created |  mandatory for service start and move (incase of service, start directory must exists)
|  filename |	Name for gif/mp3 file (without extension)   | optional (only service start), default=latest   |
|  format |  `gif` or `mp4` | optional (only service start), default='gif'   |
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

Example for usage: `snaptogif.start`


| Parameter  |Value   |
| ------------ | ------------ |
| sourcepath:  |  /config/snapshots/oprit |
| destinationpath:  | /config/www  |
| filename:   |latest_oprit   |
| excludelist: | deepstack_object_camera_oprit_latest.jpg  |
| begintimestamp | '25/12/2020 23:24:24'  |
| endtimestamp: | '25/12/2020 23:24:40  |

### Events

When a service is called an event will be triggerd after **succesful** operation of the service. This event could be used for example for notifications to the mobile app.

The event to listen for is: `snaptogif`

This could also be easily explored with the developers tool event viewer, were you can listen to this event. 

The event data contains information about the "build" of the created output file.
The `type` in the event shows which service originated the event.

```json
{
    "event_type": "snaptogif",
    "data": {
        "type": "start",
        "file": "mylatest.gif",
        "destinationpath": "/config/www",
        "begintimestamp": "26/12/2020 14:17:00",
        "endtimeStamp": "26/12/2020 14:17:59",
        "no_files": 9,
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
```
### Example Script for use:
The script below shows a usecase for this component. In this case i use a scheduler to trigger this script at 00:10:00 (During midnight). The script composes a mp4 from the snapshots taken the previous day and then the original snapshots are deleted. The mp4 filname has the datestamp in its filename so its alway easy to trace back.

```yaml
create_mp4_from_snapshots_oprit_previous_day:
  alias: Create MP4 from snapshots oprit previous day
  sequence:
  - variables:
      daysback: 0
      begintime: '{{(now()-timedelta(days=daysback)).strftime("%d/%m/%Y")}} 00:00:00'
      endtime: '{{(now()-timedelta(days=daysback)).strftime("%d/%m/%Y")}} 23:59:59'
      fname: snapshots_oprit_{{(now()-timedelta(days=daysback)).strftime("%Y_%m_%d")}}
  - service: snaptogif.start
    data:
      sourcepath: /config/snapshots/oprit
      destinationpath: /config/archive/oprit
      filename: '{{fname}}'
      format: mp4
      excludelist: deepstack_object_camera_oprit_latest.jpg
      begintimestamp: '{{begintime}}'
      endtimestamp: '{{endtime}}'
  - wait_for_trigger:
    - platform: event
      event_type: snaptogif
      event_data:
        type: start
        destinationpath: /config/archive/oprit
    timeout: 00:02:00
  - service: snaptogif.delete
    data:
      sourcepath: /config/snapshots/oprit
      excludelist: deepstack_object_camera_oprit_latest.jpg
      begintimestamp: '{{begintime}}'
      endtimestamp: '{{endtime}}'
  mode: single
```