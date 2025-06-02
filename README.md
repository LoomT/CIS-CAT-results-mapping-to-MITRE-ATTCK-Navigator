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

In case you need to change the domain used by the tool, make sure to update the `caddy/Caddyfile` accordingly. This includes modifying the domain entries to reflect the new domain and ensure that local SSL certificates are properly configured for secure access.

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
- **URL**: `/api/files`
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
  - When server encounters an unexpected error: `"Unexpected error while processing file"`

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
  - When server encounters an unexpected error: `"Unexpected error while getting file"`

### Notes
- All files are stored in a dedicated uploads directory
- Each file is stored in its own unique directory identified by UUID
- Filenames are sanitized for security
- Original files are removed after processing
- Error responses include cleanup of any partially created resources
- Mappings are loaded from an Excel spreadsheed. Currently included file is from [CIS Security](https://www.cisecurity.org/insights/white-papers/cis-controls-v8-master-mapping-to-mitre-enterprise-attck-v82)

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.ewi.tudelft.nl/cse2000-software-project/2024-2025/cluster-f/07c/cis-cat-results-mapping-to-mitre-attck-navigator.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2024-2025/cluster-f/07c/cis-cat-results-mapping-to-mitre-attck-navigator/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
