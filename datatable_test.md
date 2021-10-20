<script type="text/javascript" src="js/datatable.min.js"></script>

var datatable = new DataTable(document.getElementById('MyTable'), {
    pageSize: 15,
    sort: '*'
});

datatable.loadPage(3);
var data = datatable.all();
datatable.deleteAll(function (e) {
    return e.title.trim().length > 0;
});

<script type="text/javascript" src="js/jquery.min.js"></script> 
<script type="text/javascript" src="js/datatable.min.js"></script>
<script type="text/javascript" src="js/datatable.jquery.min.js"></script>

$('#MyTable').datatable({
    pageSize: 15,
    sort: '*'
}) ;

$('#MyTable').datatable('page', 3);
var data = $('#MyTable').datatable('select');
$('#MyTable').datatable('delete', function (e) {
    return e.title.trim().length > 0;
});
