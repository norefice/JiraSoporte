import jira_api

def calculate_metrics():
    issues = jira_api.get_issues()
    metrics = {
        "request_type_count": {},
        "organization_count": {},
        "request_type_by_organization": {}
    }

    for issue in issues['issues']:
        request_type = issue['fields'].get('customfield_10001', 'Unknown')
        organization = issue['fields'].get('customfield_10002', 'Unknown')

        # Ensure request_type and organization are single values
        if isinstance(request_type, list):
            request_type = request_type[0] if request_type else 'Unknown'
        if isinstance(organization, list):
            organization = organization[0] if organization else 'Unknown'
        if isinstance(request_type, dict):
            request_type = request_type.get('value', 'Unknown')
        if isinstance(organization, dict):
            organization = organization.get('value', 'Unknown')

        # Count by request type
        if request_type not in metrics['request_type_count']:
            metrics['request_type_count'][request_type] = 0
        metrics['request_type_count'][request_type] += 1

        # Count by organization
        if organization not in metrics['organization_count']:
            metrics['organization_count'][organization] = 0
        metrics['organization_count'][organization] += 1

        # Count by request type and organization
        if organization not in metrics['request_type_by_organization']:
            metrics['request_type_by_organization'][organization] = {}
        if request_type not in metrics['request_type_by_organization'][organization]:
            metrics['request_type_by_organization'][organization][request_type] = 0
        metrics['request_type_by_organization'][organization][request_type] += 1
        print(metrics)
    return metrics
