document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.datepicker');
    var instances = M.Datepicker.init(elems, {
        format: 'yyyy-mm-dd',
        showClearBtn: true,
        onClose: function() {
            var startDate = document.getElementById('start_date').value;
            var endDate = document.getElementById('end_date').value;
            if (startDate && !endDate) {
                document.getElementById('end_date').focus();
            }
        },
        onSelect: function(date) {
            var startDateElem = document.getElementById('start_date');
            var endDateElem = document.getElementById('end_date');
            if (!startDateElem.value) {
                startDateElem.value = date.toISOString().split('T')[0];
            } else if (!endDateElem.value) {
                endDateElem.value = date.toISOString().split('T')[0];
                instances[0].close();
            }
        }
    });

    var chartInstance = null;

    document.getElementById('date_form').addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        var loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.style.display = 'flex';
        fetch('/issue', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            var { createdIssues, resolvedIssues } = renderTables(data);

            // Prepare data for the chart
            var startDate = new Date(document.getElementById('start_date').value);
            var endDate = new Date(document.getElementById('end_date').value);
            var labels = [];
            var currentDate = new Date(startDate);

            while (currentDate <= endDate) {
                labels.push(currentDate.toISOString().split('T')[0]);
                currentDate.setDate(currentDate.getDate() + 1);
            }

            var createdData = labels.map(date => createdIssues[date] || 0);
            var resolvedData = labels.map(date => resolvedIssues[date] || 0);

            console.log('Labels:', labels); // Debugging
            console.log('Created Data:', createdData); // Debugging
            console.log('Resolved Data:', resolvedData); // Debugging

            renderChart(labels, createdData, resolvedData);

            // Show the chart title and canvas
            var issuesChartTitle = document.getElementById('issuesChartTitle');
            var issuesChart = document.getElementById('issuesChart');
            issuesChartTitle.style.display = 'block';
            issuesChart.style.display = 'block';
        })
        .finally(() => {
            loadingOverlay.style.display = 'none';
        });
    });
});
