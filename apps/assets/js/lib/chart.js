/*
 * Chart JS
 */

(function($) {

	// use strict
	"use strict";

	$(document).ready(function () {

    /**
     * Line Chart
     *
     * @opts: options for Line chart
     */
    $.fn.chartLine = function(opts) {

      var defaultOpts = {
        type: "line",
        options: {
          scales: {
            xAxes: [{
              ticks: {
                fontColor: "#c1c1c3"
              },
              gridLines: {
                color: "rgba(255,255,255,.3)",
                zeroLineColor: "rgba(255,255,255,.3)"
              }
            }],
            yAxes: [{
              ticks: {
                padding: 5,
                fontColor: "#c1c1c3"
              },
              gridLines: {
                color: "rgba(255,255,255,.3)",
                zeroLineColor: "rgba(255,255,255,.3)"
              }
            }]
          },
          legend: {
            onClick: false,
            display: true,
            position: "top",
            labels: {
              boxWidth: 40,
              fontSize: 10,
              fontColor: "#efefef"
            }
          },
          tooltips: {
            intersect: false,
            backgroundColor: "#08dd0a",
            titleFontSize: 0,
            bodyFontFamily: "Raleway",
            bodyFontSize: 14,
            bodyFontColor: "#333",
            titleMarginBottom: 0,
            displayColors: false,
            yPadding: 8,
            xPadding: 12,
            callbacks: {
              label: function(tooltipItem, data) {
                return "Accuracy: " + tooltipItem.yLabel + "%";
              }
            }
          }
        },
        data: {
          labels: opts.labels,
          datasets: []
        }
      };

      if (opts.datasets.length <= 1) {
        defaultOpts.options.legend.onClick = false;
      }

      for (var i in opts.datasets) {
        defaultOpts.data.datasets.push($.extend({}, {
          backgroundColor: "#08dd0a",
          pointBorderColor: "#08dd0a",
          pointBackgroundColor: "#333",
          fill: false,
          lineTension: 0,
          borderWidth: 3,
          borderColor: "#08dd0a"
        }, opts.datasets[i]));
      }

      // start chart
      return new Chart($(this).get(0).getContext("2d"), defaultOpts);
    };

    /**
     * Plot Chart
     *
     * @opts: options for Plot chart
     */
    $.fn.chartPlot = function(data) {

      var defaultOpts = {
        type: "bar",
        options: {
          scales: {
            xAxes: [{
              display: false
            }],
            yAxes: [{
              display: false
            }]
          },
          legend: {
            display: false
          },
          tooltips: {
            enabled: false
          }
        },
        data: {
          labels: data,
          datasets: [{
            data: data,
            backgroundColor: "#08dd0a",
            lineTension: 0,
            borderWidth: 0,
            borderColor: "#08dd0a"
          }]
        }
      };

      // start chart
      return new Chart($(this).get(0).getContext("2d"), defaultOpts);
    };

    /**
     * Area Chart
     *
     * @opts: options for Area chart
     */
    $.fn.chartArea = function(opts) {

      var defaultOpts = {
        type: "line",
        options: {
          scales: {
            xAxes: [{
              ticks: {
                fontColor: "#c1c1c3"
              },
              gridLines: {
                color: "rgba(255,255,255,.3)",
                zeroLineColor: "rgba(255,255,255,.3)"
              }
            }],
            yAxes: [{
              display: false,
            }]
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              boxWidth: 15,
              fontSize: 14,
              fontColor: "#efefef",
              padding: 10
            }
          },
          tooltips: {
            mode: "index",
            intersect: false,
            titleFontSize: 0,
            titleMarginBottom: 0,
          },
          hover: {
            mode: "nearest",
            intersect: true
          },
        },
        data: {
          labels: opts.labels,
          datasets: []
        }
      };

      if (opts.datasets.length <= 1) {
        defaultOpts.options.legend.onClick = false;
      }

      for (var i in opts.datasets) {
        defaultOpts.data.datasets.push($.extend({}, {
          fill: true,
          radius: 0,
          borderWidth: 1,
        }, opts.datasets[i]));
      }

      // start chart
      return new Chart($(this)[0].getContext("2d"), defaultOpts);
    };

    /**
     * Bar Chart
     *
     * @opts: options for bar chart
     */
    $.fn.chartBar = function(opts) {

      var defaultOpts = {
        type: "bar",
        options: {
          scales: {
            xAxes: [{
              ticks: {
                fontColor: "#c1c1c3"
              },
              gridLines: {
                display: false,
              }
            }],
            yAxes: [{
              ticks: {
                padding: 10,
                fontColor: "#c1c1c3"
              },
              gridLines: {
                drawBorder: false,
                color: "rgba(255,255,255,.3)",
                zeroLineColor: "rgba(255,255,255,.3)"
              }
            }],
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              boxWidth: 15,
              fontSize: 14,
              fontColor: "#efefef",
              padding: 10
            }
          },
          tooltips: {
            mode: "index",
            intersect: false,
            titleFontSize: 0,
            titleMarginBottom: 0,
          },
          hover: {
            mode: "nearest",
            intersect: true
          },
        },
        data: {
          labels: opts.labels,
          datasets: []
        }
      };

      for (var i in opts.datasets) {
        defaultOpts.data.datasets.push($.extend({}, {
          backgroundColor: "#08dd0a",
          fill: true,
          radius: 0,
          borderWidth: 1,
          borderColor: "#08dd0a"
        }, opts.datasets[i]));
      }

      // start chart
      return new Chart($(this).get(0).getContext("2d"), defaultOpts);
    };

    /**
     * World Map function, drive datamaps plugin
     *
     * @opts: options for datamaps
     */
	  $.fn.chartWorldMap = function(opts) {

	    // reset options
	    if (opts.bubbles && opts.bubbles.length) {
	      for (var i in opts.bubbles) {
	        if (opts.bubbles[i].fillKey) {
	          opts.bubbles[i].highlightFillColor = opts.fills[opts.bubbles[i].fillKey];
	        }
	      }
	    }

	    opts = $.extend({}, {
	      scope: "world",
	      element: $(this).get(0),
        responsive: true,
	      fills: {
	        defaultFill: "rgba(255,255,255,.1)",
	      },
	      geographyConfig: {
	        hideAntarctica: false,
	        borderColor: "rgba(255,255,255,.05)",
	        popupOnHover: false, //disable the popup while hovering
	        highlightOnHover: true,
	        highlightFillColor: "rgba(255,255,255,0.15)",
	        highlightBorderColor: "rgba(255,255,255,0.2)",
	        highlightBorderWidth: 1
	      },
	      bubblesConfig: {
	        borderWidth: 0,
	        borderOpacity: 0.2,
	        borderColor: "#FFFFFF",
	        popupOnHover: true,
	        radius: null,
	        fillOpacity: 0.5,
	        highlightOnHover: true,
	        highlightBorderWidth: 1,
	        highlightBorderColor: "rgba(255,255,255,.2)",
	        highlightBorderOpacity: 0.8,
	        highlightFillColor: "rgba(255,255,255,.3)",
	        highlightFillOpacity: 0.8
	      }
	    }, opts);

      var worldMap = new Datamap(opts);
      worldMap.bubbles(opts.bubbles, {
        popupTemplate: function(geo, data) {
          return "<div class=\"hoverinfo\">" + data.name + ": " + data.radius + "</div>";
        }
      });

	    // responsive
      $(window).on("resize", function() {
        worldMap.resize();
      });
	  };

		///////////

	}); // ready
})(jQuery);