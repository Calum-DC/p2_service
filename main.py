import boto3
import json
import os
from jira import JIRA
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv
import threading



app = Flask(__name__)

# Load environment variables
sqs_client = boto3.client('sqs', region_name=os.getenv('AWS_REGION'))


QUEUE_URL = os.getenv('SQS_P2_URL')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')



stop_flag = False

def process_sqs_p2_message():
    global stop_flag
    while not stop_flag:
        try:
            jira_client = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
            # Receive the message from the SQS queue
            response = sqs_client.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )

            messages = response.get('Messages', [])

            if not messages:
                continue

            message = messages[0]
            receipt_handle = message['ReceiptHandle']
            message_body = json.loads(message['Body'])
            print(f"Received message: {message_body}")


            title = message_body.get('title')
            description = message_body.get('description')

            # Use the native inference API to send a text message to Amazon Titan Text
            # and print the response stream.
            # Create a Bedrock Runtime client in the AWS Region of your choice.


            
            client = boto3.client("bedrock-runtime", region_name="us-east-1")

            # Set the model ID, e.g., Titan Text Premier.
            model_id = "amazon.titan-text-express-v1"

            # Define the prompt for the model.
            prompt = "The following passage of text outlines an issue that has been reported via an online web form, please pretend you are an IT support engineer and provide a solution to the problem or statement given, also be aware that this message will be read by a recipient that is unable to provide any additional information. Dont' write too much and definitely dont say that you are a model responding to the problem. Please provide a structured solution that clearly outlines a solution: " + description

            # Format the request payload using the model's native structure.
            native_request = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1024,
                    "temperature": 0.3,
                },
            }

            # Convert the native request to JSON.
            ai_request = json.dumps(native_request)

            try:
                ai_response = client.invoke_model(modelId=model_id, body=ai_request)
            except client.exceptions.EndpointConnectionError as e:
                print(f"Error connecting to the AI model endpoint: {str(e)}")

            # # Invoke the model with the request.
            # ai_response = client.invoke_model(
            #     modelId=model_id, body=ai_request
            # )

            # Decode the response body.
            model_response = json.loads(ai_response["body"].read())

            # Extract and print the response text.
            response_text = model_response["results"][0]["outputText"]
            print(response_text)

            formatted_message = f"Bug report description:\n{description}\n\nSuggested solution:\n{response_text}"

            issue_dict = {
                'project': {'key': JIRA_PROJECT_KEY},
                'summary': title,
                'description': formatted_message,
                'issuetype': {'name': 'Task'},
            }

            new_issue = jira_client.create_issue(fields=issue_dict)
            print(f"Issue created: {new_issue.key}")

            # Delete the message from the SQS queue after processing
            sqs_client.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=receipt_handle
            )
            print(f"Message deleted from SQS queue: {receipt_handle}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

def background_thread():
    sqs_thread = threading.Thread(target=process_sqs_p2_message, daemon=True)
    sqs_thread.start()
    return sqs_thread

background_thread = background_thread()

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8002)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_flag = True
        bg_thread.join()

