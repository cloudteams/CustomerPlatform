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

    // Start of:  Top (10) Activities of the Week Chart
    svg = dimple.newSvg("#Top10ActivitiesInstanceChart", "100%", "100%");

    var barChartMiddle = new dimple.chart(svg, top_activities_chart_data_by_instance);
    barChartMiddle.setBounds('20%', '0%', '77%', '75%');

    var x = barChartMiddle.addMeasureAxis("x", 'instances');
    x.tickFormat = "d";
    barChartMiddle.addCategoryAxis("y", "name").addOrderRule('instances');

    barChartMiddle.addSeries('name', dimple.plot.bar);

    barChartMiddle.draw();

    $(window).on('resize', function () {
        barChartMiddle.draw(0, true);
    });
    // End of: Top (10) Activities of the Week Chart

    /****************************************************/

    // Start of: Chart for Instances of Current & Previous Week
    var svg = dimple.newSvg("#ActivitiesInstanceChart", "100%", "100%");

    var barChartBottom = new dimple.chart(svg, chart_data);
    barChartBottom.setBounds('10%', '10%', '90%', '75%');

    barChartBottom.addCategoryAxis("x", ["day", "type"]).addOrderRule(day_order);
    var y = barChartBottom.addMeasureAxis("y", "instances");
    y.tickFormat = "d";

    barChartBottom.addSeries("type", dimple.plot.bar).addOrderRule("period_order", true);
    barChartBottom.addLegend('5%', 0, "95%", 0, "right");

    barChartBottom.draw();

    $(window).on('resize', function () {
        barChartBottom.draw(0, true);
    });

    // End of: Chart for Instances of Current & Previous Week

});

// Start of: Chart for Duration of Current & Previous Week (needs to be here in order to properly calculate the width)
$('#carousel-categories.carousel').one('slid.bs.carousel', function() {
    var svg = dimple.newSvg("#ActivitiesMinuteChart", "100%", "100%");

    var barChart = new dimple.chart(svg, chart_data);
    barChart.setBounds('10%', '10%', '90%', '75%');

    barChart.addCategoryAxis("x", ["day", "type"]).addOrderRule(day_order);
    barChart.addMeasureAxis("y", "minutes");

    barChart.addSeries("type", dimple.plot.bar).addOrderRule("period_order", true);
    barChart.addLegend('5%', 0, "95%", 0, "right");

    barChart.draw();

    $(window).on('resize', function () {
        barChart.draw(0, true);
    });
});
// End of: Chart for Duration of Current & Previous Week (needs to be wrapped around a slid.bs.carousel event)

 /******************************************************************/

// Start of: Chart of Top 10 Activities of the week (needs to be here in order to properly calculate the width)

$('#carousel-activities.carousel').one('slid.bs.carousel', function() {


    var svg = dimple.newSvg("#Top10ActivitiesMinuteChart", "100%", "100%");

    var barChart = new dimple.chart(svg, top_activities_chart_data_by_duration);
    barChart.setBounds('20%', '0%', '77%', '75%');

    barChart.addMeasureAxis("x", 'minutes');
    barChart.addCategoryAxis("y", "name").addOrderRule('minutes');


    barChart.addSeries('name', dimple.plot.bar);

    barChart.draw();

    $(window).on('resize', function () {
        barChart.draw(0, true);
    });
});

// End of of: Chart of Top 10 Activities of the week (needs to be here in order to properly calculate the width)

 /******************************************************************/

// Start of: Chart for Provider Lifetime Data

    var svg = dimple.newSvg("#ProviderActivitiesLifetimeChart", "100%", "100%");

    var barChart = new dimple.chart(svg, lifetime_provider_activities);
    barChart.setBounds('10%', '0%', '85%', '70%');

    barChart.addCategoryAxis("x", "provider");
    var y = barChart.addMeasureAxis("y", "instances");
    y.tickFormat = "d";

    barChart.addSeries("provider", dimple.plot.bar);

    barChart.draw();

    $(window).on('resize', function () {
        barChart.draw(0, true);
    });

// End of: Chart for Provider Lifetime Data

/*****************************************************/

// Remove Edit & Delete Activity Options from Display-Activity Modal
$('#showActivityModal').on("loaded.bs.modal", function(e) {
    $('#editactivity').addClass('hidden');
    $('#deleteactivity').addClass('hidden');
});

