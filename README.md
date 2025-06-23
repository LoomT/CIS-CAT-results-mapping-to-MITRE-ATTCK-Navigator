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

### Notes
- All files are stored in a dedicated uploads directory
- Each file is stored in its own unique directory identified by UUID
- Filenames are sanitized for security
- Error responses include cleanup of any partially created resources
- Mappings are loaded from an Excel spreadsheed. Currently included file is from [CIS Security](https://www.cisecurity.org/insights/white-papers/cis-controls-v8-master-mapping-to-mitre-enterprise-attck-v82)
