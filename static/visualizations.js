/**
 * Visual Analysis system for the exploration of the visual quality of
 * multidimensional time series projections.
 */

/** Initialization. **/
function init() {
    minCircleWidth = 3;
    scalableCircleWidth = 12;
    smallerCircleWidth = 1;
    highlightsCircleWidth = 10;
    hoverCircleWidthFactor = 4;

    minLineWidth = 1;
    scalableLineWidth = 8;
    hoverLineFactor = 2;

    lastScaleValue = 1;

    customScale1 = d3.scaleLinear()
      .domain([-1, -0.5, 0, 0.5, 1])
      .range(["#0475b5", "#3194cc", "#e7e5e5", "#ff47a6", "#bd0061"]);

    customScale2 = d3.scaleLinear()
      .domain([-1, -0.5, 0, 0.5, 1])
      .range(["#007500", "#33d433", "#e7e5e5", "#b136ff", "#60009c"]);

    linearLineScale = customScale2
    linearSampleScale = customScale1

    // lines, time
    timeColormaps = [d3.interpolatePuRd,
                     d3.interpolateBuPu,
                     d3.interpolatePuBuGn,
                     d3.interpolateOrRd,
                     d3.interpolateBuPu,
                     d3.interpolateYlGn,
                     d3.interpolateGnBu,
                     d3.interpolateYlOrRd,
                     d3.interpolateRdPu,
                     d3.interpolateYlGnBu,
                     d3.interpolateYlGn,
                     d3.interpolateYlOrBr]

    highlightColor = "#696969";

    haloColor_small = "#000000";
    haloColor_large = "#ebb734";
    haloOpacity = 0.4;

    // temp values
    prev_interpolate = "";
    prev_subsampleCount = -1;
    currentDataset = "";

    // current settings
    document.getElementById("lineType").selectedIndex = "1";
    document.getElementById("sampleMetric").selectedIndex = "3";
    document.getElementById("lineMetric").selectedIndex = "6";

    // visualizations
    const VisType = {
        projection: "projection",
        highlighting: "highlighting",
        halo: "halo"
    }
    currentVisType = "highlighting";

    changeDatasetOptions();
}

/** Change settings for the visualization. **/
function changeDatasetOptions() {
    var parameters = {
        trialIds: document.getElementById("trialIDs").value,
        preprocessingType: document.getElementById("preprocessingType").value,
        dimRedMethod: document.getElementById("dimRedMethod").value
    };

    var request = new XMLHttpRequest();
    request.open('POST', '/updateDatasetSelection', false);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(parameters));

    var content = JSON.parse(request.responseText);
    datasets = content["datasets"];
    selection = document.getElementById("dataSets")
    selection.options.length = 0;

    for (k in datasets) {
        var option = document.createElement("option");
        option.style.fontWeight = "bold"
        option.value = k;
        option.text = datasets[k]["preprocessSettings"]["TrialID"] + " | Scaling: " +
                      datasets[k]["preprocessSettings"]["Preprocessing"];
        option.disabled = true;
        selection.appendChild(option);

        option = document.createElement("option");
        option.value = k;

        option.text = datasets[k]["settings"]["DimRed"] + " (" +
                      JSON.stringify(datasets[k]["settings"][datasets[k]["settings"]["DimRed"]]).
                        replace(new RegExp("[{}\\[\\]\\']", 'g'), "").replaceAll("\"", "").replaceAll(",", ", ").
                        replaceAll(":", ": ")  + ")"
        option.disabled = true;
        selection.appendChild(option);

        option = document.createElement("option");
        option.value = k;
        option.text = "Subsampling: " + datasets[k]["settings"]["UseSubsampling"] +
                      " | Subsamples embedded: " + datasets[k]["settings"]["UseSubsamplesForEmbedding"] +
                      " | Line Type: " + datasets[k]["settings"]["SubsamplingType"] +
                      " | #Subsamples: " + (datasets[k]["settings"]["SubsamplingCountFixed"] == "True" ?
                       datasets[k]["settings"]["SubsamplingCount"] : "Varying");
        option.disabled = true;
        selection.appendChild(option);

        option = document.createElement("option");
        option.style.fontWeight = "bold"
        option.value = k;
        option.text = (k != "0" ? k + ": " : "") + datasets[k]["name"];
        selection.appendChild(option);

        option = document.createElement("option");
        option.disabled = true;
        option.text = "";
        selection.appendChild(option);
    }
}

/** General UI. **/
function recalculate() {

    if (currentDataset != document.getElementById("dataSets").value) {
        prev_interpolate = "";
        prev_subsampleCount = -1;
    }

    var parameters = {
        dataSets: document.getElementById("dataSets").value,
    };
    currentDataset = document.getElementById("dataSets").value

    var request = new XMLHttpRequest();
    request.open('POST', '/data', false);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(parameters));

    var content = JSON.parse(request.responseText);
    currentDatasetName = content["name"].split('.').slice(0, -1).join('.');
    valuesList = content["samples"];
    settings = content["settings"];
    preprocessingSettings = content["preprocessingSettings"];

    sampleScale = document.getElementById("sampleSlider").value / 10;
    lineScale = document.getElementById("lineSlider").value / 10;
    haloScale = document.getElementById("haloSlider").value / 10;

    updateView();
    updatePlots();
    updateInfo();
}

/** Dataset info. **/
function updateInfo() {
    var settingsText = "";
    //settingsText += "<br><b>Current Dataset: " + currentDatasetName + "</b>"

    dimRed = settings["DimRed"]
    dimRedPreprocessing = preprocessingSettings["DimRed"]
    let order = [
                 //"TrialID",
                 "#Timelines",
                 "#MainSamples",
                 "#Samples",
                 "OrigDims",
                 "Dims",
                 "Preprocessing",
                 "EveryXSample",
                 "IgnoreFirstDimension",
                 "DimRed",
                 "dimRedMethod",
                 "dimRedPreprocessing",
                 "UseSubsampling",
                 "SubsamplingCount",
                 "SubsamplingType",
                 "UseSubsamplesForEmbedding"]
    for (key of order) {
        if (key == "dimRedMethod") {
            for (const [k, v] of Object.entries(settings[dimRed])) {
                settingsText += "<br><b>" + k + "</b>: " + v;
            }
        }
        else if (settings[key] || key == "#Timelines" || key == "#Samples" || key == "#MainSamples") {
            if (settings["UseSubsampling"] != "True" && (key == "SubsamplingCount" ||
                key == "SubsamplingType" || key == "UseSubsamplesForEmbedding" || key == "UseSubsampling")) {
                continue;
            }
            else if (key == "IgnoreFirstDimension" && settings[key] != "True") {
                continue;
            }
            else if (key == "EveryXSample" && settings[key] == 1) {
                continue;
            }
            else if (key == "#Timelines") {
                v = valuesList.length;
                if (v <= 1) {
                    continue;
                }
            }
            else if (key == "#Samples") {
                var count = 0;

                for (var i = 0; i < valuesList.length; i++) {
                    for (var e = 0; e < valuesList[i].length; e++) {
                        count++;
                    }
                }
                v = count
            }
            else if (key == "#MainSamples") {
                var count = 0;
                for (var i = 0; i < valuesList.length; i++) {
                    for (var e = 0; e < valuesList[i].length; e++) {
                        if (valuesList[i][e][2]) {
                            count++;
                        }
                    }
                }
                v = count
            }
            else if (key == "SubsamplingCount") {
                v = settings["SubsamplingCountFixed"] == "True" ? settings[key] : "Varying";
            }
            else {
                v = settings[key];
            }

            highlight = key == "Projection" || key == "SubsamplingType" ||
                        key == "UseSubsamplesForEmbedding" || key == "SubsamplingCount";
            settingsText += "<br><b>" + key + "</b>: ";
            settingsText += highlight ? '<b><font color="#bc0d52">' : "";
            settingsText += v;
            settingsText += highlight ? "</font></b>" : "";
        }
    }

    var preprocessingSettingsText = ""
    for (key of order) {
        if (key == "dimRedPreprocessing") {
            for (const [k, v] of Object.entries(preprocessingSettings[dimRedPreprocessing])) {
                preprocessingSettingsText += "<br><b>" + k + "</b>: " + v;
            }
        }
        else if (preprocessingSettings[key]) {
            if (key == "IgnoreFirstDimension" && preprocessingSettings[key] != "True"){
                continue;
            }
            if (key == "EveryXSample" && preprocessingSettings[key] == 1){
                continue;
            }

            preprocessingSettingsText += "<br><b>" + key + "</b>: " + preprocessingSettings[key];
        }
    }

    document.getElementById("settingsText").innerHTML = settingsText;
    document.getElementById("preprocessingSettingsText").innerHTML = preprocessingSettingsText;

    tempText = parseFloat(metrics["trustworthiness"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["trustworthiness"]).toFixed(2);
    tempText += parseFloat(metrics["trustworthiness"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("trustworthiness").innerHTML = tempText;

    tempText = parseFloat(metrics["continuity"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["continuity"]).toFixed(2);
    tempText += parseFloat(metrics["continuity"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("continuity").innerHTML = tempText;

    tempText = parseFloat(metrics["normalizedStress"]) > 0.1 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["normalizedStress"]).toFixed(2);
    tempText += parseFloat(metrics["normalizedStress"]) > 0.1 ? "</font></b>" : "";
    document.getElementById("normalizedStress").innerHTML = tempText;

    tempText = parseFloat(metrics["pearson"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["pearson"]).toFixed(2);
    tempText += parseFloat(metrics["pearson"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("pearson").innerHTML = tempText;

    tempText = parseFloat(metrics["spearman"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["spearman"]).toFixed(2);
    tempText += parseFloat(metrics["spearman"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("spearman").innerHTML = tempText;

    tempText = parseFloat(metrics["kendall"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["kendall"]).toFixed(2);
    tempText += parseFloat(metrics["kendall"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("kendall").innerHTML = tempText;

    tempText = parseFloat(metrics["normalizedStress_time"]) > 0.1 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["normalizedStress_time"]).toFixed(2);
    tempText += parseFloat(metrics["normalizedStress_time"]) > 0.1 ? "</font></b>" : "";
    document.getElementById("normalizedStress_time").innerHTML = tempText;

    tempText = parseFloat(metrics["pearson_time"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["pearson_time"]).toFixed(2);
    tempText += parseFloat(metrics["pearson_time"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("pearson_time").innerHTML = tempText;

    tempText = parseFloat(metrics["spearman_time"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["spearman_time"]).toFixed(2);
    tempText += parseFloat(metrics["spearman_time"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("spearman_time").innerHTML = tempText;

    tempText = parseFloat(metrics["kendall_time"]) < 0.9 ? '<b><font color="#bc0d52">' : "";
    tempText += parseFloat(metrics["kendall_time"]).toFixed(2);
    tempText += parseFloat(metrics["kendall_time"]) < 0.9 ? "</font></b>" : "";
    document.getElementById("kendall_time").innerHTML = tempText;

}

/** Main visualization with projection. **/
function updateView() {
    interpolate = document.getElementById("lineType").value;
    subsampleCount = parseInt(document.getElementById("subsamples").value)
    if (prev_interpolate != interpolate | prev_subsampleCount != subsampleCount) {
        var parameters = {
            interpolationType: interpolate,
            subsampleCount: subsampleCount,
        };

        var request = new XMLHttpRequest();
        request.open('POST', '/lines', false);
        request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify(parameters));

        var content = JSON.parse(request.responseText);
        interpolatedList = content["interpolated"]

        var parameters = {};
        var request = new XMLHttpRequest();
        request.open('POST', '/intersections', false);
        request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify(parameters));

        var content = JSON.parse(request.responseText);
        haloList = content["halos"];

        prev_interpolate = interpolate
        prev_subsampleCount = subsampleCount
    }

    disableScalingSamples(document.getElementById("sampleMetric").value.includes("time") ||
        document.getElementById("sampleMetric").value.includes("equal"))
    disableScalingLines(document.getElementById("lineMetric").value.includes("time") ||
        document.getElementById("lineMetric").value.includes("equal"))

    var parameters = {
        sampleMetricId: document.getElementById("sampleMetric").value,
        lineMetricId:  document.getElementById("lineMetric").value,
        slidingWindowSize: parseInt(document.getElementById("slidingWindowSize").value),
        localNeighborhoodSize: parseInt(document.getElementById("localNeighborhoodSize").value),
        maxNumberOfNeighbors: parseInt(document.getElementById("maxNumberOfNeighbors").value),
        maxScaling_samples: document.getElementById("maxScaling_samples").checked,
        minMaxScaling_samples: document.getElementById("minmaxScaling_samples").checked,
        posNegScaling_samples: document.getElementById("posNegScaling_samples").checked,
        standardization_samples: document.getElementById("standardization_samples").checked,
        maxScaling_connections: document.getElementById("maxScaling_connections").checked,
        minMaxScaling_connections: document.getElementById("minmaxScaling_connections").checked,
        posNegScaling_connections: document.getElementById("posNegScaling_connections").checked,
        standardization_connections: document.getElementById("standardization_connections").checked,
    };
    request = new XMLHttpRequest();
    request.open('POST', '/newMetrics', false);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(parameters));

    content = JSON.parse(request.responseText);
    sampleColorMetric = content["sampleColorMetric"]
    sampleWidthMetric = content["sampleWidthMetric"]
    lineColorMetric = content["lineColorMetric"]
    lineThicknessMetric = content["lineThicknessMetric"]
    distances2D = content["distances2D"]
    distances50D = content["distances50D"]
    haloMetric = content["haloMetric"]
    maxDistance50D = content["maxDistance50D"]
    meanDistance50D = content["meanDistance50D"]
    meanDistance2D = content["meanDistance2D"]
    stdDistance50D = content["stdDistance50D"]
    stdDistance2D = content["stdDistance2D"]
    meanSampleColorMetric = content["meanSampleColorMetric"]
    meanSampleWidthMetric = content["meanSampleWidthMetric"]
    meanLineColorMetric = content["meanLineColorMetric"]
    meanLineThicknessMetric = content["meanLineThicknessMetric"]

    // overall metrics
    var parameters = {
        localNeighborhoodSize: parseInt(document.getElementById("localNeighborhoodSize").value)
    };
    request = new XMLHttpRequest();
    request.open('POST', '/overallMetrics', false);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(parameters));

    content = JSON.parse(request.responseText);
    metrics = content["metrics"]

    // time series filter
    timeSeries = document.getElementById("timeSeriesFilter").value
    timeSeriesList = []

    if (timeSeries.length > 0) {
        timeSeries = timeSeries.replace(";", ",").split(',');
        for (w of timeSeries) {
            parts = w.split('-');
            if (parts.length > 1 && parts.length == 2) {
                start = parseInt(parts[0]);
                end = parseInt(parts[1]);
                if (end < start) {
                    temp = start;
                    start = end;
                    end = temp;
                }
                for (var i = start; i <= end; i++) {
                    timeSeriesList.push(i);
                }
            }
            else if (parts.length == 1) {
                timeSeriesList.push(parseInt(w));
            }
        }
    }

    d3.select("#mainSvg").selectAll("polyline").remove();
    d3.select("#mainSvg").selectAll("line").remove();
    d3.select("#mainSvg").selectAll("rect").remove();
    d3.select("#mainSvg").selectAll("circle").remove();
    d3.select("#mainSvg").selectAll("text").remove();

    var svg = d3.select("#mainSvg");
    svg.selectAll("*").remove();

    var zoom = d3.zoom().wheelDelta(myDelta).on("zoom", function () {
        zoomBehavior();
    });

    svg = svg.call(zoom)
        .append("g")
        .attr("id", "svgGroup");

    // scale
    scales = getMainScales();
    xScale = scales[0];
    yScale = scales[1];

    // connections
    sampleConnectionsAsStringsLists = [];
    sampleConnectionsLists = [];
    for (var i = 0; i < interpolatedList.length; ++i) {
        sampleConnectionsAsStringsList = [];
        sampleConnectionsList = [];
        for (var j = 0; j < interpolatedList[i].length; ++j) {
            sampleConnections = [];

            for (var k = 0; k < interpolatedList[i][j].length; ++k) {
                sampleConnections.push(xScale(interpolatedList[i][j][k][0]));
                sampleConnections.push(yScale(interpolatedList[i][j][k][1]));
            }

            if (j < interpolatedList[i].length - 1) {
                sampleConnections.push(xScale(interpolatedList[i][j + 1][0][0]));
                sampleConnections.push(yScale(interpolatedList[i][j + 1][0][1]));
            }

            sampleConnectionsAsStringsList.push(sampleConnections.join(","));

            sampleConnectionsTempList = []
            for (var l = 0; l < sampleConnections.length; l += 2) {
                sampleConnectionsTempList.push([sampleConnections[l], sampleConnections[l + 1]])
            }
            sampleConnectionsList.push(sampleConnectionsTempList)
        }
        sampleConnectionsLists.push(sampleConnectionsList)
        sampleConnectionsAsStringsLists.push(sampleConnectionsAsStringsList)
    }

    polylineValues = []
    c = 0
    if (sampleConnectionsLists.length > 0) {
        for (var i = 0; i < lineColorMetric.length; ++i) {
            if (timeSeriesList.length > 0 && !timeSeriesList.includes(i)) {
                continue;
            }
            for (var j = 0; j < lineColorMetric[i].length; ++j) {

                colorString = getLineColor(lineColorMetric[i][j], i)

                v = {}

                v["connection"] = sampleConnectionsAsStringsLists[i][j]
                v["connectionList"] = sampleConnectionsLists[i][j]
                v["metricColor"] = colorString;
                v["colorMetric"] = lineColorMetric[i][j];
                v["thicknessMetric"] = lineThicknessMetric[i][j];

                v["startSample"] = valuesList[i][j][3];
                v["endSample"] = valuesList[i][j + 1][3];

                v["timeSeries"] = i
                v["startSample_id"] = j

                v["distance2D"] = distances2D[c]
                v["distance50D"] = distances50D[c]

                polylineValues.push(v);
                c++;
            }
        }
    }

    if (document.getElementById("showLines").checked == true) {
        var polyline = svg.selectAll("polyline").data(polylineValues);
        var polylineEnter = polyline.enter().append("polyline");

        polylineEnter.attr("points", function(d, i) { return d["connection"]; });
        polylineEnter.style("stroke", function(d, i) { return d["metricColor"]; });
        polylineEnter.style("fill", "none");
        polylineEnter.attr("class", function(d,i) { return "l" + i; });

        var mouseFunctions = tooltipFunctionsForLines()
        polylineEnter.on("mouseover", mouseFunctions[0]);
        polylineEnter.on("mousemove", mouseFunctions[1]);
        polylineEnter.on("mouseleave", mouseFunctions[2]);
    }

    // circles
    circleValues = []
    count = 0
    var mainCircleGroup = svg.append("g").attr("id", "mainCircleGroup");
    for (var i = 0; i < sampleColorMetric.length; i++) {
        if (timeSeriesList.length > 0 && !timeSeriesList.includes(i)) {
            continue;
        }
        for (var j = 0; j < sampleColorMetric[i].length; j++) {
            if (currentVisType != "highlighting") {
                colorString = getSampleColor(j / sampleColorMetric[i].length, i);
            }
            else {
                colorString = getSampleColor(sampleColorMetric[i][j], i);
            }

            v = {}
            v["x"] = xScale(valuesList[i][j][0])
            v["y"] = yScale(valuesList[i][j][1])
            v["mainSample"] = valuesList[i][j][2]
            v["label"] = valuesList[i][j][3]
            v["metricColor"] = colorString;
            v["colorMetric"] = sampleColorMetric[i][j];
            v["sizeMetric"] = sampleWidthMetric[i][j];

            v["timeSeries"] = i
            v["sample_id"] = j
            circleValues.push(v);
         }
    }

    if (document.getElementById("showSamples").checked == true) {

        var circle = mainCircleGroup.selectAll("circle").data(circleValues);
        var circleEnter = circle.enter().append("circle");

        circleEnter.attr("cx", function(d, i) { return d["x"]; });
        circleEnter.attr("cy", function(d, i) { return d["y"]; });
        circleEnter.style("fill", function(d, i) { return d["metricColor"]; });
        circleEnter.attr("class", function(d,i) { return "s" + i; });

        var mouseFunctions = tooltipFunctionsForSamples();
        circleEnter.on("mouseover", mouseFunctions[0]);
        circleEnter.on("mousemove", mouseFunctions[1]);
        circleEnter.on("mouseleave", mouseFunctions[2]);
    }

    // highlight first/last sample
    var startAndEndCirclesGroup = svg.append("g").attr("id", "startAndEndCirclesGroup");

    startEndValues = []
    for (var i = 0; i < valuesList.length; i++) {
        if (timeSeriesList.length > 0 && !timeSeriesList.includes(i)) {
            continue;
        }

        firstEl = Array.from(valuesList[i][0])
        colorStringFirst = "rgb(200,200,200)";
        lastEl = Array.from(valuesList[i][valuesList[i].length - 1])
        colorStringLast = "rgb(0,0,0)";

        v = {}
        v["x"] = xScale(firstEl[0])
        v["y"] = yScale(firstEl[1])
        v["mainSample"] = firstEl[2]
        v["label"] = firstEl[3]
        v["color"] = colorStringFirst;
        startEndValues.push(v);

        v = {}
        v["x"] = xScale(lastEl[0])
        v["y"] = yScale(lastEl[1])
        v["mainSample"] = lastEl[2]
        v["label"] = lastEl[3]
        v["color"] = colorStringLast;
        startEndValues.push(v);
    }

    var circle = startAndEndCirclesGroup.selectAll("circle").data(startEndValues);
    var circleEnter = circle.enter().append("circle");

    circleEnter.attr("cx", function(d, i) { return d["x"]; });
    circleEnter.attr("cy", function(d, i) { return d["y"]; });
    circleEnter.style("stroke", function(d, i) { return d["color"]; });
    circleEnter.style("fill", "none");

    // halos
    minHaloMetric = Math.min.apply(null, haloMetric);
    minHaloMetric = 0;
    maxHaloMetric = Math.max.apply(null, haloMetric);
    var haloCircleGroup = svg.append("g").attr("id", "haloCircleGroup");
    haloValues = []

    for (var i = 0; i < haloList.length; i++) {
        v = {}
        v["x"] = xScale(haloList[i]["x"])
        v["y"] = yScale(haloList[i]["y"])
        val = haloMetric[i];

        threshold = meanDistance50D
        // scale depending on max distance between neighboring samples
        v["size"] = val > threshold ? haloMetric[i] / maxHaloMetric * 35 : haloMetric[i] / maxHaloMetric * 20
        v["metricColor"] = val > threshold ? haloColor_large : haloColor_small
        v["opacity"] = haloOpacity
        v["distance"] = haloMetric[i] // scale depending on max distance between neighboring samples
        v["maxDistance50D"] = maxDistance50D // scale depending on max distance between neighboring samples
        v["meanDistance50D"] = meanDistance50D

        v["ts1"] = haloList[i]["ts1"]
        v["ts2"] = haloList[i]["ts2"]
        v["seg1"] = haloList[i]["seg1"]
        v["seg2"] = haloList[i]["seg2"]
        v["p1"] = haloList[i]["p1"]
        v["p2"] = haloList[i]["p2"]

        haloValues.push(v);
    }

    if (document.getElementById("showHalos").checked == true) {

        var circle = haloCircleGroup.selectAll("circle").data(haloValues);
        var circleEnter = circle.enter().append("circle");

        circleEnter.attr("cx", function(d, i) { return d["x"]; });
        circleEnter.attr("cy", function(d, i) { return d["y"]; });
        circleEnter.attr("class", function(d,i) { return "h" + i; });

        circleEnter.style("fill", function(d, i) { return d["metricColor"] });
        circleEnter.style("fill-opacity", function(d, i) { return d["opacity"] });
        circleEnter.style("stroke", function(d, i) { return d["metricColor"] });
        circleEnter.style("stroke-opacity", 0.5);

        var mouseFunctions = tooltipFunctionsForHalos()
        circleEnter.on("mouseover", mouseFunctions[0]);
        circleEnter.on("mousemove", mouseFunctions[1]);
        circleEnter.on("mouseleave", mouseFunctions[2]);
    }

    // labels
    if (document.getElementById("showLabels").checked == true) {

        var texts = svg.selectAll("text").data(circleValues);
        var textsEnter = texts.enter().append("text")
        .text(function(d, i) { return d["label"]; })
        .style("text-anchor", "middle")
        .style("alignment-baseline", "central")
        .style("color", "#f8f8f8")
        .style("opacity", function(d, i) { return d["mainSample"] ? 0.7 : 0})
        .style("pointer-events", "none")
        .classed("idText", true);
    }

    // buttons
    d3.select("#resetButton").on('click', resetted);

    // legends
    d3.select("#legend").selectAll("rect").remove();

    // legend samples
    samplesColorMapSvg = d3.select("#samplesColorMapSvg");
    dataValues = []
    for (var i = -100; i <= 100; i++) {
        dataValues.push(getSampleColor(i / 100))
    }
    samplesColorMapSvg.attr("width", 201);
    var legend = samplesColorMapSvg.selectAll("rect").data(dataValues);
    var rectEnter = legend.enter().append("rect");
    rectEnter.attr("y", function(d, i) { return 0; })
             .attr("x", function(d, i) { return i; })
             .attr("width", function(d, i) { return 1; })
             .attr("height", function(d, i) { return 19 })
             .style("fill", function(d, i) { return d; })
             .style("shape-rendering", "crispEdges");

    // legend lines
    linesColorMapSvg = d3.select("#linesColorMapSvg");
    dataValues = []
    for (var i = -100; i < 100; i++) {
        dataValues.push(getLineColor(i / 100))
    }
    linesColorMapSvg.attr("width", 201);
    var legend = linesColorMapSvg.selectAll("rect").data(dataValues);
    var rectEnter = legend.enter().append("rect");
    rectEnter.attr("y", function(d, i) { return 0; })
             .attr("x", function(d, i) { return i; })
             .attr("width", function(d, i) { return 1; })
             .attr("height", function(d, i) { return 19 })
             .style("fill", function(d, i) { return d; })
             .style("shape-rendering", "crispEdges");

    resetted(); // scale elements correctly

    if (currentVisType != "highlighting") {
        d3.select("#mainSvg").selectAll("polyline").remove();
        d3.select("#mainSvg").selectAll("line").remove();
        d3.select("#mainSvg").selectAll("rect").remove();
        d3.select("#mainSvg").selectAll("circle").remove();
        d3.select("#mainSvg").selectAll("text").remove();
        currentTs = 0
        halosDrawn = []

        var radialGradient = haloCircleGroup.append("defs")
          .append("radialGradient")
          .attr("id", "radial-gradient-white")
          .attr("gradientUnits", "objectBoundingBox")
          .attr("cx", "50%")
          .attr("cy", "50%")
          .attr("r", "50%")
          .attr("spreadMethod", "pad");

        radialGradient.append("stop")
          .attr("offset", "30%")
          .attr("stop-opacity", "0.90")
          .attr("stop-color", "white");

        radialGradient.append("stop")
          .attr("offset", "100%")
          .attr("stop-opacity", "0")
          .attr("stop-color", "white");

        for (var i = 0; i < circleValues.length; i++) {

            ts = circleValues[i]["timeSeries"]
            id = circleValues[i]["sample_id"]

            if (document.getElementById("showHalos").checked == true) {

                halos = haloValues.filter(y => y.ts2 == ts && y.seg2 == id)

                // halos
                for (var e of halos) {
                    index = haloValues.indexOf(e)

                    var newHaloCircleGroup = svg.append("g").attr("id", "haloCircleGroup" + index);
                    var circle = newHaloCircleGroup.selectAll("ellipse").data([haloValues[index]]);
                    var circleEnter = circle.enter().append("ellipse");

                    circleEnter.attr("cx", function(d, i) { return d["x"]; });
                    circleEnter.attr("cy", function(d, i) { return d["y"]; });
                    circleEnter.style("fill", "url(#radial-gradient-white)");

                    circleEnter.attr("transform", function(d, i) { return "rotate(" + " " + d["x"] + " " + d["y"] + ")" });

                    halosDrawn.push(index);
                }
           }

            polylineIndex = polylineValues.findIndex(y => y.startSample_id == id && y.timeSeries == ts)

            if (document.getElementById("showLines").checked == true) {
                // polylines
                if (polylineIndex != -1 && polylineIndex < polylineValues.length) {
                    var newPolylineGroup = svg.append("g").attr("id", "polylineGroup" + polylineIndex);
                    var polyline = newPolylineGroup.selectAll("polyline").data([polylineValues[polylineIndex]]);
                    var polylineEnter = polyline.enter().append("polyline");
                    polylineEnter.attr("points", function(d, i) { return d["connection"]; });
                    //polylineEnter.style("stroke", function(d, i) { return d["metricColor"]; });
                    polylineEnter.style("stroke", "gray");
                    polylineEnter.style("fill", "none");
                }
            }

            if (document.getElementById("showSamples").checked == true) {
                // circle in new group
                var newCircleGroup = svg.append("g").attr("id", "mainCircleGroup" + i);
                var circle = newCircleGroup.selectAll("circle").data([circleValues[i]]);
                var circleEnter = circle.enter().append("circle");
                circleEnter.attr("cx", function(d, i) { return d["x"]; });
                circleEnter.attr("cy", function(d, i) { return d["y"]; });
                circleEnter.style("fill", function(d, i) { return d["metricColor"]; });

                var mouseFunctions = tooltipFunctionsForSamples();
                circleEnter.on("mouseover", mouseFunctions[0]);
                circleEnter.on("mousemove", mouseFunctions[1]);
                circleEnter.on("mouseleave", mouseFunctions[2]);
            }
        }

        var circle = startAndEndCirclesGroup.selectAll("circle").data(startEndValues);
        var circleEnter = circle.enter().append("circle");

        circleEnter.attr("cx", function(d, i) { return d["x"]; });
        circleEnter.attr("cy", function(d, i) { return d["y"]; });
        circleEnter.style("stroke", function(d, i) { return d["color"]; });
        circleEnter.style("fill", "none");

        // labels
        if (document.getElementById("showLabels").checked == true) {
            var texts = svg.selectAll("text").data(circleValues);
            var textsEnter = texts.enter().append("text")
            .text(function(d, i) { return d["label"]; })
            .style("text-anchor", "middle")
            .style("alignment-baseline", "central")
            .style("color", "#f8f8f8")
            .style("opacity", function(d, i) { return d["mainSample"] ? 0.7 : 0})
            .style("pointer-events", "none")
            .classed("idText", true);
        }

        scaleValues();
    }
}

/** Plots (bar charts and scatterplot). **/
function updatePlots() {
   // bar charts for metrics
    updateBarChart("barChart4", circleValues, "colorMetric", "Samples", "samples", [meanSampleWidthMetric])
    updateBarChart("barChart1", polylineValues, "colorMetric", "Connections", "lines", [meanLineThicknessMetric])

    updateBarChart("barChart2", polylineValues, "distance50D", "Orig. Distance (Conn.)", "lines", [meanDistance50D])
    updateBarChart("barChart3", polylineValues, "distance2D", "2D Distance (Conn.)", "lines", [meanDistance2D])
    updateBarChart("barChart5", haloValues, "distance", "Intersections - Orig. Dist.", "halos", [meanDistance50D, maxDistance50D])

    // scatterplot for distances
    labelList = []
    for (var i = 0; i < valuesList.length; i++) {
        for (var j = 0; j < valuesList[i].length; j++) {
            labelList.push(valuesList[i][j][3])
         }
    }

    updateScatterPlot("scatterPlot1", circleValues, polylineValues, "Shepard Diagram", "2D Distance", "Original Distance", true)

    // Redraw when window size changes
    window.addEventListener("resize", updatePlots);
}

/** Create the scatterplot. **/
function updateScatterPlot(id, circleValues, polylineValues, title, xAxis, yAxis, diagonal=false) {

    scatterPlotSvg = d3.select("#" + id)
    scatterPlotElement = document.getElementById(id)

    scatterPlotSvg.selectAll("*").remove();

    var margin = {top: 15, right: 10, bottom: 38, left: 40};

    var scatterPlotSvgWidth = scatterPlotElement.getBoundingClientRect().width - margin.right - margin.left;
    var scatterPlotSvgHeight = scatterPlotElement.getBoundingClientRect().height - margin.bottom - margin.top;

    scatterPlotSvg.append("text")
        .attr("transform", "translate(" + margin.left + "," + (margin.top) + ")")
        .attr("font-size", "17px")
        .text("Shepard Diagram")

    var xScale = d3.scaleLinear().range([0, scatterPlotSvgWidth]);
    var yScale = d3.scaleLinear().range([scatterPlotSvgHeight, 0]);

    xScale.domain([0, d3.max(polylineValues, function (d) { return d["distance2D"]; })]);
    yScale.domain([0, d3.max(polylineValues, function (d) { return d["distance50D"]; })]);

    var valueline = d3.line()
     .x(function (d) { return xScale(d["2D"]); })
     .y(function (d) { return yScale(d["50D"]); });

    var scatterPlotSvg = scatterPlotSvg
     .append("g")
     .attr("transform", "translate(" + margin.left + "," + (margin.top + 5) + ")");

    if (diagonal) {
        maxX = meanDistance2D + stdDistance2D
        maxY = meanDistance50D + stdDistance50D
        if (maxX > maxY) {
            diff = d3.max(xScale.domain()) - maxX
            maxX = d3.max(xScale.domain())
            maxY = maxY + maxY * diff
        }
        else {
            diff = d3.max(yScale.domain()) - maxY
            maxY = d3.max(yScale.domain())
            maxX = maxX + maxX * diff
        }

        scatterPlotSvg.append('line')
         .style("stroke", highlightColor)
         .style("stroke-width", 1)
         .attr("x1", xScale(d3.min(xScale.domain())))
         .attr("y1", yScale(d3.min(yScale.domain())))
         .attr("x2", xScale(maxX))
         .attr("y2", yScale(maxY))
         .attr("class", "markerLine");
    }

    data = polylineValues.slice(0,-1);

    var lineEnter =
        scatterPlotSvg.append("g").selectAll("line")
       .data(data)
       .enter().append("line")

    lineEnter.attr("fill", "black")
      .attr("stroke", function(d,i) { return circleValues[i]["metricColor"] })
      .attr("stroke-width", 2)
      .attr("x1", function(d,i) { return xScale(polylineValues[i]["distance2D"]); })
      .attr("x2", function(d,i) { return xScale(polylineValues[i + 1]["distance2D"]); })
      .attr("y1", function(d,i) { return yScale(polylineValues[i]["distance50D"]); })
      .attr("y2", function(d,i) { return yScale(polylineValues[i + 1]["distance50D"]); });

    var scatterEnter = scatterPlotSvg.selectAll("dot")
         .data(polylineValues)
         .enter().append("circle")

    scatterEnter.attr("r", 4)
         .attr("cx", function (d, i) { return xScale(d["distance2D"]); })
         .attr("cy", function (d) { return yScale(d["distance50D"]); })
         .attr("fill", function (d) { return d["metricColor"]; });
    scatterEnter.attr("class", function(d,i) { return "s-s" + i; });

    scatterPlotSvg.append("g")
     .attr("transform", "translate(0," + scatterPlotSvgHeight + ")")
     .call(d3.axisBottom(xScale).tickFormat(function(d, i){ return d3.format(".1f")(d); })
     .ticks(5))
     .append("text")
     .attr("y", 30)
     .attr("x", 70)
     .attr("text-anchor", "end")
     .attr("stroke", "black")
     .text(xAxis)
     .style("fill", "black")
     .attr("font-size", "14px")
     .style("stroke", "none")

    scatterPlotSvg.append("g")
     .call(d3.axisLeft(yScale).tickFormat(function(d, i){ return d3.format(".1f")(d); })
     .ticks(5))
     .append("text")
     .attr("transform", "rotate(-90)")
     .attr("x", - scatterPlotSvgHeight + 105)
     .attr("y", -25)
     .attr("text-anchor", "end")
     .attr("stroke", "black")
     .text(yAxis)
     .style("fill", "black")
     .attr("font-size", "14px")
     .style("stroke", "none");

    var mouseFunctions = tooltipFunctionsForLines(true);
    scatterEnter.on("mouseover", mouseFunctions[0]);
    scatterEnter.on("mousemove", mouseFunctions[1]);
    scatterEnter.on("mouseleave", mouseFunctions[2]);
}

/** Color transformation. **/
function rgba2rgb(color, alpha) {
  background = [255, 255, 255]
  result = [Math.floor((1 - alpha) * background[0] + alpha * color[0] + 0.5),
            Math.floor((1 - alpha) * background[1] + alpha * color[1] + 0.5),
            Math.floor((1 - alpha) * background[2] + alpha * color[2] + 0.5)]
  return "rgb(" + result[0] + ", " + result[1] + ", " +  result[2] + ")"
}

/** Create the bar chart. **/
// https://www.tutorialsteacher.com/d3js/create-bar-chart-using-d3js
function updateBarChart(id, metricValues, metricType, title, type, lineValues=[]) {

    barChartSvg = d3.select("#" + id)
    barChartElement = document.getElementById(id)

    barChartSvg.selectAll("*").remove();

    yAxis = "Metric Value"
    xAxis = "Time"

    var margin = {top: 20, right: 10, bottom: 15, left: 40};
    var barChartSvgWidth = barChartElement.getBoundingClientRect().width - margin.left - margin.right;
    var barChartSvgHeight = barChartElement.getBoundingClientRect().height - margin.top - margin.bottom;

    barChartSvg.append("text")
        .attr("transform", "translate(" + margin.left + "," + (margin.top - 5) + ")")
        .attr("font-size", "17px")
        .text(title)

    var xScale = d3.scaleBand().range([0, barChartSvgWidth])//.padding(0.4),
        yScale = d3.scaleLinear().range([barChartSvgHeight, 0]);

    var g = barChartSvg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    xScale.domain(metricValues.map(function(d, i) { return i; }));
    yScale.domain([Math.min(0, d3.min(metricValues, function(d, i) {
        return d[metricType]; })), d3.max(metricValues, function(d, i) { return d[metricType]; })]);

    rectEnter = g.selectAll(".bar")
     .data(metricValues)
     .enter().append("rect")
    rectEnter.style("fill", function(d, i) { return d["metricColor"] } )
             .attr("class", "bar")
             .attr("x", function(d, i) { return xScale(i); })
             .attr("y", function(d, i) { return yScale(Math.max(0, d[metricType])); })
             .attr("width", Math.max(1, xScale.bandwidth()))
             .attr("height", function(d, i) { return Math.abs(yScale(d[metricType]) - yScale(0)); })
             .attr("class", function(d,i) { return (type == "samples" ? "s" : type == "lines" ? "l" : "h") + i; })
             .style("shape-rendering", "crispEdges");

    if (type == "halos") {
        rectEnter.style("fill", function(d, i) { return rgba2rgb([d3.rgb(d["metricColor"]).r, d3.rgb(d["metricColor"]).g,
        d3.rgb(d["metricColor"]).b], d["opacity"]) } )
    }

    if (type == "samples") {
        var mouseFunctions = tooltipFunctionsForSamples();
    }
    else if (type == "lines") {
        var mouseFunctions = tooltipFunctionsForLines();
    }
    else {
        var mouseFunctions = tooltipFunctionsForHalos();
    }

    // first line
    if (lineValues.length >= 1) {
        g.append('line')
         .style("stroke", highlightColor)
         .style("stroke-width", 1)
         .attr("x1", 0)
         .attr("y1", yScale(lineValues[0]))
         .attr("x2", xScale(d3.max(xScale.domain())) + xScale(1))
         .attr("y2", yScale(lineValues[0]))
         .style("stroke-dasharray", ("3, 3"))
         .attr("class", "markerLine");
    }

    // second line
    if (lineValues.length >= 2) {
        g.append('line')
         .style("stroke", highlightColor)
         .style("stroke-width", 1)
         .attr("x1", 0)
         .attr("y1", yScale(lineValues[1]))
         .attr("x2", xScale(d3.max(xScale.domain())) + xScale(1))
         .attr("y2", yScale(lineValues[1]))
         .attr("class", "markerLine");
    }

    g.append("g")
     .attr("transform", "translate(0," + barChartSvgHeight + ")")
     .call(d3.axisBottom(xScale).tickValues([]))

    g.append("g")
     .call(d3.axisLeft(yScale).tickFormat(function(d, i){ return d; })
     .ticks(5))
     .append("text")
     .attr("transform", "rotate(-90)")
     .attr("x", - barChartSvgHeight + 60)
     .attr("y", -30)
     .attr("text-anchor", "end")
     .attr("stroke", "black");

    rectEnter.on("mouseover", mouseFunctions[0]);
    rectEnter.on("mousemove", mouseFunctions[1]);
    rectEnter.on("mouseleave", mouseFunctions[2]);
}

/** Tooltips for samples. **/
function tooltipFunctionsForSamples() {

    // Tooltip circles and lines
    var Tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")

    var mouseoverCircle = function(d, i) {
        Tooltip
            .style("opacity", 0.9);

        d3.selectAll("circle.s" + d["sample_id"])
          .style("stroke", highlightColor)
          .style("opacity", 1)
          .attr("r", ((d["mainSample"] == true ? scalableCircleWidth * Math.abs(d["sizeMetric"]) + minCircleWidth :
              smallerCircleWidth) + hoverCircleWidthFactor) / lastScaleValue * sampleScale)

        d3.selectAll("rect.s" + d["sample_id"])
          .style("stroke", highlightColor)
          .style("stroke-width", 3)
          .style("fill", highlightColor)

        // lines before and after
        if (document.getElementById("showLines").checked == true) {
            for (var x = -1; x < 1; x++) {
                ts = d["timeSeries"]
                id = d["sample_id"]
                index = polylineValues.findIndex(y => y.startSample_id == id && y.timeSeries == ts) + x

                if (index < 0) {
                    continue;
                }

                d3.selectAll("polyline.l" + index)
                  .style("stroke", highlightColor)
                  .style("opacity", 1)
                  .attr("stroke-width", (Math.abs(polylineValues[index]["thicknessMetric"]) * scalableLineWidth +
                      minLineWidth + hoverLineFactor) / lastScaleValue)

                d3.selectAll("rect.l" +  + index)
                  .style("fill", highlightColor)
                  .style("stroke", highlightColor)
                  .style("stroke-width", 3);

                d3.selectAll("circle.s-s" + index)
                  .style("stroke", highlightColor)
                  .style("fill", highlightColor)
                  .attr("r", 6);
            }
        }
    }
    var mousemoveCircle = function(d, i) {
        var text = "Sample " + d["label"];
        if (currentVisType != "projection") {
            text = text + "<br>Sample metric: " + d["colorMetric"].toFixed(2)
        }
        Tooltip
            .html(text)
            .style("left", (d3.event.pageX + 15) + "px")
            .style("top", (d3.event.pageY - 20) + "px")
            .style("opacity", d["mainSample"] ? 1 : 0);
    }

    var mouseleaveCircle = function(d, i) {
        Tooltip
            .style("opacity", 0);
        d3.selectAll("circle.s" + d["sample_id"])
            .style("stroke", "none")
            .style("fill", d["metricColor"])
            .style("opacity", 1.0);

        d3.selectAll("rect.s" + d["sample_id"])
          .style("stroke", "none")
          .style("fill", d["metricColor"])

        // lines before and after
        if (document.getElementById("showLines").checked == true) {
            for (var x = -1; x < 1; x++) {
                ts = d["timeSeries"]
                id = d["sample_id"]
                index = polylineValues.findIndex(y => y.startSample_id == id && y.timeSeries == ts) + x

                if (index < 0) {
                    continue;
                }

                d3.selectAll("polyline.l" + index)
                  .style("stroke", polylineValues[index]["metricColor"])
                  .attr("stroke-width", (Math.abs(polylineValues[index]["thicknessMetric"]) *
                                         scalableLineWidth + minLineWidth) / lastScaleValue)
                  .style("opacity", 1);

                d3.selectAll("rect.l" + index)
                  .style("stroke", "none")
                  .style("fill", polylineValues[index]["metricColor"])

                d3.selectAll("circle.s-s" + index)
                  .style("stroke", "none")
                  .style("fill", polylineValues[index]["metricColor"])
                  .attr("r", 2);
            }
        }

        scaleValues();
    }

    return [mouseoverCircle, mousemoveCircle, mouseleaveCircle]
}

/** Tooltips for connections. **/
function tooltipFunctionsForLines(scatter=false) {

    // Tooltip circles and lines
    var Tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")

    var mouseoverLine = function(d, i) {
        Tooltip
            .style("opacity", 0.9);

        d3.selectAll("polyline.l" + i)
          .style("stroke", highlightColor)
          .style("opacity", 1)
          .attr("stroke-width", (Math.abs(d["thicknessMetric"]) * scalableLineWidth +
                                 minLineWidth + hoverLineFactor) / lastScaleValue)

        d3.selectAll("rect.l" + i)
          .style("fill", highlightColor)
          .style("stroke", highlightColor)
          .style("stroke-width", 3);

        d3.selectAll("circle.s-s" + i)
          .style("stroke", highlightColor)
          .style("fill", highlightColor)
          .attr("r", 6);

        // circles
        if (document.getElementById("showSamples").checked == true) {
            for (var x = 0; x < 2; x++) {
                ts = d["timeSeries"]
                id = d["startSample_id"]
                index = circleValues.findIndex(y => y.sample_id == id && y.timeSeries == ts) + x

                d3.selectAll("circle.s" + index)
                  .style("stroke", highlightColor)
                  .style("opacity", 1)
                  .attr("r", ((circleValues[index]["mainSample"] == true ?
                      scalableCircleWidth * Math.abs(circleValues[index]["sizeMetric"]) + minCircleWidth :
                      smallerCircleWidth) + hoverCircleWidthFactor) / lastScaleValue * sampleScale)

                d3.selectAll("rect.s" + index)
                  .style("stroke", highlightColor)
                  .style("stroke-width", 3)
                  .style("fill", highlightColor)
            }
        }

        // halos
        if (document.getElementById("showHalos").checked == true) {
            ts = d["timeSeries"]
            id = d["startSample_id"]
            elements = haloValues.filter(y => y.ts1 == ts && y.seg1 == id || y.ts2 == ts && y.seg2 == id)

            for (var e of elements) {
                index = haloValues.indexOf(e)

                d3.selectAll("circle.h" + index)
                  .style("fill-opacity", function(d, i) { return d["opacity"] / 2 })
                  .style("stroke-opacity", 0.3);

                d3.selectAll("rect.h" + index)
                  .style("fill", highlightColor)
                  .style("stroke", highlightColor)
                  .style("opacity", 1)
                  .style("stroke-width", 3);
            }
        }
    }

    if (scatter) {
        var mousemoveLine = function(d, i) {
            Tooltip
                .html("Connection " + d["startSample"] + " &#8212; " + d["endSample"] + "<br>" +
                "2D distance: " + d["distance2D"].toFixed(2) + "<br>Original distance: " + d["distance50D"].toFixed(2))
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 20) + "px")
                .style("opacity", 1);
        }
    }
    else {
        var mousemoveLine = function(d, i) {
            Tooltip
                .html("Connection " + d["startSample"] + " &#8212; " + d["endSample"] +
                     "<br>2D distance: " + d["distance2D"].toFixed(2) + "<br>Original distance: " + d["distance50D"].toFixed(2) +
                     "<br>Line metric: " + d["colorMetric"].toFixed(2) +
                     "<br>Mean 2D distance: " + meanDistance2D.toFixed(2) +
                     "<br>Mean original distance: " + meanDistance50D.toFixed(2))
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 20) + "px")
                .style("opacity", 1);
        }
    }

    var mouseleaveLine = function(d, i) {
        Tooltip
            .style("opacity", 0);

        d3.selectAll("polyline.l" + i)
          .style("stroke", d["metricColor"])
          .attr("stroke-width", (Math.abs(d["thicknessMetric"]) * scalableLineWidth + minLineWidth) / lastScaleValue)
          .style("opacity", 1);

        d3.selectAll("rect.l" + i)
          .style("stroke", "none")
          .style("fill", d["metricColor"])

        d3.selectAll("circle.s-s" + i)
          .style("stroke", "none")
          .style("fill", d["metricColor"])
          .attr("r", 2);

        // circles
        if (document.getElementById("showSamples").checked == true) {
            for (var x = 0; x < 2; x++) {
                ts = d["timeSeries"]
                id = d["startSample_id"]
                index = circleValues.findIndex(y => y.sample_id == id && y.timeSeries == ts) + x

            d3.selectAll("circle.s" + index)
                .style("stroke", "none")
                .style("fill", circleValues[index]["metricColor"])
                .style("opacity", 1.0)
                .attr("r", ((circleValues[index]["mainSample"] == true ?
                    scalableCircleWidth * Math.abs(circleValues[index]["sizeMetric"]) + minCircleWidth :
                    smallerCircleWidth) + hoverCircleWidthFactor) / lastScaleValue * sampleScale)

            d3.selectAll("rect.s" + index)
              .style("stroke", "none")
              .style("fill", circleValues[index]["metricColor"])
            }
        }

        // halos
        if (document.getElementById("showHalos").checked == true) {
            ts = d["timeSeries"]
            id = d["startSample_id"]
            elements = haloValues.filter(y => y.ts1 == ts && y.seg1 == id || y.ts2 == ts && y.seg2 == id)

            for (var e of elements) {
                index = haloValues.indexOf(e)

                d3.selectAll("circle.h" + index)
                  .style("fill-opacity", function(d, i) { return d["opacity"] })
                  .style("stroke-opacity", 0.5);

                d3.selectAll("rect.h" + index)
                  .style("stroke", "none")
                  .style("fill", haloValues[index]["metricColor"])
                  .style("opacity", haloValues[index]["opacity"])
            }
        }

        scaleValues();
    }

    return [mouseoverLine, mousemoveLine, mouseleaveLine]
}

/** Tooltips for halos. **/
function tooltipFunctionsForHalos() {

    // Tooltip circles and lines
    var Tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")

    var mouseoverHalo = function(d, i) {
        Tooltip
            .style("opacity", 0.9);

        d3.selectAll("circle.h" + i)
            .style("fill-opacity", function(d, i) { return d["opacity"] / 2 })
            .style("stroke-opacity", 0.3);

        d3.selectAll("rect.h" + i)
          .style("fill", highlightColor)
          .style("stroke", highlightColor)
          .style("opacity", 1)
          .style("stroke-width", 3);

        // lines
        if (document.getElementById("showLines").checked == true) {
            for (var x = 1; x <= 2; x++) {
                ts = d["ts" + x]
                id = d["seg" + x]

                index = polylineValues.findIndex(y => y.startSample_id == id && y.timeSeries == ts)

                d3.selectAll("polyline.l" + index)
                  .style("stroke", highlightColor)
                  .style("opacity", 1)
                  .attr("stroke-width", (Math.abs(polylineValues[index]["thicknessMetric"]) * scalableLineWidth +
                      minLineWidth + hoverLineFactor) / lastScaleValue)

                d3.selectAll("rect.l" +  + index)
                  .style("fill", highlightColor)
                  .style("stroke", highlightColor)
                  .style("stroke-width", 3);

                d3.selectAll("circle.s-s" + index)
                  .style("stroke", highlightColor)
                  .style("fill", highlightColor)
                  .attr("r", 6);
            }
        }
    }

    var mousemoveHalo = function(d, i) {
        Tooltip
            .html("Intersection<br>Distance in orig. Space: " + d["distance"].toFixed(2) +
                  "<br>Max. distance between neighboring samples in orig. Space: " + d["maxDistance50D"].toFixed(2) +
                  "<br>Mean distance between neighboring samples in orig. Space: " + d["meanDistance50D"].toFixed(2) + "<br>" +
                  "T1: " + d["ts1"] + " - " + d["seg1"] + "<br>T2: " + d["ts2"] + " - " + d["seg2"])
            .style("left", (d3.event.pageX + 15) + "px")
            .style("top", (d3.event.pageY - 20) + "px")
            .style("opacity", 1);
    }

    var mouseleaveHalo = function(d, i) {
        Tooltip
            .style("opacity", 0);

        d3.selectAll("circle.h" + i)
            .style("fill-opacity", function(d, i) { return d["opacity"]})
            .style("stroke-opacity", 0.5);

        d3.selectAll("rect.h" + i)
          .style("stroke", "none")
          .style("fill", d["metricColor"])
          .style("opacity", function(d, i) { return d["opacity"] })

        // lines
        if (document.getElementById("showLines").checked == true) {
            for (var x = 1; x <= 2; x++) {
                ts = d["ts" + x]
                id = d["seg" + x]

                index = polylineValues.findIndex(y => y.startSample_id == id && y.timeSeries == ts)

                d3.selectAll("polyline.l" + index)
                  .style("stroke", polylineValues[index]["metricColor"])
                  .attr("stroke-width", (Math.abs(polylineValues[index]["thicknessMetric"]) *
                                         scalableLineWidth + minLineWidth) / lastScaleValue)
                  .style("opacity", 1);

                d3.selectAll("rect.l" + index)
                  .style("stroke", "none")
                  .style("fill", polylineValues[index]["metricColor"])

                d3.selectAll("circle.s-s" + index)
                  .style("stroke", "none")
                  .style("fill", polylineValues[index]["metricColor"])
                  .attr("r", 2);
            }
        }
    }

    return [mouseoverHalo, mousemoveHalo, mouseleaveHalo]
}

/** Scaling. **/
function zoomBehavior() {

    lastScaleValue = d3.event.transform.k;
    var zoom = d3.zoom().wheelDelta(myDelta).on("zoom", function () {
        zoomBehavior();
    });

    d3.select("#svgGroup").attr("transform", d3.event.transform);
    scaleValues();
}

/** Resize main visualization. **/
function resetted() {
    var svg = d3.select("#mainSvg");
    var zoom = d3.zoom().wheelDelta(myDelta).on("zoom", function () {
        zoomBehavior();
    });
   svg.call(zoom.transform, d3.zoomIdentity);
}

/** Correct scaling of all visual elements. **/
function scaleValues() {
    // scale
    scales = getMainScales();
    xScale = scales[0];
    yScale = scales[1];

    // connections
    if (currentVisType == "halo") {
        d3.select("#mainSvg").selectAll("polyline")
            .attr("stroke-width", function(d, i) {
                return ((1 - Math.pow(Math.abs(d["thicknessMetric"]), 2)) * scalableLineWidth + minLineWidth) /
                    lastScaleValue * lineScale * 0.5; });
    }
    else if (currentVisType == "highlighting") {
        d3.select("#mainSvg").selectAll("polyline")
        .attr("stroke-width", function(d, i) { return (Math.abs(d["thicknessMetric"]) * scalableLineWidth +
                                                   minLineWidth) / lastScaleValue * lineScale; });
    }
    else { // projection
        d3.select("#mainSvg").selectAll("polyline")
        .attr("stroke-width", function(d, i) { return (0.3 * scalableLineWidth + minLineWidth) / lastScaleValue * lineScale; });
    }

    d3.select("#mainSvg").selectAll("line")
        .attr("stroke-width", function(d, i) { return (Math.abs(d["thicknessMetric"]) + 0.5) / lastScaleValue * lineScale; });

    // labels
    d3.select("#mainSvg").selectAll(".idText")
        .attr("x", function(d, i) { return d["x"]; })
        .attr("y", function(d, i) { return d["y"] + 5 / lastScaleValue; })
        .attr("font-size", function(d, i) { return 12 / lastScaleValue + "px"; });

    // start/end
    d3.select("#mainSvg").select("#startAndEndCirclesGroup").selectAll("circle")
        .attr("r", function(d, i) { return highlightsCircleWidth / lastScaleValue; })
        .attr("stroke-width", function(d, i) { return 3 / lastScaleValue; });

    // samples and halos
   if (currentVisType == "highlighting") {
       d3.select("#mainSvg").select("#mainCircleGroup").selectAll("circle")
        .attr("r", function(d, i) { return (d["mainSample"] == true ?
                                    scalableCircleWidth * Math.abs(d["sizeMetric"]) + minCircleWidth : smallerCircleWidth) / lastScaleValue * sampleScale; })
        .attr("stroke-width", function(d, i) { return 1 / lastScaleValue });

       d3.select("#mainSvg").select("#haloCircleGroup").selectAll("circle")
        .attr("r", function(d, i) { return d["size"] / lastScaleValue * haloScale; })
        .style("stroke-width", 1 / lastScaleValue);
   }
   else if (currentVisType == "halo") {
       for (var i = 0; i < circleValues.length; i++) {
           d3.select("#mainSvg").select("#mainCircleGroup" + i).selectAll("circle")
            .attr("r", function(d, i) { return (d["mainSample"] == true ?
                                        scalableCircleWidth * (1 - Math.pow(Math.abs(d["sizeMetric"]), 2)) + minCircleWidth :
                                        smallerCircleWidth) / lastScaleValue * sampleScale * 0.5; })
            .attr("stroke-width", function(d, i) { return 1 / lastScaleValue });
       }

       for (var i = 0; i < haloValues.length; i++) {
          d3.select("#mainSvg").select("#haloCircleGroup" + i).selectAll("ellipse")
            .attr("rx", function(d, i) { return d["size"] / lastScaleValue * haloScale * 2; })
            .attr("ry", function(d, i) { return d["size"] / lastScaleValue * haloScale * 2; });
       }
   }
   else {
       for (var i = 0; i < circleValues.length; i++) {
           d3.select("#mainSvg").select("#mainCircleGroup" + i).selectAll("circle")
            .attr("r", function(d, i) { return (d["mainSample"] == true ?
                                        scalableCircleWidth * 0.5 + minCircleWidth :
                                        smallerCircleWidth) / lastScaleValue * sampleScale; })
            .attr("stroke-width", function(d, i) { return 1 / lastScaleValue });
       }

       d3.select("#mainSvg").select("#haloCircleGroup").selectAll("circle")
        .attr("r", function(d, i) { return 0 / lastScaleValue * haloScale; })
        .style("stroke-width", 1 / lastScaleValue);
   }
}

/** Determine dimensions for the visualization. **/
function getMainScales() {
    var margin = 30;

    var plotElement = document.getElementById("mainSvg");
    var svgWidth = plotElement.getBoundingClientRect().width - 2 * margin;
    var svgHeight = plotElement.getBoundingClientRect().height - 2 * margin;

    valuesFlattened = []
    for (var i = 0; i < valuesList.length; i++) {
        valuesFlattened = valuesFlattened.concat(valuesList[i])
    }

    minValx = d3.min(valuesFlattened, function (d) { return d[0]; });
    minValy = d3.min(valuesFlattened, function (d) { return d[1]; });
    maxValx = d3.max(valuesFlattened, function (d) { return d[0]; });
    maxValy = d3.max(valuesFlattened, function (d) { return d[1]; });
    differenceX = maxValx - minValx;
    differenceY = maxValy - minValy;

    ratioX = svgWidth / differenceX
    ratioY = svgHeight / differenceY
    ratioXLargerThanY = ratioX > ratioY

    var scaleTemp = d3.scaleLinear().range([margin, ratioXLargerThanY ? (svgHeight + margin) : (svgWidth + margin)]);
    scaleTemp.domain([0, ratioXLargerThanY ? (maxValy - minValy) : (maxValx - minValx)]);

    diffShiftX = (svgWidth - scaleTemp(maxValx - minValx) + margin) / 2;
    diffShiftY = (svgHeight - scaleTemp(maxValy - minValy) + margin) / 2;
    // scale and center
    var scaleX = d3.scaleLinear().range([ratioXLargerThanY ? (margin + diffShiftX) : margin, ratioXLargerThanY ?
        (svgHeight + margin + diffShiftX) : (svgWidth + margin)]);
    var scaleY = d3.scaleLinear().range([ratioXLargerThanY ? margin : (margin + diffShiftY), ratioXLargerThanY ?
        (svgHeight + margin) : (svgWidth + margin + diffShiftY)]);
    scaleX.domain([minValx, ratioXLargerThanY ? (maxValy - minValy + minValx) : maxValx]);
    scaleY.domain([minValy, ratioXLargerThanY ? maxValy : (maxValx - minValx + minValy)]);

    function scaleY2(d) { return plotElement.getBoundingClientRect().height - scaleY(d) }

    return [scaleX, scaleY2];
}

/** Colors for color map. **/
// moves a value from [0, 1] to e.g., [0.1, 1] to avoid every light colors of the color maps
function scaleValueForColorMap(value, leftOffset = 0, rightOffset = 0) {
    return (value) * (1 - leftOffset - rightOffset) + leftOffset;
}

/** Colors for connections. **/
function getLineColor(value, timeSeries = 0) {
    if (document.getElementById("lineMetric").value == "equal1_line") {
        colorString = timeColormaps[timeSeries % timeColormaps.length](scaleValueForColorMap(0.55))
    }
    else if (document.getElementById("lineMetric").value == "equal2_line") {
        x = (timeSeries * 71) % 210;
        colorString = "rgb(" + x + "," + x + "," + x + ")";
    }
    else if (document.getElementById("lineMetric").value == "time_line") {
        colorString = timeColormaps[timeSeries % timeColormaps.length](scaleValueForColorMap(value))
    }
    else {
        colorString = linearLineScale(scaleValueForColorMap(value))
    }
    return colorString;
}

/** Colors for samples. **/
function getSampleColor(value, timeSeries = 0) {
    if (currentVisType != "highlighting") { // for static vis
        colorString = timeColormaps[timeSeries % timeColormaps.length](scaleValueForColorMap(value, 0.1, 0.1))
    }

    else if (document.getElementById("sampleMetric").value == "equal_sample") {
        colorString = timeColormaps[timeSeries % timeColormaps.length](scaleValueForColorMap(0.55))
        //colorString = "#b642f5"//d3.interpolateRdPu(0.9)
    }
    else if (document.getElementById("sampleMetric").value == "time_sample") {
        colorString = timeColormaps[timeSeries % timeColormaps.length](scaleValueForColorMap(value))
    }
    else {
        colorString = linearSampleScale(scaleValueForColorMap(value))
    }
    return colorString;
}

/** Save main view as svg. **/
// http://techslides.com/save-svg-as-an-image
// http://techslides.com/demos/d3/svg-to-image-3.html
function saveSVG() {
    if (currentDatasetName == "") {
        return;
    }

    var html = d3.select("#mainSvg")
        .attr("version", 1.1)
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .node().parentNode.innerHTML;

    // set correct dimensions
    var svgWidth = document.getElementById("mainSvg").getBoundingClientRect().width;
    var svgHeight = document.getElementById("mainSvg").getBoundingClientRect().height;
    html = html.replace('width="100%" height="100%"', 'width="' + svgWidth + '" height="' + svgHeight + '"')

    var imgsrc = 'data:image/svg+xml;base64,'+ btoa(html);

    var image = new Image;
    image.src = imgsrc;
    image.onload = function() {
        var a = document.createElement("a");
        a.download = currentDatasetName + ".svg";
        a.href = imgsrc;
        a.click();
    };
}

/** Save main view as png. **/
// http://techslides.com/demos/d3/svg-to-image-3.html
function savePNG() {
    if (currentDatasetName == "") {
        return;
    }
    var html = d3.select("#mainSvg")
        .attr("version", 1.1)
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .node().parentNode.innerHTML;

    // set correct dimensions
    var svgWidth = document.getElementById("mainSvg").getBoundingClientRect().width;
    var svgHeight = document.getElementById("mainSvg").getBoundingClientRect().height;
    html = html.replace('width="100%" height="100%"', 'width="' + svgWidth + '" height="' + svgHeight + '"')

    var imgsrc = 'data:image/svg+xml;base64,'+ btoa(html);

    var img = '<img src="'+imgsrc+'">';
    d3.select("#svgdataurl").html(img);

    var canvas = document.querySelector("canvas"),
        context = canvas.getContext("2d");

    canvas.width = svgWidth;
    canvas.height = svgHeight;

    var image = new Image;
    image.src = imgsrc;
    image.onload = function() {
        context.drawImage(image, 0, 0);

        //save and serve it as an actual filename
        binaryblob();

        var a = document.createElement("a");
        a.download = currentDatasetName + ".png";
        a.href = canvas.toDataURL("image/png");

        var pngimg = '<img src="'+a.href+'">';
        d3.select("#pngdataurl").html(pngimg);

        a.click();
    };
}

/** Help function to save images. **/
// http://techslides.com/demos/d3/svg-to-image-3.html
function binaryblob() {
    var byteString = atob(document.querySelector("canvas").toDataURL().replace(/^data:image\/(png|jpg);base64,/, ""));
	var ab = new ArrayBuffer(byteString.length);
	var ia = new Uint8Array(ab);
	for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    var dataView = new DataView(ab);
	var blob = new Blob([dataView], {type: "image/png"});
	var DOMURL = self.URL || self.webkitURL || self;
	var newurl = DOMURL.createObjectURL(blob);

	var img = '<img src="'+newurl+'">';
    d3.select("#img").html(img);
}

/** Help function for zooming. **/
// https://stackoverflow.com/questions/44960362/how-to-use-zoom-wheeldelta-in-d3-v4
function myDelta() {
    return -d3.event.deltaY * (d3.event.deltaMode ? 120 : 1) / 1500;
}

/** Disables in the UI that a scaling such as standardization is used. **/
function disableScalingSamples(disable) {
    if (disable) {
        document.getElementById("standardization_samples").checked = !disable
        document.getElementById("maxScaling_samples").checked = !disable
        document.getElementById("minmaxScaling_samples").checked = !disable
        document.getElementById("posNegScaling_samples").checked = !disable
    }
}

/** Disables in the UI that a scaling such as standardization is used. **/
function disableScalingLines(disable) {
    if (disable) {
        document.getElementById("standardization_connections").checked = !disable
        document.getElementById("maxScaling_connections").checked = !disable
        document.getElementById("minmaxScaling_connections").checked = !disable
        document.getElementById("posNegScaling_connections").checked = !disable
    }
}

/** Switch visualization modes. **/
function switchView(type) {
    if (type == "u" ) {
        document.getElementById("switchToAlternativeVisH").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisP").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisU").classList.add("buttonSelection");
        currentVisType = "highlighting";
    }
    else if (type == "h" ) {
        document.getElementById("switchToAlternativeVisP").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisU").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisH").classList.add("buttonSelection");
        currentVisType = "halo";
    }
    else if (type == "p" ) {
        document.getElementById("switchToAlternativeVisH").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisU").classList.remove("buttonSelection");
        document.getElementById("switchToAlternativeVisP").classList.add("buttonSelection");
        currentVisType = "projection";
    }

    document.getElementById("showHalos").disabled = (type == "p");
    document.getElementById("slidingWindowSize").disabled = (type == "p");
    document.getElementById("neighborhoodInput").disabled = (type == "p");
    recalculate();
}
