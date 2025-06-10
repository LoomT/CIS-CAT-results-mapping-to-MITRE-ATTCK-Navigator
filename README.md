# CIS-CAT results mapping to MITRE ATTCK Navigator

## Running the app

### Build attack navigator


First make sure all the submodules are cloned as well `git submodule update --init`, then in the cloned submodule directory enter the `nav-app` folder and run `npm ci` to install dependencies  

Then run `npm run build '--' --deploy-url /attack-navigator/ --base-href /attack-navigator/ --configuration production --aot=false --build-optimizer=false` to build the navigator

### Client

In the client directory

For the first time execute `npm install` to install dependencies

Execute `npm run dev` to start the frontend for development


### Server

In the api directory

For the first time execute `python -m venv .venv`, `source .venv/bin/activate` (linux) or `.venv\Scripts\activate` (Windows) and `pip install -r requirements.txt` to install dependencies

Execute `python -m flask run` to start Flask server for development

### Deployment

Docker should be installed

In case you need to change the domain used by the tool, make sure to update the `caddy/Caddyfile` accordingly. This includes modifying the domain entries to reflect the new domain.  
In addition to changing the `Caddyfile` also add the certificates to `caddy/certs/private.key` and `caddy/certs/cert.crt`. To generate a sample certificate run `gen.sh` in `caddy/`.

Build and start the application `docker-compose up --build`

To run in detached mode `docker-compose up -d --build`

To stop the application `docker-compose down`

### Wrapper

There are two ways to run the wrapper, the first is from any directory. In this case it expects as first argument the path to the actual CLI, (i.e `path/to/Assessor-CLI.sh` or `path\to\Assessor-CLI.bat`).  
The second way is to make sure the respective `wrapper.sh` or `wrapper.ps1` is present in the same directory.  
The remaining arguments are the same as for the normal `Assessor-CLI`.  
On top of this a `.wrapper.env` must be present in the same directory as the wrapper. The format is as follows:
```env
POST_URL=http://localhost:5000/api/files
POST_BEARER=TOKEN_sometoken_here
```

## Development

### Backend Testing

First ensure `pytest` is installed (`pip install pytest`)

Then run `python -m pytest` from the project root directory

### End-to-End Testing

The Flask server needs to be running with the static frontend files compiled before running these tests!
To do that, run `npm run build` in the client directory, this will build static frontend files in client/dist.
Then start the server as usual in the api directory `python -m flask run`.

Navigate to `tests/e2e` and for the first time run `npm install`

Then run `npm run test` to execute tests automatically

Alternatively run `npm run open` to open a visual interface for running and debugging E2E tests

### Backend Style Checking

First ensure `flake8` is installed (`pip install flake8`)

Then run `python -m flake8 api tests`

Alternatively install `flake8` in vscode

### Frontend Style Checking

Enter the client directory and make sure eslint is installed (i.e. do a regular `npm install`)

Then run `npm run lint` to recursively check all `js` and `jsx` in client
or `npm run lint:fix` to fix all issues automatically

Alternatively install `eslint` in vscode

# API Documentation

## Endpoints

### Upload File
- **URL**: `/api/files/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file`: File to be uploaded (required)

#### Successful Response
- **Code**: `201 Created`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  {
    "id": "string",       // Unique identifier for the file
    "filename": "string"  // Name of the converted file
  }
  ```

#### Error Responses
- **Code**: `400 Bad Request`
  - When no file is provided: `"No file part"`
  - When filename is empty: `"No selected file"`
  - When filename is invalid: `"Invalid filename"`
  - When file contents are invalid: `"Invalid file format"`

- **Code**: `500 Internal Server Error`
  - When server encounters an unexpected error: `"Internal Server Error"`

### Download File
- **URL**: `/api/files/<file_id>`
- **Method**: `GET`
- **URL Parameters**:
  - `file_id`: Unique identifier of the file (required)

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: Based on file type
- **Headers**:
  - `Content-Disposition`: `attachment; filename=<filename>`
- **Response Body**: File content as binary data

#### Error Responses
- **Code**: `400 Bad Request`
  - When the file ID is invalid: `"Invalid file id"`

- **Code**: `404 Not Found`
  - When file ID doesn't exist: `"No file by this id found"`

- **Code**: `500 Internal Server Error`
  - When multiple files found: `"Multiple files found"`
  - When no files found in directory (dangling directory): `"No file found"`
  - When server encounters an unexpected error: `"Internal Server Error"`

### List File Metadata
- **URL**: `/api/files`
- **Method**: `GET`

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
``` json
  {
    "files": [
      {
        "id": "string",       // Unique identifier for the file
        "filename": "string"  // Name of the file
      },
      ...
    ]
  }
```

#### Error Responses
- **Code**: `500 Internal Server Error`
    - When server encounters an unexpected error: `"Internal Server Error"`

### Aggregate Files
- **URL**: `/api/files/aggregate`
- **Method**: `GET`

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Headers**:
    - `Content-Disposition`: `attachment; filename=converted_aggregated_results.json`

- **Response Body**: Aggregated and converted file content as JSON

#### Error Responses
- **Code**: `400 Bad Request`
    - When `aggregate=true` but no file IDs provided: `"No file ids provided"`

- **Code**: `404 Not Found`
    - When a specified file ID doesn't exist: `"No file by this id found"`

- **Code**: `500 Internal Server Error`
    - When server encounters an unexpected error: `"Internal Server Error"`


### Notes
- All files are stored in a dedicated uploads directory
- Each file is stored in its own unique directory identified by UUID
- Filenames are sanitized for security
- Original files are removed after processing
- Error responses include cleanup of any partially created resources
- Mappings are loaded from an Excel spreadsheed. Currently included file is from [CIS Security](https://www.cisecurity.org/insights/white-papers/cis-controls-v8-master-mapping-to-mitre-enterprise-attck-v82)
