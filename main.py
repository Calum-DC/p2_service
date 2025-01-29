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


QUEUE_URL = os.getenv('SQS_P1_URL')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')

jira_client = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))


def process_sqs_p2_message():

    title = "Pre-test 1"
    description = "Jira create issue functionality.....working??"

    issue_dict = {
        'project': {'key': "PMC"},
        'summary': title,
        'description': description,
        'issuetype': {'name': 'Task'},
    }

    new_issue = jira_client.create_issue(fields=issue_dict)

    print(f"Issue created: {new_issue.key}")




if __name__ == '__main__':
    process_sqs_p2_message()
    app.run(debug=False)