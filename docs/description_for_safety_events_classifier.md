# h2oGPTe GenAI Healthcare Safety Event Classifier
Visually explore and manage h2oGPTe GenAI Healthcare Safety Events classifications and explanations.

## Current Functionality

### Select the Healthcare Safety Event Dataset to upload
* Upload a CSV file. 
* Must contain fields: File_ID, Event_Date, Event_Description, Question, h2oGPTe_Response, Email_Question, h2oGPTe_Email_Response

### Human-in-the-loop - Search, Review Accept or Edit GenAI Classification Responses 
* Search by File ID for Safet Events of interest
* Point the mouse at the description or response to see the entire field as a tooltip
* Double click on the File DI to drill down into the event
* On the detail form, edit the GenAI response classification and explanation
* Save edits or cancel and return to the table preview of all safety events

### Generate and send an automated email on the safety event
* Review the automatically generated email on the event
* Optionally edit and save the auto generated email
* Send the email and return to the table preview of all safety events
* 

*Have feedback? Reach out to us on slack.*

The H2O GenAI Healthcare Safety Event Classifier app is example code from H2O for exploring event classification results.
The goal is to help accelerate with building a front end for NLP analysis. This is not a fully supported product.
We would love your feedback on the ease of making this app your own, and the content of the app.
We are open to requests on this app but please note that since it is demo code the regular H2O
Support process does not apply.
