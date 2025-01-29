import boto3
import json
import os

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


def process_sqs_p2_message():








if __name__ == '__main__':
    app.run(debug=True)