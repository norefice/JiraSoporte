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

    var orgTableHtml = '<h2>Issues por Organización</h2><button class="btn waves-effect waves-light" onclick="exportTableToExcel(\'orgTable\', \'issues_por_organizacion\')">Exportar a Excel</button><div class="table-container"><table id="orgTable" class="striped"><thead><tr><th>Organization Name</th><th>Total Issues</th><th>Open Issues</th><th>Closed Issues</th></tr></thead><tbody>';
    var startDate = document.getElementById('start_date').value;
    var endDate = document.getElementById('end_date').value;
    for (var orgName in organizationMetrics) {
        orgTableHtml += `<tr><td><a href="/issues_by_org?org_name=${orgName}&start_date=${startDate}&end_date=${endDate}">${orgName}</a></td><td>${organizationMetrics[orgName].total}</td><td>${organizationMetrics[orgName].open}</td><td>${organizationMetrics[orgName].closed}</td></tr>`;
    }
    orgTableHtml += '</tbody></table></div>';

    var requestTypeTableHtml = '<h2>Issues por Tipo de Solicitud</h2><button class="btn waves-effect waves-light" onclick="exportTableToExcel(\'requestTypeTable\', \'issues_por_tipo_de_solicitud\')">Exportar a Excel</button><div class="table-container"><table id="requestTypeTable" class="striped"><thead><tr><th>Request Type Name</th><th>Total Issues</th></tr></thead><tbody>';
    for (var requestTypeName in requestTypeMetrics) {
        requestTypeTableHtml += `<tr><td>${requestTypeName}</td><td>${requestTypeMetrics[requestTypeName]}</td></tr>`;
    }
    requestTypeTableHtml += '</tbody></table></div>';

    var requestTypeByOrgTableHtml = '<h2>Issues por Tipo de Solicitud y Organización</h2><button class="btn waves-effect waves-light" onclick="exportTableToExcel(\'requestTypeByOrgTable\', \'issues_por_tipo_de_solicitud_y_organizacion\')">Exportar a Excel</button><div class="table-container"><table id="requestTypeByOrgTable" class="striped"><thead><tr><th>Request Type</th>';
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

function exportTableToExcel(tableID, filename = '') {
    var table = document.getElementById(tableID);
    var wb = XLSX.utils.table_to_book(table, { sheet: "Sheet1" });
    var wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'binary' });

    function s2ab(s) {
        var buf = new ArrayBuffer(s.length);
        var view = new Uint8Array(buf);
        for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
    }

    var blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename ? filename + '.xlsx' : 'excel_data.xlsx';
    link.click();
}

function exportAllTablesToExcel() {
    var wb = XLSX.utils.book_new();

    var orgTable = document.getElementById('orgTable');
    var orgSheet = XLSX.utils.table_to_sheet(orgTable);
    XLSX.utils.book_append_sheet(wb, orgSheet, 'Org Issues');

    var requestTypeTable = document.getElementById('requestTypeTable');
    var requestTypeSheet = XLSX.utils.table_to_sheet(requestTypeTable);
    XLSX.utils.book_append_sheet(wb, requestTypeSheet, 'Request Type Issues');

    var requestTypeByOrgTable = document.getElementById('requestTypeByOrgTable');
    var requestTypeByOrgSheet = XLSX.utils.table_to_sheet(requestTypeByOrgTable);
    XLSX.utils.book_append_sheet(wb, requestTypeByOrgSheet, 'Request Type by Org');

    var wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'binary' });

    function s2ab(s) {
        var buf = new ArrayBuffer(s.length);
        var view = new Uint8Array(buf);
        for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
    }

    var blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = 'all_tables.xlsx';
    link.click();
}
