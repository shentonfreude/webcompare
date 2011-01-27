/*jslint browser: true, undef: true, nomen: true,
  eqeqeq: true, plusplus: true, bitwise: true, regexp: true, strict: true,
  newcap: true, immed: true,
  indent: 4, white: true, onevar: false
*/
/*global YAHOO, window */

// I'm not proud of this: my first JavaScript, cargo-culted from the YUI site.

var data;	// I need this for Firefox4 else complains about undefined 'data' during assignment but doesn't say where.

"use strict";
YAHOO.util.Event.onDOMReady(function () {
    var WebCompare = {
        load: function (data) {
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
                if (sData === null) {
                    elCell.innerHTML = "";
                } else {
                    elCell.innerHTML = YAHOO.util.Number.format(sData * 1, {decimalPlaces: 2});
                }
            };
            var formatHtmlErrors = function (elCell, oRecord, oColumn, sData) {
                elCell.innerHTML = (sData ? sData.length : ''); // how to higlight linkability?
            };
            var getResFilter = function () {
                var resFilter = {};
                resFilter.ErrorResult     = (document.getElementById("ErrorResult").checked === true);
                resFilter.BadOriginResult = (document.getElementById("BadOriginResult").checked === true);
                resFilter.BadTargetResult = (document.getElementById("BadTargetResult").checked === true);
                resFilter.GoodResult      = (document.getElementById("GoodResult").checked === true);
                return resFilter;
            };

            var statsSource = new YAHOO.util.DataSource([data.results.stats]);
            statsSource.responseType = YAHOO.util.XHRDataSource.TYPE_JSARRAY;
            statsSource.responseSchema = {
                fields:      ["ErrorResult", "BadOriginResult", "BadTargetResult", "GoodResult"]
            };
            var statsColumns = [
                {key: "ErrorResult",         label: "Errors"},
                {key: "BadOriginResult",     label: "Bad Origin"},
                {key: "BadTargetResult",     label: "Bad Target"},
                {key: "GoodResult",          label: "Good"}
            ];

            var statsTable = new YAHOO.widget.DataTable("statsTable", statsColumns, statsSource);

            function flatten_results(input) {
                var res = [];

                for (var i = 0; i < input.resultlist.length; i += 1) {
                    var tmp = input.resultlist[i];
                    for (var k in tmp.comparisons) {
                        tmp[k] = tmp.comparisons[k];
                    }
                    res.push(tmp);
                }
                return res;
            }

            var dataSource = new YAHOO.util.FunctionDataSource(function () { return flatten_results(data.results);}, {
                doBeforeCallback : function (req, oFullResponse, res, cb) {
                    var data     = res.results || [];
                    var filtered = [];
                    var i, l;

                    var resFilter = getResFilter();
                    for (i = 0, l = data.length; i < l; i += 1) {
                        if (resFilter[data[i].result_type]) {
                            filtered.push(data[i]);
                        }
                    }
                    res.results = filtered;
                    return res;
                }
            });
            dataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
            dataSource.responseSchema = {
                fields: [
                    "result_type",
                    "origin_url",
                    "target_url",
                    {key: "origin_code",        parser: "number"},
                    {key: "target_code",        parser: "number"},
                    {key: "origin_time",        parser: "number"},
                    {key: "target_time",        parser: "number"},
                    "origin_html_errors",
                    "target_html_errors",
                    {key: "BodyComparator",     parser: "number"},
                    {key: "ContentComparator",  parser: "number"},
                    {key: "LengthComparator",   parser: "number"},
                    {key: "TitleComparator",    parser: "number"}
                ]
            };

            var tableColumns = [
                {key: "result_type",                    label: "Result<br/>Type",      sortable: true},
                {key: "origin_code",                    label: "Origin<br/>Code",      sortable: true, formatter: formatOriginCode},
                {key: "target_code",                    label: "Target<br/>Code",      sortable: true, formatter: formatTargetCode},
                {key: "origin_time",                    label: "Origin<br/>Time",      sortable: true, formatter: formatDownloadTime},
                {key: "target_time",                    label: "Target<br/>Time",      sortable: true, formatter: formatDownloadTime},
                {key: "origin_html_errors",             label: "Origin<br/>Errors",    sortable: true, formatter: formatHtmlErrors},
                {key: "target_html_errors",             label: "Target<br/>Errors",    sortable: true, formatter: formatHtmlErrors},
                {key: "BodyComparator",                 label: "Body<br/>proxim",      sortable: true},
                {key: "ContentComparator",              label: "Content<br/>proxim",   sortable: true},
                {key: "LengthComparator",               label: "Length<br/>proxim",    sortable: true},
                {key: "TitleComparator",                label: "Title<br/>proxim",     sortable: true},
                {key: "origin_url",                     label: "URL Path",             sortable: true, formatter: formatUrlPath}
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

            // Reload the table when they select new filter options and click on Filter!

            YAHOO.util.Event.addListener('filter', 'click', function () {
                dataTable.showTableMessage("Reloading ...");
                dataTable.getDataSource().sendRequest(
                    '',
                    {success: dataTable.onDataReturnInitializeTable,
                     scope: dataTable});
            });
        }
    };

    YAHOO.util.Connect.asyncRequest('GET', document.location.href.replace("html", "json"),
    {
        success: function (o) {
            // Use the JSON Utility to parse the data returned from the server
            try {
                data = YAHOO.lang.JSON.parse(o.responseText);
            }
            catch (x) {
                alert("Error loading webcompare data: " + x);
                return;
            }

            WebCompare.load(data);
        },
        failure: function (o) {
            alert("Unable to load webcompare data: " + o.status + ":" + o.statusText);
        }
    });
});
