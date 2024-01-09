import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import numpy as np


async def prepare_text(q):
    prefix_str = 'You are a clinician classifying safety and accident events. You review event descriptions and provide an event classification as a non-safety event, near miss safety event, precursor safety event, or serious safety event. A non-safety event does not reach or effect the patient and there is no potential threat of injury or error in the event description. A near miss safety event does not reach or effect the patient and the error is caught by a detection barrier or by chance. A precursor safety event reaches or effects the patient, but only results in minimal harm or no detectable harm or injury. A Serious safety event reaches the patient and results in moderate to severe harm, injury, or death. For example, given the event description "patient fell off bed and broke ankle," you would reply in 4 words or less "Serious Safety Event". given the event description '
    suffix_str = ' ", what would be your response for the event classification in 4 words or less and explain why?'
    q.client.original_data['question'] = prefix_str + '"' + q.client.original_data['event_description'].astype(str) + '"' + suffix_str
    return



async def classify_events(q):
    print("classifying events")
    q.client.original_data['answer'] = q.client.original_data['question'].apply(lambda x: q.app.h2ogpte_client.answer_question(question=x, llm=q.args.llm_name).content)
    print("done classifying events")
    #q.client.original_data.to_csv('app_scored_data.csv')
    return



async def classify_report(q):

    # Clean up y_pred and y_true
    #print(q.client.original_data.loc[:, ['safety_event_classification', 'answer_clean']])
    #q.client.original_data.to_csv('app_scored_data_20000_sample_sm2.csv')
    q.client.original_data['y_pred'] = [0 if "Not a" in x
                                        else 1 if  "Near Miss" in x
                                        else 2 if  "Precursor" in x
                                        else 3 for x in q.client.original_data['answer']]
    q.client.original_data['y_true'] = [0 if  "Not a" in x
                                        else 1 if  "Near Miss" in x
                                        else 2 if  "Precursor" in x
                                        else 3
                                        for x in q.client.original_data['safety_event_classification']]
    print (f"classify_report: save scored dataset")
    q.client.original_data.to_csv(q.app.data_save_location + 'adverse_event_data_to_report.csv', index=False)



    # Calculate classification metrics
    y_true = q.client.original_data['y_true']
    y_pred = q.client.original_data['y_pred']
    accuracy = accuracy_score(y_true, y_pred)
    precision_macro = precision_score(y_true, y_pred, average='macro')
    recall_macro = recall_score(y_true, y_pred, average='macro')
    f1_macro = f1_score(y_true, y_pred, average='macro')

    # Generate a classification report

    classification_rep = classification_report(y_true,
                                               y_pred,
                                               #target_names=['Not a', 'Near Miss', 'Precursor', 'Serious'],
                                               target_names=['Not a Safety Event', 'Near Miss Event', 'Precursor Event', 'Serious Event'],
                                               output_dict=True)
    classification_df = pd.DataFrame(classification_rep).transpose()
    classification_df = classification_df.reset_index()

    # Create a confusion matrix DataFrame
    #confusion = confusion_matrix(y_true, y_pred)
    #confusion_df = pd.DataFrame(confusion, columns=["Predicted Class 0", "Predicted Class 1", "Predicted Class 2", "Predicted Class 3"],
    #                            index=["Actual Class 0", "Actual Class 1", "Actual Class 2", "Actual Class 3"])

    # Create a DataFrame for the calculated metrics
    metrics_df = pd.DataFrame({
        "Accuracy": [accuracy],
        "Precision (Macro)": [precision_macro],
        "Recall (Macro)": [recall_macro],
        "F1-Score (Macro)": [f1_macro]
    })

    # Display the metrics DataFrame
    #print(f"Metrics DataFrame: {metrics_df}")
    # Display the classification report DataFrame
    #print(f"\nClassification Report DataFrame: {classification_df}")
    # Display the confusion matrix DataFrame
    #print(f "\nConfusion Matrix DataFrame: {confusion_df}")

    print (f"classify_report: save metrics")
    metrics_df.to_csv(q.app.data_save_location + 'metrics_report.csv', index=False)
    classification_df.to_csv(q.app.data_save_location + 'classification_report.csv', index=False)

    return metrics_df, classification_df

