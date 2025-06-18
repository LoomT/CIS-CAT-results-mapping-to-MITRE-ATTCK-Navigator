# CIS-CAT results mapping to MITRE ATT&CK Navigator

An enterprise solution for automating and centralizing CIS-CAT Assessor report storage,
aggregation and visualization in the MITRE ATT&CK framework using MITRE ATT&CK Navigator.

## Requirements

- Python 3.12
- npm 11.4
- Docker 28.2
- docker-compose v2.36

For the first time execute `python -m venv .venv` then `source .venv/bin/activate` (linux) 
or `.venv\Scripts\activate` (Windows) to create a virtual Python environment.

## Deploying the Application using Docker
*For building and running the application for local development go to `Local Development` section.*

### Downloading ATT&CK Navigator

First make sure the ATT&CK Navigator submodule is cloned as well `git submodule update --init`.

For the ATT&CK Navigator to work offline from the root project directory install 
`pip install -r navigator-config/requirements.txt` and run `python navigator-config/update.py` 
to download all the files required to run it fully offline (this may take a while).

### Domains and Certificates

In case you need to change the domain or ports used by the tool, 
make sure to update the `caddy/Caddyfile` accordingly. 
This includes modifying the domain entries to reflect the new domain.  
In addition to changing the `Caddyfile` also add the certificates to 
`caddy/certs/private.key` and `caddy/certs/cert.crt` or change the path in the `caddy/Caddyfile`
if the certificates are already in a different location.

To generate a sample certificate run `gen.sh` in `caddy/` directory.

### X-Forwarded-User setup

In addition to setting up caddy, also modify the `web.env` environment file to change 
`SUPER_ADMINS` and `TRUSTED_IPS`, where `SUPER_ADMINS` is matched against `X-Forwarded-User`
(case-sensitive) and `TRUSTED_IPS` is tested against the source IP a request came from. 
In order for an admin to be trusted both the IP and the `X-Forwarded-User` have to be trusted. 
This is only enabled when the `ENABLE_SSO` environment variable is `true`.

If `ENABLE_SSO` is false, all users will have super admin privileges by default.

### Docker Compose

Build and start the application `docker-compose up --build`

To run in detached mode `docker-compose up -d --build`

To stop the application `docker-compose down`

## Deploying and Using Wrapper for CIS-CAT Assessor

The wrapper scripts for Windows or Linux can be found in `wrapper/` directory.

There are two ways to run the wrapper, the first is from any directory.
In this case it expects as first argument the path to the actual Assessor CLI executable, 
(i.e `path/to/Assessor-CLI.sh` or `path\to\Assessor-CLI.bat`).  
The second way is to make sure the respective `wrapper.sh` or `wrapper.ps1` 
is present in the same directory as `Assessor-CLI` file which should be in the root directory
of a CIS-CAT Assessor installation.
The remaining arguments are the same as for the normal `Assessor-CLI`.  
On top of this a `.wrapper.env` must be present in the same directory as the wrapper.
The format is as follows:
```env
POST_URL=http://localhost:5000/api/files/
POST_BEARER=YOUR_GENERATED_TOKEN
```

## Local Development

### Building ATT&CK Navigator

First make sure the ATT&CK Navigator submodule is cloned as well `git submodule update --init`.

From `attack-navigator/nav-app/` directory run `npm ci` to install dependencies.

In the same directory run `npm run build '--' --deploy-url /attack-navigator/ 
--base-href /attack-navigator/ --configuration production --aot=false --build-optimizer=false` 
to build the navigator (this may take a while).

*Optionally* for the ATT&CK Navigator to work offline from the root project directory install 
`pip install -r navigator-config/requirements.txt` and run `python navigator-config/update.py` 
to download all the files required to run it fully offline (this may take a while).

### Building and Running Development Client Server

In the `client/` directory.

For the first time execute `npm install` to install dependencies.

Execute `npm run dev` to start the frontend Vite server for development,
the link will appear in the console.

This frontend development server will hot reload when modifying code in `client/`
enabling comfortable UI coding experience.

The frontend development server includes a proxy configuration that automatically redirects
any request starting with `/api` to `http://localhost:5000` where the backend Flask server runs. 
This eliminates CORS issues during development and allows seamless API communication.
If port `5000` is already in use, instructions in section **Changing the Backend Port**
can be found.

### Building and Running Development back-end Server

Run `pip install -r api/requirements.txt` to install dependencies.

In the `api/` directory execute `python -m flask run` to start Flask server for development.

This server uses `api/.flaskenv` for environment variables such as database link,
uploaded file directory, and `X-Forwarded-User` configuration (see section `X-Forwarded-User setup`).

By default, the server's port is `5000`. If port `5000` is already in use,
instructions in section **Changing the Backend Port** can be found.

### Changing the Backend Port

If port 5000 is already in use, you can change the backend port in two places:
1. **Backend Flask Server** - In the `api/.flaskenv` change `FLASK_RUN_PORT` variable.
2. **Frontend Proxy Configuration** - Update file `client/vite.config.js`:
```javascript
server: {
   proxy: {
     '/api': {
       target: 'http://localhost:5001',  // Change to your new port
       changeOrigin: true,
     },
   },
 },
```

## Dummy SSO Server for Simulating X-Forwarded-User Header

First make sure Caddy is [downloaded](https://caddyserver.com/download), then in the `SSO/` folder run `caddy run`.
Depending on the setup, change the `UPSTREAM_PORT` environment variable
(i.e `$env:UPSTREAM_PORT=5000`) to the server IP. By default, it will use port `5173`.

After setting up caddy it is possible to access the dummy SSO portal through port `3000`
with a login at `:3000/login`. The entered username will be attached as `X-Forwarded-User`
to all requests allowing to simulate using the client as a super admin, department admin or regular user.

If used together with the docker-compose setup, the `web` service in `docker-compose.yml`
should expose the `WEB_PORT` by adding `ports`:
```dockerfile
web:
  build: ...
  volumes: ...
  networks: ...
  ports:
    - "5000:5000"
  env_file: ...
```

## Running Automated Tests

### Backend Testing

First ensure dependencies are installed `pip install -r tests/requirements.txt`.

Then run `python -m pytest` from the project root directory.

### End-to-End Testing

**The Flask server needs to be running with the static frontend files compiled before running these tests!**
To do that, in the `client/` directory run `npm run build`, this will build static frontend files in `client/dist/`.
Then start the Flask server as usual in the `api/` directory `python -m flask run`.

Navigate to `tests/e2e` and for the first time run `npm install`.

Then run `npm run test` to execute all Cypress tests.
By default, it will use the built-in Electron browser,
for other browsers run (these need to be installed on the system)
- `npm run test:firefox`
- `npm run test:edge`
- `npm run test:chrome`
- `npm run test:all` to run on all four browsers in sequence

Alternatively run `npm run open` to open a visual Cypress interface for running and debugging E2E tests.

### Python PEP8 Style Checking

First ensure `flake8` is installed (`pip install flake8`)

Then run `python -m flake8 api tests navigator-config`

Alternatively install `flake8` in vscode

### JavaScript and JSX Style Checking

Enter the `client/` directory and make sure eslint is installed (i.e. do a regular `npm install`)

Then run `npm run lint` to recursively check all `js` and `jsx` in `client/`
or `npm run lint:fix` to fix all issues automatically.

Also, the same can be done in the `tests/e2e/` folder for the E2E tests as there is 
a separate ESlint configuration there.

Alternatively, if using VSCode install plugin `eslint` or 
if using PyCharm right click file `eslint.config.js` and click apply
(in settings `Run eslint --fix on save` can be toggled on to automatically fix issues with `Ctrl + S`).

# API Documentation

## Endpoints

### Upload File
- **URL**: `/api/files/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file`: File to be uploaded (required), should have original generated filename to be parsed correctly

#### Successful Response
- **Code**: `201 Created`
- **Content-Type**: `application/json`
- **Response Body**:
# TODO: Change response
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

### List File Metadata ir IDs
- **URL**: `/api/files`
- **Method**: `GET`
- **Optional Query Parameters**:
  - `verbose`: if `true` will return full metadata of retrieved files, else will return a list of file ids
  - `search`: will filter on file whose filenames contain the search string
  - `hostname`: hostname id to limit results to, can contain multiple
  - `benchmark`: benchmark type id to limit results to, can contain multiple
  - `result`: result type id of the report to limit results to, can contain multiple
  - `department`: department id to limit results to, can contain multiple
  - `min_time`: lower bound of report's creation date-time in ISO 8601 format, e.g., 2025-06-13T20:26:30Z
  - `max_time`: upper bound of report's creation date-time in ISO 8601 format
  - `page`: page index of results, starts at 0, default is 0 if omitted
  - `page_size`: page size of results, default is 20 if omitted

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:

if query parameters contains `verbose=true`:
``` json
{
  "data": [
    {
      "benchmark": {
        "id": 1,
        "name": "CIS_Microsoft_Windows_11_Stand"
      },
      "department": {
        "id": 1,
        "name": "some department"
      },
      "filename": "DESKTOP-123-CIS_Microsoft_Windows_11_Stand-alone_Benchmark-20250519T174834Z.json",
      "hostname": {
        "id": 1,
        "name": "DESKTOP-123"
      },
      "id": "c39a05a3-d0b2-4b4a-b74d-414b2e79a428",
      "result": {
        "id": 1,
        "name": "Passing"
      },
      "time_created": "2025-06-12T19:23:21"
    }
  ],
  "filters": {
    "benchmark": [
      {
        "count": 1,
        "id": 1,
        "name": "CIS_Microsoft_Windows_11_Stand"
      }
    ],
    "department": [
      {
        "count": 1,
        "id": 1,
        "name": "some department"
      }
    ],
    "hostname": [
      {
        "count": 1,
        "id": 1,
        "name": "DESKTOP-123"
      }
    ],
    "result": [
      {
        "count": 1,
        "id": 1,
        "name": "Passing"
      }
    ],
    "time": {
      "global_max_value": "Thu, 12 Jun 2025 19:23:21 GMT",
      "global_min_value": "Tue, 06 May 2025 09:32:26 GMT",
      "local_max_value": "Thu, 12 Jun 2025 19:23:21 GMT",
      "local_min_value": "Tue, 06 May 2025 09:32:26 GMT"
    }
  },
  "pagination": {
    "page": 0,
    "page_size": 20,
    "total_count": 1
  }
}
```
else
```json
{
  "ids": ["id1", "id2"]
}
```

#### Error Responses
- **Code**: `500 Internal Server Error`
    - When server encounters an unexpected error: `"Internal Server Error"`

### Aggregate Files
- **URL**: `/api/files/aggregate`
- **Method**: `GET`

Accepts same query parameters as api/files to aggregate all files that are matching the criteria
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


### List Departments
- **URL**: `/api/admin/departments`
- **Method**: `GET`
- **Role Required**: Admin (Department Admin or Super Admin)
- **Headers**:
  - `X-Forwarded-User`: Authenticated user handle (required)
  - Originating IP **must** be in `TRUSTED_IPS`

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  {
    "departments": [
      { "id": 3, "name": "SOC" },
      { "id": 7, "name": "Blue Team" }
    ]
  }
  ```

#### Error Responses
- **Code**: `401 Unauthorized`
  - Missing `X-Forwarded-User` header or untrusted IP
- **Code**: `403 Forbidden`
  - Caller is not an admin
- **Code**: `500 Internal Server Error`
  - Unexpected database error


### Create Department
- **URL**: `/api/admin/departments`
- **Method**: `POST`
- **Role Required**: **Super Admin**
- **Content-Type**: `application/json`
- **Request Body**:
  - `name` *(string, required)* - Unique department name

#### Successful Response
- **Code**: `201 Created`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  {
    "department": { "id": 12, "name": "Forensics" }
  }
  ```

#### Error Responses
- **Code**: `400 Bad Request`
  - Missing name or duplicate department name
- **Code**: `401 Unauthorized` / `403 Forbidden`
  - Not authenticated / not a Super Admin
- **Code**: `500 Internal Server Error`
  - Database failure


### Delete Department
- **URL**: `/api/admin/departments/<department_id>`
- **Method**: `DELETE`
- **Role Required**: **Super Admin**
- **URL Parameters**:
  - `department_id` - ID of the department to delete (integer)

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  { "message": "Department deleted successfully" }
  ```

#### Error Responses
- **Code**: `404 Not Found`
  - Department does not exist
- **Code**: `401 Unauthorized` / `403 Forbidden`
  - Not authenticated / not a Super Admin
- **Code**: `500 Internal Server Error`
  - Database failure


### List Users
- **URL**: `/api/admin/users`
- **Method**: `GET`
- **Role Required**: Admin (Department Admin or Super Admin)

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  {
    "users": [
      { "handle": "alice", "department_id": 3, "department_name": "SOC" },
      { "handle": "bob",   "department_id": null }
    ]
  }
  ```

#### Error Responses
- **Code**: `401 Unauthorized`
  - Missing `X-Forwarded-User` header or untrusted IP
- **Code**: `403 Forbidden`
  - Caller is not an admin
- **Code**: `500 Internal Server Error`
  - Unexpected database error


### Add User to Department
- **URL**: `/api/admin/department-users`
- **Method**: `POST`
- **Role Required**: **Super Admin**
- **Content-Type**: `application/json`
- **Request Body**:
  - `department_id` *(integer, required)*
  - `user_handle` *(string, required)*

#### Successful Response
- **Code**: `201 Created`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  { "message": "User added to department successfully" }
  ```

#### Error Responses
- **Code**: `400 Bad Request`
  - Missing/invalid body or user is already assigned to a department
- **Code**: `404 Not Found`
  - Department not found
- **Code**: `401 Unauthorized` / `403 Forbidden`
  - Not authenticated / not a Super Admin
- **Code**: `500 Internal Server Error`
  - Database failure


### Remove User from Department
- **URL**: `/api/admin/department-users`
- **Method**: `DELETE`
- **Role Required**: **Super Admin**
- **Content-Type**: `application/json`
- **Request Body**:
  - `department_id` *(integer, required)*
  - `user_handle` *(string, required)*

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  { "message": "User removed from department successfully" }
  ```

#### Error Responses
- **Code**: `404 Not Found`
  - User not found in the specified department
- **Code**: `400 Bad Request`
  - Missing/invalid body
- **Code**: `401 Unauthorized` / `403 Forbidden`
  - Not authenticated / not a Super Admin
- **Code**: `500 Internal Server Error`
  - Database failure


### Get Authentication Status
- **URL**: `/api/auth/status`
- **Method**: `GET`
- **Role Required**: None
- **Headers (optional)**:
  - `X-Forwarded-User`: User handle (only evaluated if request originates from a `TRUSTED_IP`)

#### Successful Response
- **Code**: `200 OK`
- **Content-Type**: `application/json`
- **Response Body**:
  ```json
  {
    "user": "alice",
    "is_super_admin": true,
    "is_department_admin": true
  }
  ```

#### Error Responses
- **Code**: `500 Internal Server Error`
  - Unexpected server error

### Notes
- All files are stored in a dedicated uploads directory
- Each file is stored in its own unique directory identified by UUID
- Filenames are sanitized for security
- Error responses include cleanup of any partially created resources
- Mappings are loaded from an Excel spreadsheed. Currently included file is from [CIS Security](https://www.cisecurity.org/insights/white-papers/cis-controls-v8-master-mapping-to-mitre-enterprise-attck-v82)
