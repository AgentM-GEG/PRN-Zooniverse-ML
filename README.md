
### Uploading the images to Zooniverse
The image data can be uploaded to Zooniverse using the `upload_data.py` script. The script has the following command line arguments:
```
python3 upload_data.py [-h] -d DATA_FOLDER -p PROJECT_ID [--subject_set_name SUBJECT_SET_NAME] [--subject_set SUBJECT_SET] [-o OUTPUT_MANIFEST]
```

 * `DATA_FOLDER`: points to the directory containing the JPEG images
 * `PROJECT_ID`: is the integer Zooniverse project ID
 * `SUBJECT_SET_NAME` or `SUBJECT_SET_ID`: defines the Zooniverse subject set to upload to. Specify the name if you want the script to create a new subject set or specify the ID if you want the script to upload to an existing subject set (NOTE: The script will not detect existing images and overwrite them. If you want to overwrite existing images, delete the subject set on Zooniverse and restart the upload)
 * `OUTPUT_MANIFEST`: the path to the output manifest file which will store the mapping between the filenames and Zooniverse subject ID

### Import the workflow on Caesar
Log in to [caesar.zooniverse.org](https://caesar.zooniverse.org) with your Zooniverse username and password and click on Workflows. Click the "+ Add" button and type in the Workflow ID on Zooniverse.
Follow the steps [here](https://zooniverse.github.io/caesar/#creating-an-extractor) to create an extractor and reducer. For the ML annotations, we will create a Blank Extractor and a FirstExtract reducer.
The extractor key is up to you, but the reducer key must be `machineLearnt`. Make sure to specify the extractor key when configuring the reducers (see [here](https://zooniverse.github.io/caesar/#filters)).

### Creating the machine annotation export for Zooniverse
The machine annotation for Zooniverse is uploaded using a CSV file. We can generate this CSV file using the `create_csv.py` script:
```
create_csv [-h] -d DATA_FOLDER -m SUBJECT_MANIFEST [--extractor_key EXTRACTOR_KEY] [-o OUTPUT]
```

 * `DATA_FOLDER`: points to the directory containing the segmentation masks
 * `SUBJECT_MANIFEST`: points to the manifest file generated from the `upload_data.py` step
 * `EXTRACTOR_KEY`: the extractor that was defined in the Caesar step
 * `OUTPUT`: output path for the CSV file (defaults to `correct-a-cell.csv`)

### Uploading the machine data to Zooniverse
This must be done in two steps. First, we must upload the generated CSV file to a public URL so that Caesar can retrieve it. Second, we must point Caesar to that URL so that it can import the data.
One way to upload data to a public URL is using [file.io](https://www.file.io), through the following command:

```
curl -F "file=@[path/to/csv/file]" https://file.io
```
replacing `[path/to/csv/file]` with the path to the CSV file generated above (note the extra `@` before the file path). This returns a dictionary like the one below:
```
{"success":true,"status":200,"id":"73098a90-3eb2-11ee-b46c-e3d7b7473aec","key":"wcZ1UtYXYQd3","path":"/","nodeType":"file","name":"correct-a-cell.csv","title":null,"description":null,"size":83096491,"link":"https://file.io/wcZ1UtYXYQd3","private":false,"expires":"2023-09-02T17:04:25.005Z","downloads":0,"maxDownloads":1,"autoDelete":true,"planId":0,"screeningStatus":"pending","mimeType":"application/octet-stream","created":"2023-08-19T17:04:25.005Z","modified":"2023-08-19T17:04:25.005Z"}
```

Note the `link` key and the URL and pass it to the command below to upload the data to Caesar:
```
python3 upload_csv.py [-h] -w WORKFLOW_ID -u URL
```

 * `WORKFLOW_ID`: is the Zooniverse workflow ID
 * `URL`: is the public URL

The upload will be fast but Caesar can take several minutes to process the CSV file.
Depending on the number of subjects, you can check whether the upload succeeded by going to `https://caesar.zooniverse.org/workflows/[WORKFLOW_ID]/subjects/[SUBJECT_ID]` for any subject in the subject set
and checking whether the extracts and reducers field is populated. 
