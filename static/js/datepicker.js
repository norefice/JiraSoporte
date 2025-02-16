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
});
