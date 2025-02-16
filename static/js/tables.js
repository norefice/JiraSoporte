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

    var orgTableHtml = '<h2>Issues por Organización</h2><button onclick="exportTableToExcel(\'orgTable\', \'issues_por_organizacion\')">Exportar a Excel</button><div class="table-container"><table id="orgTable" class="striped"><thead><tr><th>Organization Name</th><th>Total Issues</th><th>Open Issues</th><th>Closed Issues</th></tr></thead><tbody>';
    for (var orgName in organizationMetrics) {
        orgTableHtml += `<tr><td>${orgName}</td><td>${organizationMetrics[orgName].total}</td><td>${organizationMetrics[orgName].open}</td><td>${organizationMetrics[orgName].closed}</td></tr>`;
    }
    orgTableHtml += '</tbody></table></div>';

    var requestTypeTableHtml = '<h2>Issues por Tipo de Solicitud</h2><button onclick="exportTableToExcel(\'requestTypeTable\', \'issues_por_tipo_de_solicitud\')">Exportar a Excel</button><div class="table-container"><table id="requestTypeTable" class="striped"><thead><tr><th>Request Type Name</th><th>Total Issues</th></tr></thead><tbody>';
    for (var requestTypeName in requestTypeMetrics) {
        requestTypeTableHtml += `<tr><td>${requestTypeName}</td><td>${requestTypeMetrics[requestTypeName]}</td></tr>`;
    }
    requestTypeTableHtml += '</tbody></table></div>';

    var requestTypeByOrgTableHtml = '<h2>Issues por Tipo de Solicitud y Organización</h2><button onclick="exportTableToExcel(\'requestTypeByOrgTable\', \'issues_por_tipo_de_solicitud_y_organizacion\')">Exportar a Excel</button><div class="table-container"><table id="requestTypeByOrgTable" class="striped"><thead><tr><th>Request Type</th>';
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
