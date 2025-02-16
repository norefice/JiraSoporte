import requests
from requests.auth import HTTPBasicAuth
import config
import json
from datetime import datetime

def get_issues():
    url = f"{config.JIRA_URL}/rest/api/3/search"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }
    query = {
        "jql": f"project={config.PROJECT_CODE}",
        "maxResults": 1000
    }
    response = requests.get(url, headers=headers, auth=auth, params=query)
    return response.json()

def issue_search(jql="project = SOP", max_results=2000, start_at=0, start_date=None, end_date=None):
    url = f"{config.JIRA_URL}/rest/api/3/search"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    date_filter = ""
    if start_date and end_date:
        date_filter = f" AND created >= '{start_date}' AND created <= '{end_date}'"
    elif start_date:
        date_filter = f" AND created >= '{start_date}'"
    elif end_date:
        date_filter = f" AND created <= '{end_date}'"

    jql += date_filter

    payload = json.dumps({
        "expand": [],
        "fields": [
            "created",            # Created
            "issuetype",          # Issue Type
            "key",                # Issue Key
            "status",             # Status
            config.CUSTOM_FIELDS["organizations"],  # Organizations
            config.CUSTOM_FIELDS["request_type"],   # Request Type
            "summary",            # Summary
            config.CUSTOM_FIELDS["impacto"],        # Impacto
            config.CUSTOM_FIELDS["impact"],         # Impact
            config.CUSTOM_FIELDS["vulnerability"],  # Vulnerability
            config.CUSTOM_FIELDS["information"],    # Information
            config.CUSTOM_FIELDS["severity"],       # Severity
            "labels",             # Labels
            "creator",            # Creator
            config.CUSTOM_FIELDS["satisfaction"],   # Satisfaction
            config.CUSTOM_FIELDS["date_of_first_response"],  # Date of First Response
            "resolutiondate",     # Resolved
            config.CUSTOM_FIELDS["time_to_resolution"],      # Time to resolution
            config.CUSTOM_FIELDS["time_to_first_response"],  # Time to first response
            config.CUSTOM_FIELDS["time_to_resolution_custom"]  # Time to resolution
        ],
        "fieldsByKeys": True,
        "jql": jql,
        "maxResults": max_results,
        "startAt": start_at
    })

    response = requests.post(url, data=payload, headers=headers, auth=auth)

    if response.status_code == 200:
        data = response.json()
        issues = data.get("issues", [])
        processed_issues = []

        for issue in issues:
            fields = issue["fields"]

            processed_issue = {
                "issue_id": issue.get("id"),
                "issue_key": issue.get("key"),
                "summary": fields.get("summary"),
                "created": date_format(fields.get("created")),
                "status": fields["status"].get("name"),
                "resolution_date": date_format(fields.get("resolutiondate")),
                "creator_name": fields.get("creator", {}).get("displayName"),
                "creator_email": fields.get("creator", {}).get("emailAddress"),
                "request_type_name": fields.get(config.CUSTOM_FIELDS["request_type"], {}).get("requestType", {}).get("name"),
                "current_status": fields.get(config.CUSTOM_FIELDS["request_type"], {}).get("currentStatus", {}).get("status"),
                "organization_name": next((org.get("name") for org in issue["fields"].get(config.CUSTOM_FIELDS["organizations"], [])), ""),
                "organization_id": next((int(org.get("id")) for org in issue["fields"].get(config.CUSTOM_FIELDS["organizations"], [])), ""),
                "impacto": fields.get(config.CUSTOM_FIELDS["impacto"]),
                "impact": fields.get(config.CUSTOM_FIELDS["impact"]),
                "vulnerability": fields.get(config.CUSTOM_FIELDS["vulnerability"]),
                "information": fields.get(config.CUSTOM_FIELDS["information"]),
                "severity": fields.get(config.CUSTOM_FIELDS["severity"]),
                "labels": fields.get("labels"),
                "satisfaction": fields.get(config.CUSTOM_FIELDS["satisfaction"]),
                "date_of_first_response": date_format(fields.get(config.CUSTOM_FIELDS["date_of_first_response"])),
                "time_to_resolution": date_format(get_breach_time(fields.get(config.CUSTOM_FIELDS["time_to_resolution"]))),
                "time_to_first_response": date_format(get_breach_time(fields.get(config.CUSTOM_FIELDS["time_to_first_response"]))),
                "time_to_resolution_custom": date_format(fields.get(config.CUSTOM_FIELDS["time_to_resolution_custom"]))
            }
            processed_issues.append(processed_issue)
        print(processed_issues) #DEBUG
        for processed_issue in processed_issues:
            for key, value in processed_issue.items():
                if value is None:
                    processed_issue[key] = ""
        return processed_issues
    else:
        print(f"Error en la solicitud: {response.status_code}")
        print(response.text)
        return None

def date_format(date):
    if isinstance(date, dict):
        date = date.get("jira")
    if date is None:
        return ""
    # Parsear la cadena de tiempo
    original_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    process_date = datetime.strptime(date, original_format)
    # Formatear la fecha en el formato deseado
    custom_format = "%Y-%m-%d %H:%M:00"  # Ejemplo: 2025-02-17 14:13:00 
    return process_date.strftime(custom_format)

def get_breach_time(customfield):
    if customfield and "completedCycles" in customfield and customfield["completedCycles"]:
        return customfield["completedCycles"][0].get("breachTime", {}).get("jira")
    return None