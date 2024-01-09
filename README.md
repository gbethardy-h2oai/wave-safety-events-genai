# h2oGPTe GenAI Safety Events Classifier
This is an app which allows a user to upload a CSV file of safety event classifications generated 
using h2oGPTe GenAI LLM, provide human0in0the0loop feedback, and visually explore/manage the 
classification results and explanations.

## End Users:
* **Business Stakeholders** - generate a classification using a GenAI LLM and explore the results and explanations.



## Project Overview

```
├── data                    # Static files used primarily for local development and at run time
├── docs                    # Documentation
├── notebooks               # Jupyter notebooks for backend code development
├── src                     # Application source code
├── static                  # Non-changing assets
├── venv                    # Virtual python environment
├── .appignore              # Files to not publish to the AI Cloud
├── .gitignore              # Files to not check into GitHub
├── app.toml                # AI Cloud configuration
├── Makefile                # For local code compilation
├── README.md               
└── requirements.txt
```

## Contributing
When working on this application, please complete the following items:

- [ ] Testing
    - [ ] Ensure that the app can run successfully locally
    - [ ] Ensure that the app can run in the AI Cloud using `h2o bundle deploy`

- [ ] Clean up
    - [ ] Add folders and files to the `.gitignore` which should not be checked into GitHub
    - [ ] Add folders and files to the `.appignore` which should do not need to be added to the AI Cloud
    - [ ] Run `make format` to ensure the codebase stays consistent using black and isort

- [ ] Documentation
    - [ ] Document any new App Secrets in the `README.md`
    - [ ] Add any new developer information to the `README.md`
    - [ ] Read the `README.md`, is everything still relevant and true?
    - [ ] Add any new user features to the `docs/description_for_adverse_events_classifier.md`
    - [ ] Read the `docs/description_for_adverse_events_classifier.md`, is everything still relevant and true?
    - [ ] Replace any dated images in the `static` folder

- [ ] Release
    - [ ] Increment the app version number in the `app.toml`
    - [ ] Create a new bundle using `h2o bundle` and this file into the `build` folder, no need to delete old bundles
    - [ ] Deploy the app to the AI Cloud

- [ ] Open a pull request (PR) in GitHub
    - [ ] Assign a reviewer
    - [ ] Assign at least one `area` label and `type` label
    - [ ] Use a descriptive title
    - [ ] Include a list of what your PR does in the description
    - [ ] Include `RELNOTES=brief explaination` in the description


## Local Development
Setup your local python environment. Note that python 3.7 is specified as this is the default for the H2O AI
Hybrid Cloud.

```shell script
make setup
```

Run your app for local development **after setting up the key information in Make File.**
```shell script
make run
```
