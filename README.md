File Storage XBlock
===================

The “File Storage XBlock” allows course staffers to add files stored in various internet file storage services to the courseware (courseware, course info and syllabus) by adding a link through an advanced component that they create in edX’s Studio authoring tool. The files can be added either as embedded content, or as links to the files in their original location, or as links to the files after uploading them to the edX server itself. 

Students will view these files in their Open edX or edX.org courses. 

Installation
------------
To install the File Storage XBlock within your edX Python environment, run the following command:

```bash
$ pip install /path/to/xblock-file-storage/
```

Enabling in Studio
------------------

To enable the File Storage XBlock within studio:

1. Navigate to `Settings -> Advanced Settings` from the top nav bar.
2. Add `"filestorage"` to the Advanced Module List, as shown in the screen shot below.

![Advanced Module List](docs/img/advanced.png)

Usage
-----
Once enabled in Studio, it's easy to use the File Storage XBlock.

Start by navigating to the unit in studio where you want to insert your file. From here choose the `Advanced` component.

![Studio Component List](docs/img/component_list.png)

This will bring up a list of the XBlocks that have been enabled in Studio. If you followed the previous step to enable the File Storage XBlock in Studio you will see an option titled `File Storage`. Click on it to insert the File Storage XBlock into your unit.

![Studio Advanced Component Selection](docs/img/unit2.png)

After you've inserted the File Storage XBlock, a default document will be inserted into your unit as shown in the screen shot below.

![Studio Initial File Storage XBlock Insertion](docs/img/xblock_insert.png)

To change the inserted, XBlock click on the `Edit` button on the upper-right corner of the File Storage XBlock. This will bring up the edit dialog where you can change the display name of the component as well as the  document that is being inserted and how you want it to be embedded.

![Edit inserted OneDrive for Business document](docs/img/editme.png)

Update the component name to the text you want to be displayed.
Enter the URL to the file from its original location (in YouTube or OneDrive or Google Drive or Dropbox etc.)

You will be able to select the way you want the file to be displayed inside the xblock:

- As a link to the file in its original location.
- Upload the file from its origial location to the edX Files and Uploads area and then insert a link to it. 
- Embed the file in its original loaction inside an iframe.

After you click save, your File Storage XBlock will have been updated with the new values.

At present, the following services are explicitly supported:
- YouTube
- OneDrive for Business
- OneDrive for consumers
- Google docs
- Google presentations
- Vimeo
- Slideshare
- Soundcloud
- Screenr
- TED
- Office Mix
- Issuu
- Box.com

More services can be added easily. Even if a service is not explicitly supported, an attempt will be made to allow you to include the file, but it may fail depending upon the level of support provided by the service.
Also note that some of these services do not support embedding and some do not support uploading to the edX server. Also, some may need their own login before you can view the files in their original location.

![Updated studio view](docs/img/xblock_studio_insert.png)

At this point simply click on the `Publish` button and the OneDrive for Business document will be available for students to view it from the LMS.

![Published File Storage XBlock in LMS](docs/img/student_view.png)
