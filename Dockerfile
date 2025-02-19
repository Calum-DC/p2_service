FROM python

ENV JIRA_URL=""
ENV JIRA_EMAIL=""
ENV JIRA_API_TOKEN=""
ENV JIRA_PROJECT_KEY=""
ENV SQS_P2_URL=""
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_REGION=""

WORKDIR /p2_service
COPY . /p2_service
RUN pip install -r requirements.txt
EXPOSE 8002
CMD ["gunicorn", "--bind","0.0.0.0:8002", "main:app"]
