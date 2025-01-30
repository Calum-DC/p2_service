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
load_dotenv()
sqs_client = boto3.client('sqs', region_name=os.getenv('AWS_REGION'))


QUEUE_URL = os.getenv('SQS_P2_URL')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')

jira_client = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))


def process_sqs_p2_message():
    while True:
        try:
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

            issue_dict = {
                'project': {'key': JIRA_PROJECT_KEY},
                'summary': title,
                'description': description,
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

@app.route('/health', methods=["GET"])
def health_check():
    return "Everything is A-OK"


if __name__ == '__main__':
    # Run the function in a separate thread
    threading.Thread(target=process_sqs_p2_message, daemon=True).start()

    app.run(debug=False, port=5002)