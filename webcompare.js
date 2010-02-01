/*jslint browser: true, undef: true, nomen: true,
  eqeqeq: true, plusplus: true, bitwise: true, regexp: true, strict: true,
  newcap: true, immed: true,
  indent: 4, white: true, onevar: false
*/
/*global YAHOO, window */

// I'm not proud of this: my first JavaScript, cargo-culted from the YUI site.


"use strict";
YAHOO.util.Event.addListener(window, "load", function () {
    YAHOO.example.XHR_JSON = function () {
        
        var urlPath = function (url) {
            return url.replace(/http:\/\/[\w.]+/, '');
        };
        var formatUrlPath = function (elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = urlPath(sData);
        };
        var formatOriginCode = function (elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = "<a href='" + oRecord.getData("origin_url") +
                "' target='_origin'>" + sData + "</a>";
        };
        var formatTargetCode = function (elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = (sData ?
                                "<a href='" + oRecord.getData("target_url") +
                                "' target='_target'>" + sData + "</a>" : '');
        };
        var formatDownloadTime = function (elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = Math.round(sData * 100) / 100 || sData;
        };
        var formatHtmlErrors = function (elCell, oRecord, oColumn, sData) {
            elCell.innerHTML = (sData ? sData.length : '');
        };
        var getResFilter = function () {
            var resFilter = {};
            resFilter.ErrorResult     = (document.getElementById("ErrorResult").checked === true);
            resFilter.BadOriginResult = (document.getElementById("BadOriginResult").checked === true);
            resFilter.BadTargetResult = (document.getElementById("BadTargetResult").checked === true);
            resFilter.GoodResult      = (document.getElementById("GoodResult").checked === true);
            return resFilter;
        };

        // This duplicates the json loading but I don't know yet how else to
        // process the same data to get stats AND filtered result details.
        var statsSource = new YAHOO.util.DataSource("webcompare.json");
        statsSource.responseSchema = {
            resultsList: "results.stats",
            fields:      ["ErrorResult", "BadOriginResult", "BadTargetResult", "GoodResult"]
        };
        var statsColumns = [
            {key: "ErrorResult",         label: "ErrorResult"},
            {key: "BadOriginResult",     label: "BadOriginResult"},
            {key: "BadTargetResult",     label: "BadTargetResult"},
            {key: "GoodResult",          label: "GoodResult"}
            ]
        var statsTable = new YAHOO.widget.DataTable("statsTable", statsColumns, statsSource);

        var dataSource = new YAHOO.util.DataSource("webcompare.json", {
            doBeforeCallback : function (req, raw, res, cb) { // filter
                var data     = res.results || [];
                var filtered = [];
                var i, l;
                var resFilter = getResFilter();
                for (i = 0, l = data.length; i < l; i = i + 1) {
                    if (resFilter[data[i].result_type] === true) {
                        filtered.push(data[i]);
                    }
                }
                res.results = filtered;
                return res;
            }
        });
        dataSource.responseSchema = {
            resultsList: "results.resultlist",
            fields: ["result_type",
                     "origin_url", "target_url",
                     "origin_code", "target_code",
                     "origin_time", "target_time",
                     "origin_html_errors", "target_html_errors",
                     {key: "comparisons.BodyComparator",    parser: "number"},
                     {key: "comparisons.ContentComparator", parser: "number"},
                     {key: "comparisons.LengthComparator",  parser: "number"},
                     {key: "comparisons.TitleComparator",   parser: "number"}
                    ]
        };

        var tableColumns = [
            {key: "result_type",                   label: "Result<br/>Type",      sortable: true},
            {key: "origin_code",                   label: "Origin<br/>Code",      sortable: true, formatter: formatOriginCode},
            {key: "target_code",                   label: "Target<br/>Code",      sortable: true, formatter: formatTargetCode},
            {key: "origin_time",                   label: "Origin<br/>Time",      sortable: true, formatter: formatDownloadTime},
            {key: "target_time",                   label: "Target<br/>Time",      sortable: true, formatter: formatDownloadTime},
            {key: "origin_html_errors",            label: "Origin<br/>Errors",    sortable: true, formatter: formatHtmlErrors},
            {key: "target_html_errors",            label: "Target<br/>Errors",    sortable: true, formatter: formatHtmlErrors},
            {key: "comparisons.BodyComparator",    label: "Body<br/>proxim",      sortable: true},
            {key: "comparisons.ContentComparator", label: "Content<br/>proxim",   sortable: true},
            {key: "comparisons.LengthComparator",  label: "Length<br/>proxim",    sortable: true},
            {key: "comparisons.TitleComparator",   label: "Title<br/>proxim",     sortable: true},
            {key: "origin_url",                    label: "URL Path",             sortable: true, formatter: formatUrlPath}
        ];
        
        var dataTable = new YAHOO.widget.DataTable("resultlist", tableColumns, dataSource);
        dataTable.set("seletionMode", "singlecell");
        dataTable.subscribe("cellClickEvent", function (oArgs) {
            var html_errors;
            var ln;
            var rec = this.getRecord(oArgs.target);
            var data = rec.getData();
            var mywin;
            if (oArgs.target.headers.indexOf("origin_html_errors") >= 0) {
                html_errors = data.origin_html_errors;
            }
            if (oArgs.target.headers.indexOf("target_html_errors") >= 0) {
                html_errors = data.target_html_errors;
            }
            if (html_errors !== undefined) {
                for (ln = 0; ln < html_errors.length; ln = ln + 1) {
                    html_errors[ln] = html_errors[ln].replace(/</g, '&lt;').replace(/>/g, '&gt;');
                }
                mywin = window.open('', "popWindow", 'height=400,location=no,menubar=no,status=no,toolbar=no');
                mywin.document.write(html_errors.join("<br/>"));
                mywin.document.close();
            }
            return true;        // allow other handers to see the click
        });


        // This is a suboptimal way of re-drawing the table, what's correct?
        // BUGBUG: the refresh loses the eventsubscribers!
        var filterClick = function () {
            // Doesn't update on filter: dataTable.render();
            var dataTable = new YAHOO.widget.DataTable("resultlist", tableColumns, dataSource);
        };
        YAHOO.util.Event.addListener('filter', 'click', filterClick);
    }();
});
