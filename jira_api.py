import requests
from requests.auth import HTTPBasicAuth
import config
import json
from datetime import datetime

def issue_search(jql=None, max_results=100, start_at=0, start_date=None, end_date=None):
    if jql is None:
        jql = f"project = {config.PROJECT_CODE}"
    url = f"{config.JIRA_URL}/rest/api/3/search/jql"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # JQL: incluir todo el dÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ­a final usando < dÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ­a siguiente
    date_filter = ""
    if start_date and end_date:
        from datetime import datetime as dt, timedelta
        try:
            end_dt = dt.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            end_next = end_dt.strftime("%Y-%m-%d")
            date_filter = f" AND created >= '{start_date}' AND created < '{end_next}'"
        except ValueError:
            date_filter = f" AND created >= '{start_date}' AND created <= '{end_date}'"
    elif start_date:
        date_filter = f" AND created >= '{start_date}'"
    elif end_date:
        try:
            from datetime import datetime as dt, timedelta
            end_dt = dt.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            date_filter = f" AND created < '{end_dt.strftime('%Y-%m-%d')}'"
        except ValueError:
            date_filter = f" AND created <= '{end_date}'"

    jql += date_filter
    print(f"[JIRA] JQL: {jql}")

    all_issues = []
    next_page_token = None

    while True:
        payload_dict = {
            "fields": [
                "created",
                "issuetype",
                "key",
                "status",
                config.CUSTOM_FIELDS["organizations"],
                config.CUSTOM_FIELDS["request_type"],
                "summary",
                config.CUSTOM_FIELDS["impacto"],
                config.CUSTOM_FIELDS["impact"],
                config.CUSTOM_FIELDS["vulnerability"],
                config.CUSTOM_FIELDS["information"],
                config.CUSTOM_FIELDS["severity"],
                "labels",
                "creator",
                config.CUSTOM_FIELDS["satisfaction"],
                config.CUSTOM_FIELDS["date_of_first_response"],
                "resolutiondate",
                config.CUSTOM_FIELDS["time_to_resolution"],
                config.CUSTOM_FIELDS["time_to_first_response"],
                config.CUSTOM_FIELDS["time_to_resolution_custom"]
            ],
            "fieldsByKeys": True,
            "jql": jql,
            "maxResults": max_results,
        }
        if next_page_token is not None:
            payload_dict["nextPageToken"] = next_page_token

        response = requests.post(url, data=json.dumps(payload_dict), headers=headers, auth=auth)

        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)
            next_page_token = data.get("nextPageToken")
            if not next_page_token or not issues:
                break
        else:
            error_msg = f"JIRA API error {response.status_code}: {response.text[:500]}"
            print(error_msg)
            return {"error": error_msg, "issues": None}

    processed_issues = []

    for issue in all_issues:
        try:
            fields = issue.get("fields", {})
            status_obj = fields.get("status") or {}
            orgs = fields.get(config.CUSTOM_FIELDS["organizations"], [])
            req_type = fields.get(config.CUSTOM_FIELDS["request_type"], {}) or {}

            processed_issue = {
                "issue_id": issue.get("id"),
                "issue_key": issue.get("key"),
                "summary": fields.get("summary"),
                "created": date_format(fields.get("created")),
                "status": status_obj.get("name", ""),
                "resolution_date": date_format(fields.get("resolutiondate")),
                "creator_name": (fields.get("creator") or {}).get("displayName"),
                "creator_email": (fields.get("creator") or {}).get("emailAddress"),
                "request_type_name": (req_type.get("requestType") or {}).get("name"),
                "current_status": (req_type.get("currentStatus") or {}).get("status"),
                "organization_name": next((org.get("name") for org in orgs), "") if isinstance(orgs, list) else "",
                "organization_id": next((int(org.get("id")) for org in orgs if org.get("id")), "") if isinstance(orgs, list) else "",
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
        except Exception as e:
            print(f"Error procesando issue {issue.get('key', '?')}: {e}")
            continue

    for processed_issue in processed_issues:
        for key, value in processed_issue.items():
            if value is None:
                processed_issue[key] = ""
    return processed_issues

def date_format(date):
    if isinstance(date, dict):
        date = date.get("jira")
    if date is None or date == "":
        return ""
    if not isinstance(date, str):
        return str(date)
    # Formatos que JIRA puede devolver
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            process_date = datetime.strptime(date.replace("Z", "+00:00").rstrip("Z"), fmt)
            return process_date.strftime("%Y-%m-%d %H:%M:00")
        except (ValueError, TypeError):
            continue
    return date[:19] if len(date) >= 19 else date  # fallback: primeros 19 chars

def get_breach_time(customfield):
    if customfield and "completedCycles" in customfield and customfield["completedCycles"]:
        return customfield["completedCycles"][0].get("breachTime", {}).get("jira")
    return None

def get_issues_by_org(org_name, start_date=None, end_date=None):
    if not org_name:
        return []
        
    try:
        jql = f"project = {config.PROJECT_CODE} AND organizations = '{org_name}'"
        result = issue_search(jql=jql, start_date=start_date, end_date=end_date)
        if isinstance(result, dict) and result.get("issues") is None:
            return []
        return result if result is not None else []
    except Exception as e:
        print(f"Error getting issues for organization {org_name}: {str(e)}")
        return []

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

def get_available_transitions(issue_key):
    url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, auth=auth)
    
    if response.status_code == 200:
        transitions_data = response.json()
        transitions = []
        
        # Print available transitions for debugging
        print("Available transitions:")
        for transition in transitions_data.get("transitions", []):
            print(f"ID: {transition['id']}, Name: {transition['name']}")
            transitions.append({
                "id": transition["id"],
                "name": transition["name"]
            })
        
        return transitions
    return []

def change_status(issue_key, new_status):
    url = f"{config.JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # First, get all available transitions
    transitions = get_available_transitions(issue_key)
    
    # Map our status names to Jira transition names
    status_mapping = {
        "CREADO": ["Start progress"],
        "EN PROCESO": ["Start progress"],
        "FINALIZADO": ["Mark as done"]
    }
    
    # Find the matching transition
    transition_id = None
    for transition in transitions:
        if any(status.lower() == transition["name"].lower() for status in status_mapping[new_status]):
            transition_id = transition["id"]
            break
    
    if not transition_id:
        print(f"Could not find transition ID for status: {new_status}")
        print("Available transitions:", transitions)
        return False

    payload = json.dumps({
        "transition": {
            "id": transition_id
        }
    })

    print(f"Sending transition request with payload: {payload}")
    response = requests.post(url, data=payload, headers=headers, auth=auth)
    
    if response.status_code != 204:
        print(f"Failed to change status. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    return True