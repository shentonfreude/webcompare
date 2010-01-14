new YAHOO.widget.LogReader("my_logger", {draggable:true}); 

YAHOO.util.Event.addListener(window, "load", function() {
    YAHOO.example.XHR_JSON = function() {

        var urlPath = function(url) {
            return url.replace(/http:\/\/[\w.]+/,'');
        };
        var formatUrlPath = function(elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = urlPath(sData);
        };
        var formatOriginCode = function(elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = "<a href='" + oRecord.getData("origin_url") + "' target='_origin'>" + sData + "</a>";
        };
        var formatTargetCode = function(elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = "<a href='" + oRecord.getData("target_url") + "' target='_target'>" + sData + "</a>";
        };
        var formatDownloadTime = function(elCell, oRecord, oColumn, sData) {
            // Return None if we got None, or rounded float if we got real data
            elCell.innerHTML = Math.round(sData * 100) / 100 || sData;
        };

        var resfilter = function(req,raw,res,cb) {
            var data = res.results || [];
            var filtered = [];
            var i,l;
            if (req) {
                req = req.toLowerCase();
                for (i = 0, l = data.length; i < l; ++i) {
		    if ( ! data[i].result_type.toLowerCase().indexOf(req)) {
                        filtered.push(data[i]);
                    }
                }
                res.results = filtered;
            }
            return res
        }

        var dataSource = new YAHOO.util.DataSource("http://asylum.hitsshq.com/~cshenton/webcompare/webcompare.json");
        //dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        //dataSource.connXhrMode = "queueRequests";
        dataSource.responseSchema = {
            resultsList: "results.resultlist",
            fields: ["result_type", "origin_url", "target_url", "origin_code", "target_code", "origin_time", "target_time",
                     {key:"comparisons.BodyComparator",    parser:"number"},
		     {key:"comparisons.ContentComparator", parser:"number"},
		     {key:"comparisons.LengthComparator",  parser:"number"},
		     {key:"comparisons.TitleComparator",   parser:"number"}
                    ]
        };

        var tableColumns = [
            {key:"result_type",			  label:"Result Type", sortable:true},
            {key:"origin_code",			  label:"Origin Code", sortable:true, formatter:formatOriginCode},
            {key:"target_code",			  label:"Target Code", sortable:true, formatter:formatTargetCode},
            {key:"origin_time",			  label:"Origin Time", sortable:true, formatter:formatDownloadTime},
            {key:"target_time",			  label:"Target Time", sortable:true, formatter:formatDownloadTime},
            {key:"comparisons.BodyComparator",    label:"Body",        sortable:true},
            {key:"comparisons.ContentComparator", label:"Content",     sortable:true},
            {key:"comparisons.LengthComparator",  label:"Length",      sortable:true},
            {key:"comparisons.TitleComparator",   label:"Title",       sortable:true},
            {key:"origin_url",                    label:"URL Path",    sortable:true, formatter:formatUrlPath},
        ];
	
        var dataTable = new YAHOO.widget.DataTable("resultlist", tableColumns, dataSource);

    }();
});
