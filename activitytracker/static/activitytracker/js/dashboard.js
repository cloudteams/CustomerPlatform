/**
 * Created by Aggelos on 10/23/2015.
 */

$(document).on('ready',function() {

    // Percent ( % ) Circle Configuration
    $(".whiteCircle").knob({
        'min': 0,
        'max': 100,
        'readOnly': true,
        'width': 120,
        'height': 120,
        'bgColor': 'rgba(255,255,255,0.5)',
        'fgColor': 'rgba(255,255,255,0.9)',
        'dynamicDraw': true,
        'thickness': 0.2,
        'tickColorizeValues': true
    });

    // Text and Speed Configuration of Knobs
    $(".circleStatsItemBox").each(function () {

        var value = $(this).find(".value > .number").html();
        var percent = $(this).find("input").val() / 100;

        (percent == 0) ? countSpeed = 1 : countSpeed = 2700 * percent;

        endValue = $(this).find(".count > .number").html();

        $(this).find(".count > .number").countTo({

            from: 0,
            to: endValue,
            speed: countSpeed,
            refreshInterval: 50

        });

    });
    // Start of: Chart for Instances of Current & Previous Week
    var svg = dimple.newSvg("#ActivitiesInstanceChart", "100%", "100%");

    var timelineChart = new dimple.chart(svg, chart_data);
    timelineChart.setBounds('10%', '10%', '90%', '75%');

    timelineChart.addCategoryAxis("x", "day").addOrderRule(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
    var y = timelineChart.addMeasureAxis("y", "instances");
    y.tickFormat = "d";

    timelineChart.addSeries("type", dimple.plot.line);
    timelineChart.addLegend('5%', 0, "95%", 0, "right");

    timelineChart.draw();

    $(window).on('resize', function () {
        timelineChart.draw(0, true);
    });

    // End of: Chart for Instances of Current & Previous Week

    /* ------------------------------------------------------ */

    // Start of:  Top (10) Activities of the Week Chart
    svg = dimple.newSvg("#TopActivitiesInstanceChart", "100%", "100%");

    var barChart = new dimple.chart(svg, top_activities_chart_data_by_instance);
    barChart.setBounds('10%', '10%', '90%', '75%');

    var x = barChart.addMeasureAxis("x", 'instances');
    x.tickFormat = "d";
    barChart.addCategoryAxis("y", "name").addOrderRule('instances');


    barChart.addSeries('name', dimple.plot.bar);
    barChart.addLegend('5%', 0, "95%", 0, "right");

    barChart.draw();

    $(window).on('resize', function () {
        barChart.draw(0, true);
    });
    // End of: Top (10) Activities of the Week Chart

});

// Start of: Chart for Duration of Current & Previous Week (needs to be here in order to properly calculate the width)
$('#carousel-categories.carousel').one('slid.bs.carousel', function() {
    var svg = dimple.newSvg("#ActivitiesMinuteChart", "100%", "100%");

    var timelineChart = new dimple.chart(svg, chart_data);
    timelineChart.setBounds('10%', '10%', '90%', '75%');

    timelineChart.addCategoryAxis("x", "day").addOrderRule(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
    timelineChart.addMeasureAxis("y", "minutes");

    timelineChart.addSeries("type", dimple.plot.line);
    timelineChart.addLegend('5%', 0, "95%", 0, "right");

    timelineChart.draw();

    $(window).on('resize', function () {
        timelineChart.draw(0, true);
    });
});
// End of: Chart for Duration of Current & Previous Week (needs to be wrapped around a slid.bs.carousel event)

// Start of: Chart of Top 10 Activities of the week (needs to be here in order to properly calculate the width)
$('#carousel-activities.carousel').one('slid.bs.carousel', function() {
    var svg = dimple.newSvg("#TopActivitiesMinuteChart", "100%", "100%");

    var barChart = new dimple.chart(svg, top_activities_chart_data_by_duration);
    barChart.setBounds('10%', '10%', '90%', '75%');

    barChart.addMeasureAxis("x", 'minutes');
    barChart.addCategoryAxis("y", "name").addOrderRule('minutes');


    barChart.addSeries('name', dimple.plot.bar);
    barChart.addLegend('5%', 0, "95%", 0, "right");

    barChart.draw();

    $(window).on('resize', function () {
        barChart.draw(0, true);
    });
});
// End of: Chart of Top 10 Activities of the week (needs to be wrapped around a slid.bs.carousel event)

// Remove Edit & Delete Activity Options from Display-Activity Modal
$('#showActivityModal').on("loaded.bs.modal", function(e) {
    $('#editactivity').addClass('hidden');
    $('#deleteactivity').addClass('hidden');
});
