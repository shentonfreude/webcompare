// I'm not proud of this ...
// It's my first use of JavaScript, cargo-culted from the YUI site.

//new YAHOO.widget.LogReader("my_logger", {draggable:true}); 

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
            // Return rounded float if we got real data, or None if not
            elCell.innerHTML = Math.round(sData * 100) / 100 || sData;
        };

	var getResFilter = function() {
	    var resFilter = {};
	    if ( document.getElementById("ErrorResult").checked )     { resFilter["ErrorResult"] = 1 };
	    if ( document.getElementById("BadOriginResult").checked ) { resFilter["BadOriginResult"] = 1 };
	    if ( document.getElementById("BadTargetResult").checked ) { resFilter["BadTargetResult"] = 1 };
	    if ( document.getElementById("GoodResult").checked )      { resFilter["GoodResult"] = 1 };
	    console.log("resFilter return Error=" + resFilter['ErrorResult'] + " BadOrig=" + resFilter['BadOriginResult'] +
			" BadTarg=" + resFilter['BadTargetResult'] + " Good=" + resFilter['GoodResult']);
	    return resFilter;
	}
	var dataSource = new YAHOO.util.DataSource("webcompare.json",
						   {
						       doBeforeCallback : function (req,raw,res,cb) {
							   // This is the filter function
							   var data     = res.results || [];
							   var filtered = [];
							   var i,l;
							   var resFilter = getResFilter();
							   for (i = 0, l = data.length; i < l; ++i) {
							       if (data[i].result_type in resFilter) {
								   filtered.push(data[i]);
							       }
							   }
							   res.results = filtered;
							   return res;
						       }
						   }
						  );

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


	// This seems a suboptimal way of re-drawing the table, what's correct?
	var filterClick = function() {
	    // Doesn't update on filter: dataTable.render();
	    // Seems Overkill:
            var dataTable = new YAHOO.widget.DataTable("resultlist", tableColumns, dataSource);
	}
	YAHOO.util.Event.addListener('filter','click', filterClick);


    }();

});
