Title: Pushing bulk legacy data to XNAT
Category: XNAT
Status: Published
Tags: xnat, dicom
Authors: Grégory Operto

This is not intended to be a tutorial on the subject, rather some feedback from a
recent experience dealing with an old and half-remembered <del>dream.</del> dataset.

<!-- PELICAN_END_SUMMARY -->

There are already plenty of useful resources out there e.g. from the XNAT
[documentation](https://wiki.xnat.org/documentation/how-to-use-xnat/image-session-upload-methods-in-xnat/), [discussion group](https://groups.google.com/forum/#!forum/xnat_discussion).
For instance, the [Desktop Upload Assistant](https://wiki.xnat.org/documentation/how-to-use-xnat/image-session-upload-methods-in-xnat/using-the-desktop-upload-assistant)
is pretty handy if you can afford to use a GUI.

The simplest way to send DICOM images and other DICOM composite objects
to an XNAT instance from a CLI may be using `storescu` (from the [`dcmtk`](http://support.dcmtk.org) DICOM toolkit).


### Example:

```bash
storescu -nh -v --scan-directories --scan-pattern "*.dcm" --recurse -aec <AETITLE> \
   <XNAT_SERVER_IP> <XNAT_SERVER_PORT> /path/to/local/data
```

> _`AETITLE` is the Application Entity title used by the XNAT instance to
identify itself_

The command will recursively look for any DICOM (`*.dcm`) file contained in a given source folder.
This requires the DICOMs to be previously structured and curated such a
way that XNAT will correctly identify the associated study and its various
subjects, sessions and sequences.

DICOMs are typically organized in folders, one per subject, one subfolder per
sequence. However the folder organization of the DICOMs is of little importance
at this point as XNAT will rely on information carried by DICOM tags to classify
each file and populate its database (Read [Basic DICOM object identification](https://wiki.xnat.org/docs16/3-administrator-documentation/configuring-xnat/configuring-the-dicom-c-store-scp-receiver/basic-dicom-object-identification))

By default, XNAT will start looking for the contents of the `Patients Comments` attribute
(0010,4000) then for the `Study Comments` (0032,4000) attribute. These are fields
which are by default generally left free by many scanners. If no relevant
information is found, then XNAT will look for three following DICOM fields, namely
`Study Description` **(0008,1030)**, `Patient Name` **(0010,0010)** and
`Patient ID` **(0010,0020)**, identifying the project, subject and session,
respectively (given as PROJECTID, SESSIONID, SUBJECTID later in the example).

The command `dcmodify` (again from `dcmtk`) can be used to modify any of these
fields. In association with `find` this can be done over a large number of files
using a single command. If working in Python, `pydicom` may also be a good option.

### Example:

```bash
find /path/to/data -name "*.dcm" -exec dcmodify -i PatientID="SESSIONID" \
   -i PatientName="SUBJECTID" -i StudyDescription="PROJECTID" {} \;
```

In this example if the data is to be stored in one single project, it is wise
to check that all DICOMs share the same `Study Description` field. The same goes
for the `PatientName` field within a single subject or for the `PatientID` within
a session.

### Note #1:

Even with a unique `Study Description` value, XNAT may complain and result in
conflicts in the prearchive if the DICOMs do not share the same
`Study Instance UID` (0020,000D). Then again `dcmodify` would be handy to make
this field consistent across all files.

```bash
find /path/to/data -name "*.dcm" -exec \
   dcmodify -i StudyInstanceUID="STUDYINSTANCEID" {} \;
```

### Note #2:

XNAT can be configured so that these default rules can be overridden. This is
something to keep in mind when assigning the attributes so as to avoid any
unexpected result and so that `dcmodify` may target the correct fields.







