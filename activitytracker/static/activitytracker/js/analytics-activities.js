/**
 * Created by Aggelos.
 */

    var svg = dimple.newSvg("#all-activities-chart", "100%", "100%");

    function updateAllActivitiesCharts() {
        var range = '01/01/2016 - ' + moment().format("MM/DD/YYYY");
        var metric = "Number of Instances";

		$.ajax({
			type: "post",
			data: { csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + "analytics/activities/update/activities_all/",
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg.selectAll('*').remove();
                    svg2.selectAll('*').remove();
                }
                catch(err) {}
                var chartOuter = new dimple.chart(svg, response[1]);
                var chartInner = new dimple.chart(svg, response[0]);
                chartOuter.setBounds('0%', '0%', '80%', '100%');
                chartInner.setBounds('0%', '0%', '80%', '100%');

                var inner_p, outer_p;
                if ( metric == "Number of Instances") {
                    outer_p = chartOuter.addMeasureAxis("p", "Instances");
                    inner_p = chartInner.addMeasureAxis("p", "Instances");
				}
                else{
                    outer_p = chartOuter.addMeasureAxis("p", "Hours");
                    inner_p = chartInner.addMeasureAxis("p", "Hours");
                }
				var chartOuterLegend = chartOuter.addLegend("63%", 50, 90, 500, "left");
				var chartInnerLegend = chartInner.addLegend("63%", 0, 90, 300, "left");
                var outerRing = chartOuter.addSeries("Activity", dimple.plot.pie);
                var innerRing = chartInner.addSeries("Category", dimple.plot.pie);
                outerRing.addOrderRule("Category");
                innerRing.addOrderRule("Category");
				outerRing.innerRadius = "-30px";
				innerRing.outerRadius = "-40px";
				innerRing.innerRadius = "-70px";

				chartOuter.defaultColors = [new dimple.color("#98abc5"), new dimple.color("#8a89a6"), new dimple.color("#ff8c00"),new dimple.color("#995411"),
                                            new dimple.color("#7b6888"), new dimple.color("#E07C27"), new dimple.color("#a05d56"), new dimple.color("#d0743c"),
                                            new dimple.color("#7b6888"), new dimple.color("#266419"), new dimple.color("#DF7821"), new dimple.color("#4DA4DA"),
                                            new dimple.color("#A5C59E"), new dimple.color("#5C5596"), new dimple.color("#CA9A9A"), new dimple.color("#D8E4EA"),
                                            new dimple.color("#326277"), new dimple.color("#9174A5"), new dimple.color("#7B0404"), new dimple.color("#EAE2EF"),
                                            new dimple.color("#562323"), new dimple.color("#03671F"), new dimple.color("#7b6888"), new dimple.color("#E3F25E"),
                                            new dimple.color("#F498DA"), new dimple.color("#6b486b") ];

                var orange_colors = ["rgb(182, 102, 54)","rgb(186, 87, 28)",
                                "rgb(202, 85, 16)","rgb(236, 98, 17)","rgb(253, 101, 12)","rgb(253, 128, 54)","rgb(252, 143, 52)",
                                "rgb(252, 181, 73)","rgb(252, 217, 143)","rgb(240, 168, 13)","rgb(253, 175, 7)","rgb(247, 202, 104)",
                                "rgb(224, 136, 18)","rgb(247, 232, 154)","rgb(247, 187, 108)","rgb(240, 209, 161)"];
                var blue_colors = ["rgb(6, 67, 86)","rgb(15, 88, 184)","rgb(11, 105, 132)","rgb(71, 122, 190)","rgb(37, 134, 163)","rgb(50, 158, 190)",
                                   "rgb(58, 180, 216)","rgb(64, 198, 237)","rgb(102, 215, 249)","rgb(140, 223, 247)","rgb(176, 235, 252)" ];

                var purple_colors = ["rgb(48, 17, 87)","rgb(88, 35, 115)","rgb(121, 28, 136)","rgb(129, 58, 140)","rgb(160, 78, 173)","rgb(183, 39, 207)",
                                   "rgb(224, 63, 250)","rgb(232, 111, 252)","rgb(239, 153, 253)","rgb(242, 192, 250)" ];

                var green_colors = ["rgb(40, 60, 6)","rgb(58, 84, 13)","rgb(82, 118, 20)","rgb(91, 144, 1)","rgb(101, 144, 29)","rgb(124, 179, 30)",
                                   "rgb(155, 219, 42)","rgb(170, 219, 84)","rgb(189, 240, 100)","rgb(102, 215, 249)","rgb(201, 249, 119)","rgb(217, 250, 159)" ];

                var red_colors = ["rgb(77, 7, 7)","rgb(95, 9, 9)","rgb(111, 0, 0)","rgb(145, 12, 12)","rgb(174, 2, 2)","rgb(194, 12, 12)",
                                   "rgb(221, 23, 23)","rgb(249, 13, 13)","rgb(253, 35, 35)","rgb(252, 63, 63)","rgb(247, 104, 104)","rgb(247, 162, 162)" ];

                var black_colors = ["rgb(8, 7, 7)","rgb(39, 33, 33)","rgb(63, 54, 54)","rgb(81, 74, 74)","rgb(94, 88, 88)","rgb(113, 108, 108)",
                                   "rgb(142, 139, 139)","rgb(169, 166, 166)","rgb(194, 189, 189)","rgb(252, 63, 63)","rgb(216, 213, 213)","rgb(239, 234, 234)" ];

                var color_dict = {"Communication/Socializing": blue_colors,
                              "Fun/Leisure/Hobbies": orange_colors,
                              "Responsibilities": red_colors,
                              "Self-care/Everyday Needs": black_colors,
                              "Transportation": purple_colors,
                              "Sports/Fitness": green_colors
                };
                var prev_category = "";
                var counter = 0;
                $.each(response[0], function(i, e) {
                    chartInner.assignColor(e.Category, e.Color);
                });
                $.each(response[1], function(i, e) {
                    if (e.Category != prev_category){
                        counter = 0
                    }
                    chartOuter.assignColor(e.Activity, color_dict[e.Category][counter%16]);
                    prev_category = e.Category;
                    counter += 1;
                });

                chartOuter.draw();
                chartInner.draw();

                $(window).on('resize', function() {
                    chartOuter.draw(0, true);
                    chartInner.draw(0, true);
                });

			}
	    });
     };

    $(window).on('load', function() {
        updateAllActivitiesCharts();
    });