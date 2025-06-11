import requests
from requests.auth import HTTPBasicAuth
import config
import json
from datetime import datetime

def issue_search(jql="project = SOP", max_results=100, start_at=0, start_date=None, end_date=None):
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

    all_issues = []
    total = 1  # Inicializamos con un valor mayor a start_at para entrar en el bucle

    while start_at < total:
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
            total = data.get("total", 0)
            all_issues.extend(issues)
            start_at += max_results
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print(response.text)
            return None

    processed_issues = []

    for issue in all_issues:
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

    for processed_issue in processed_issues:
        for key, value in processed_issue.items():
            if value is None:
                processed_issue[key] = ""
    return processed_issues

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

def get_issues_by_org(org_name, start_date=None, end_date=None):
    jql = f"project = SOP AND organizations = '{org_name}'"
    return issue_search(jql=jql, start_date=start_date, end_date=end_date)

def format_atlassian_doc(doc):
    if not doc:
        return ""
    
    if isinstance(doc, str):
        return doc
        
    if isinstance(doc, dict):
        if doc.get('type') == 'doc':
            content = []
            for block in doc.get('content', []):
                if block.get('type') == 'paragraph':
                    text = []
                    for item in block.get('content', []):
                        if item.get('type') == 'text':
                            text.append(item.get('text', ''))
                        elif item.get('type') == 'hardBreak':
                            text.append('<br>')
                    content.append('<p>' + ''.join(text) + '</p>')
                elif block.get('type') == 'expand':
                    for media_block in block.get('content', []):
                        if media_block.get('type') == 'mediaSingle':
                            for media in media_block.get('content', []):
                                if media.get('type') == 'media':
                                    attrs = media.get('attrs', {})
                                    if attrs.get('type') == 'external':
                                        content.append(f'<img src="{attrs.get("url")}" alt="Image" style="max-width: 100%;">')
            return '\n'.join(content)
    return str(doc)

def get_issue_details(issue_key):
    url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, auth=auth)
    
    if response.status_code == 200:
        issue_data = response.json()
        fields = issue_data["fields"]
        
        # Get comments
        comments_url = f"{url}/comment"
        comments_response = requests.get(comments_url, headers=headers, auth=auth)
        comments = []
        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            for comment in comments_data.get("comments", []):
                comments.append({
                    "author": comment["author"]["displayName"],
                    "created": date_format(comment["created"]),
                    "body": format_atlassian_doc(comment["body"])
                })

        # Get attachments
        attachments = []
        for attachment in fields.get("attachment", []):
            attachments.append({
                "filename": attachment["filename"],
                "content": attachment["content"],
                "size": attachment["size"]
            })

        return {
            "issue_id": issue_data["id"],
            "issue_key": issue_data["key"],
            "summary": fields.get("summary"),
            "description": format_atlassian_doc(fields.get("description")),
            "status": fields["status"]["name"],
            "created": date_format(fields.get("created")),
            "resolution_date": date_format(fields.get("resolutiondate")),
            "creator_name": fields.get("creator", {}).get("displayName"),
            "creator_email": fields.get("creator", {}).get("emailAddress"),
            "request_type_name": fields.get(config.CUSTOM_FIELDS["request_type"], {}).get("requestType", {}).get("name"),
            "organization_name": next((org.get("name") for org in fields.get(config.CUSTOM_FIELDS["organizations"], [])), ""),
            "comments": comments,
            "attachments": attachments
        }
    return None

def add_comment(issue_key, body, comment_type="internal", files=None):
    # First, add the comment
    comment_url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Create Atlassian Document Format for the comment
    comment_doc = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": body
                    }
                ]
            }
        ]
    }

    # Prepare the payload
    payload = {
        "body": comment_doc
    }

    # Add visibility restriction for internal comments
    if comment_type == "internal":
        payload["properties"] = [
            {
                "key": "sd.public.comment",
                "value": {
                    "internal": True
                }
            }
        ]

    response = requests.post(comment_url, data=json.dumps(payload), headers=headers, auth=auth)
    
    if response.status_code != 201:
        print(f"Failed to add comment. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    # If there are files, attach them
    if files:
        comment_id = response.json()["id"]
        for file in files:
            if file.filename:  # Check if a file was selected
                # Prepare the attachment
                files = {
                    'file': (file.filename, file.read(), file.content_type)
                }
                
                # Upload the attachment
                attachment_url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}/attachments"
                attachment_headers = {
                    "Accept": "application/json",
                    "X-Atlassian-Token": "no-check"
                }
                
                attachment_response = requests.post(
                    attachment_url,
                    files=files,
                    headers=attachment_headers,
                    auth=auth
                )
                
                if attachment_response.status_code != 200:
                    print(f"Failed to attach file {file.filename}. Status: {attachment_response.status_code}")
                    print(f"Response: {attachment_response.text}")
                    continue

    return True

def change_status(issue_key, new_status_id):
    url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "transition": {
            "id": new_status_id
        }
    })

    response = requests.post(url, data=payload, headers=headers, auth=auth)
    return response.status_code == 204