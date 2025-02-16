function renderTables(data) {
    var metricsDiv = document.getElementById('metrics');
    var organizationMetrics = {};
    var requestTypeMetrics = {};
    var createdIssues = {};
    var resolvedIssues = {};
    var requestTypeByOrg = {};

    data.forEach(issue => {
        var orgName = issue.organization_name || 'Unknown';
        if (!organizationMetrics[orgName]) {
            organizationMetrics[orgName] = { total: 0, open: 0, closed: 0 };
        }
        organizationMetrics[orgName].total++;

        if (issue.status === 'FINALIZADO') {
            organizationMetrics[orgName].closed++;
        } else {
            organizationMetrics[orgName].open++;
        }

        var requestTypeName = issue.request_type_name || 'Unknown';
        if (!requestTypeMetrics[requestTypeName]) {
            requestTypeMetrics[requestTypeName] = 0;
        }
        requestTypeMetrics[requestTypeName]++;

        if (!requestTypeByOrg[requestTypeName]) {
            requestTypeByOrg[requestTypeName] = {};
        }
        if (!requestTypeByOrg[requestTypeName][orgName]) {
            requestTypeByOrg[requestTypeName][orgName] = { open: 0, closed: 0 };
        }
        if (issue.status === 'FINALIZADO') {
            requestTypeByOrg[requestTypeName][orgName].closed++;
        } else {
            requestTypeByOrg[requestTypeName][orgName].open++;
        }

        var createdDate = issue.created.split(' ')[0];
        if (!createdIssues[createdDate]) {
            createdIssues[createdDate] = 0;
        }
        createdIssues[createdDate]++;

        var resolvedDate = issue.resolution_date ? issue.resolution_date.split(' ')[0] : null;
        if (resolvedDate) {
            if (!resolvedIssues[resolvedDate]) {
                resolvedIssues[resolvedDate] = 0;
            }
            resolvedIssues[resolvedDate]++;
        }
    });

    var orgTableHtml = '<div class="table-container"><table class="striped"><thead><tr><th>Organization Name</th><th>Total Issues</th><th>Open Issues</th><th>Closed Issues</th></tr></thead><tbody>';
    for (var orgName in organizationMetrics) {
        orgTableHtml += `<tr><td>${orgName}</td><td>${organizationMetrics[orgName].total}</td><td>${organizationMetrics[orgName].open}</td><td>${organizationMetrics[orgName].closed}</td></tr>`;
    }
    orgTableHtml += '</tbody></table></div>';

    var requestTypeTableHtml = '<div class="table-container"><table class="striped"><thead><tr><th>Request Type Name</th><th>Total Issues</th></tr></thead><tbody>';
    for (var requestTypeName in requestTypeMetrics) {
        requestTypeTableHtml += `<tr><td>${requestTypeName}</td><td>${requestTypeMetrics[requestTypeName]}</td></tr>`;
    }
    requestTypeTableHtml += '</tbody></table></div>';

    var requestTypeByOrgTableHtml = '<div class="table-container"><table class="striped"><thead><tr><th>Request Type</th>';
    for (var orgName in organizationMetrics) {
        requestTypeByOrgTableHtml += `<th>${orgName} (Open)</th><th>${orgName} (Closed)</th>`;
    }
    requestTypeByOrgTableHtml += '</tr></thead><tbody>';
    for (var requestTypeName in requestTypeByOrg) {
        requestTypeByOrgTableHtml += `<tr><td>${requestTypeName}</td>`;
        for (var orgName in organizationMetrics) {
            var openIssues = requestTypeByOrg[requestTypeName][orgName] ? requestTypeByOrg[requestTypeName][orgName].open : 0;
            var closedIssues = requestTypeByOrg[requestTypeName][orgName] ? requestTypeByOrg[requestTypeName][orgName].closed : 0;
            requestTypeByOrgTableHtml += `<td>${openIssues}</td><td>${closedIssues}</td>`;
        }
        requestTypeByOrgTableHtml += '</tr>';
    }
    requestTypeByOrgTableHtml += '</tbody></table></div>';

    metricsDiv.innerHTML = orgTableHtml + '<br>' + requestTypeTableHtml + '<br>' + requestTypeByOrgTableHtml;

    return { createdIssues, resolvedIssues };
}
