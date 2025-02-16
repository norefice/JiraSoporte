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

def issue_search(jql="project = SOP", max_results=2000, start_at=0):
    url = f"{config.JIRA_URL}/rest/api/3/search"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "expand": [],
        "fields": [
            "created",            # Created
            "issuetype",          # Issue Type
            "key",                # Issue Key
            "status",             # Status
            "customfield_10002",  # Organizations
            "customfield_10010",  # Request Type
            "summary",            # Summary
            "customfield_10066",  # Impacto
            "customfield_10004",  # Impact
            "customfield_10060",  # Vulnerability
            "customfield_10067",  # Information
            "customfield_10101",  # Severity
            "labels",             # Labels
            "creator",            # Creator
            "customfield_10034",  # Satisfaction
            "customfield_10024",  # Date of First Response
            "resolutiondate",     # Resolved
            "customfield_10094",  # Time to resolution
            "customfield_10095",  # Time to first response
            "customfield_10098"   # Time to resolution
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
                "request_type_name": fields.get("customfield_10010", {}).get("requestType", {}).get("name"),
                "current_status": fields.get("customfield_10010", {}).get("currentStatus", {}).get("status"),
                "organization_name": next((org.get("name") for org in issue["fields"].get("customfield_10002", [])), ""),
                "organization_id": next((int(org.get("id")) for org in issue["fields"].get("customfield_10002", [])), ""),
                "impacto": fields.get("customfield_10066"),
                "impact": fields.get("customfield_10004"),
                "vulnerability": fields.get("customfield_10060"),
                "information": fields.get("customfield_10067"),
                "severity": fields.get("customfield_10101"),
                "labels": fields.get("labels"),
                "satisfaction": fields.get("customfield_10034"),
                "date_of_first_response": date_format(fields.get("customfield_10024")),
                "time_to_resolution": date_format(get_breach_time(fields.get("customfield_10094"))),
                "time_to_first_response": date_format(get_breach_time(fields.get("customfield_10095"))),
                "time_to_resolution_custom": date_format(fields.get("customfield_10098"))
            }
            processed_issues.append(processed_issue)

        for processed_issue in processed_issues:
            for key, value in processed_issue.items():
                if value is None:
                    processed_issue[key] = ""
                    
        print(processed_issues) #DEBUG
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