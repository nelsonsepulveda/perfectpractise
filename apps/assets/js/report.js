$(document).ready(function () {

    var tz_offset = moment().utcOffset();

    var $club_select = $("#club-select"),
        $club_chart = $("#club-chart-wrapper");

    var $putting_select = $("#putting-select"),
        $putting_chart = $("#putting-chart-wrapper");

    var HITS_INDEX = 0, SHOTS_INDEX = 1, ACCURACY_INDEX = 2,
        daily_chart_labels=[], daily_shot_data=[], daily_long_count=0, daily_short_count=0, daily_putting_count=0, daily_long_dist=0,
        daily_club_info=null,

        club_date_range = [],
        club_chart_lines = {
            'avg_dist': {
                'data': {},
                'color': "#ffe498",
                'title': 'Avg Distance'
            },
            'hit_acc': {
                'data': {},
                'color': "#a1c3c8",
                'title': 'Club'
            },
            'draw_acc': {
                'data': {},
                'color': "#f9ca9b",
                'title': 'Draw'
            },
            'fade_acc': {
                'data': {},
                'color': "#f17e0c",
                'title': 'Fade'
            },
            'straight_acc': {
                'data': {},
                'color': "#fbb065",
                'title': 'Straight'
            },
            'low_acc': {
                'data': {},
                'color': "#ffff00",
                'title': 'Trajectory Low'
            },
            'high_acc': {
                'data': {},
                'color': "#b3de67",
                'title': 'Trajectory High'
            }
        },

        put_date_range = [], feet_range = [],
        put_color_list = ["#ffe498", "#a1c3c8", "#f9ca9b", "#f17e0c", "#fbb065", "#ffff00", "#b3de67"],
        put_chart_lines = {
            'acc': {},
            'left': {},
            'right': {},
            'short': {},
            'long': {}
        };


    function initialize_club_data() {
        club_date_range = [];
        $.each(club_chart_lines, function (k, item) {
            item.data = {};
        });
    }

    function initialize_putting_data() {
        put_date_range = []; feet_range = [];
        put_chart_lines = {
            'acc': {},
            'left': {},
            'right': {},
            'short': {},
            'long': {}
        };
    }

    function initialize_daily_data() {
        $(".prg_daily_overall").data("val", 0);
        $(".prg_daily_bestclub").data("val", 0).data("best-club", "Unknown");
        daily_chart_labels=[]; daily_shot_data=[]; daily_long_count=0; daily_short_count=0; daily_putting_count=0; daily_long_dist=0;
        daily_club_info=null;
    }

    function renderClubChart(){
        $club_chart.html("").html("<canvas id=\"club-chart-line-1\"></canvas>");
        var selected_club = $club_select.val(),
            datasets = [], data_series=[];

        $.each(club_chart_lines, function (k, item) {
            data_series = [];
            $.each(club_date_range, function (i, k_date) {
                if ( $.isEmptyObject(item.data)
                    || typeof item.data[selected_club] === "undefined"
                    || typeof item.data[selected_club][k_date] === "undefined") {

                    data_series.push(NaN)
                }else{
                    if (k==="avg_dist"){
                        data_series.push(
                            parseInt(item.data[selected_club][k_date])
                        )
                    }else{
                        data_series.push(
                            parseInt(item.data[selected_club][k_date] * 100)  // 100 percent
                        )
                    }

                }
            });

            datasets.push({
                label: item.title,
                backgroundColor: item.color,
                borderColor: item.color,
                pointHoverBackgroundColor: item.color,
                data: data_series,

                lineTension: 0,
                fill: false,
                pointBorderWidth: 1,
                pointHoverRadius: 8,
                pointHoverBorderWidth: 2,
                pointRadius: 4,
                pointHitRadius: 6,
                spanGaps: true
            });
        });

        var data = {
            labels: club_date_range,
            datasets: datasets
        };

        // Chart declaration:
        return new Chart($("#club-chart-line-1").get(0).getContext("2d"), {
          type: 'line',
          data: data,
          options: {
            tooltips: {
              mode: 'index',
              intersect: false,
              callbacks: {
                  label: function(tooltipItem, data) {
                      var label = data.datasets[tooltipItem.datasetIndex].label + ": " + tooltipItem.yLabel;

                      if (tooltipItem.datasetIndex===0){
                          label += " yrds"
                      }else{
                          label += " %"
                      }
                      return label;
                  }
              }
            },
            // scales: {
                // yAxes: [{
                    // display: true,
                    // ticks: {
                    //     beginAtZero: true,
                    //     stepSize: 10,
                    //     max: 110
                    // },
                    // scaleLabel: {
                    //      display: true,
                    //      labelString: 'Accuracy (%)'
                    // }
                // }]
            // }
          }
        });
    }

    function renderPuttingChart(){
        $putting_chart.html("").html("<canvas id=\"putting-chart-line-1\"></canvas>");
        var selected_acc = $putting_select.val(),
            datasets = [], data_series=[];

        $.each(feet_range, function (k, feet) {
            var color = put_color_list[k%7];
            data_series = [];
            $.each(put_date_range, function (i, k_date) {
                if ( $.isEmptyObject(put_chart_lines[selected_acc])
                    || typeof put_chart_lines[selected_acc][feet] === "undefined"
                    || typeof put_chart_lines[selected_acc][feet][k_date] === "undefined") {

                    data_series.push(NaN)
                }else{
                    data_series.push(
                        parseInt(put_chart_lines[selected_acc][feet][k_date] * 100)  // 100 percent
                    )
                }
            });

            datasets.push({
                label: feet + " feet",
                backgroundColor: color,
                borderColor: color,
                pointHoverBackgroundColor: color,
                data: data_series,

                lineTension: 0,
                fill: false,
                pointBorderWidth: 1,
                pointHoverRadius: 8,
                pointHoverBorderWidth: 2,
                pointRadius: 4,
                pointHitRadius: 6,
                spanGaps: true
            });
        });

        var data = {
            labels: put_date_range,
            datasets: datasets
        };

        // Chart declaration:
        return new Chart($("#putting-chart-line-1").get(0).getContext("2d"), {
          type: 'line',
          data: data,
          options: {
            tooltips: {
              mode: 'index',
              intersect: false,
              callbacks: {
                  label: function(tooltipItem, data) {
                      return data.datasets[tooltipItem.datasetIndex].label + ": " + tooltipItem.yLabel + " %";
                  }
              }
            }
          }
        });

    }

    function renderDailyActivity(){
        $("[data-prgbar]").html("");
        $("#daily_chart_wrapper").html("").html("<canvas id=\"chart-bar-1\"></canvas>");
        $("#daily_club_info").html("");

        if (typeof($.progressbar) == "function") {
            $.progressbar();
        }

        if (typeof($.fn.chartBar) == "function") {
          // bar chart
          $("#chart-bar-1").chartBar({
            labels: daily_chart_labels,
            datasets: [
                {
                  label: "Shots",
                  data: daily_shot_data
                }
            ]
          });
        }

        $("#daily-long-count").text(daily_long_count);
        $("#daily-short-count").text(daily_short_count);
        $("#daily-putting-count").text(daily_putting_count);
        $("#daily-long-dist").text(daily_long_dist + "yds");

        if (daily_club_info === null){
            $("#daily_club_info").html("No club data");
        }else{
            var club_text = '';
            $.each(daily_club_info, function (club, item) {
                if (!club){
                    club = "Unknown";
                }
                club_text += "<div><strong>" + club + ":</strong> <span>" + item.sum + "</span> hits/<span>" + item.count + "</span> shots</div>";
            });
            $("#daily_club_info").html(club_text);
        }
    }

	// date range picker
    // -----------------------
    var start = moment().subtract(29, 'days');
    var end = moment();

    function cb(start, end) {
        // show daterange
        $('#reportrange span').html(start.format('MMM D, YYYY') + ' - ' + end.format('MMM D, YYYY'));

        // ajax post
        $.ajax({
            url:  '/filter_by_daterange/',
            type: 'POST',
            data: {
                'start': start.format('MM/DD/YYYY'),
                'end': end.format('MM/DD/YYYY'),
                'tz_offset': tz_offset,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function (r) {
                console.log("response-----------\n", r);

                if (r.success){
                    club_date_range = r.club_date_range;

                    club_chart_lines['hit_acc']['data'] = r.hit_acc;
                    club_chart_lines['avg_dist']['data'] = r.avg_dist;

                    club_chart_lines['draw_acc']['data'] = r.aim_acc['Draw'];
                    club_chart_lines['fade_acc']['data'] = r.aim_acc['Fade'];
                    club_chart_lines['straight_acc']['data'] = r.aim_acc['Straight'];

                    club_chart_lines['low_acc']['data'] = r.traj_acc['Low'];
                    club_chart_lines['high_acc']['data'] = r.traj_acc['High'];

                    put_date_range = r.put_date_range;
                    feet_range = r.feet_range;

                    put_chart_lines = {
                        'acc': r.put_hit,
                        'left': r.put_left,
                        'right': r.put_right,
                        'short': r.put_short,
                        'long': r.put_long
                    };

                }else{
                    initialize_club_data();
                    initialize_putting_data();
                }
                renderClubChart();
                renderPuttingChart();
            },
            error: function (r) {
                console.log(r);
            }
        });
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
           'Today': [moment(), moment()],
           'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
           'Last 7 Days': [moment().subtract(6, 'days'), moment()],
           'Last 30 Days': [moment().subtract(29, 'days'), moment()],
           'This Month': [moment().startOf('month'), moment().endOf('month')],
           'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, cb);


    // single date picker
    // -----------------------
    $("#single_date_picker").daterangepicker({
        singleDatePicker: true,
        showDropDowns: true,
        minYear: 2018,
        maxYear: parseInt(moment().format('YYYY'), 10)
        }, function(date){
            getDailyActivity(date)
        }
    );

    function getDailyActivity(singleDate) {
        if (!$('#single_date_picker span').length){
            return false;
        }

        $('#single_date_picker span').html(singleDate.format('MMM D, YYYY'));

        // ajax post
        $.ajax({
            url:  '/get_daily_activity/',
            type: 'POST',
            data: {
                'date': singleDate.format('MM/DD/YYYY'),
                'tz_offset': tz_offset,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function (r) {
                daily_chart_labels = [];
                daily_shot_data = [];

                console.log(r);

                // parse response
                if (r.success){
                    var daily_activity = r.daily_activity;

                    $.each(daily_activity.data_by_hour.data, function (i, item) {
                        daily_shot_data.push(parseInt(item[SHOTS_INDEX]));
                    });

                    $.each(daily_activity.data_by_hour.index, function (i, item) {
                        if (item < 12){
                            daily_chart_labels.push(item + ' AM');
                        }else{
                            daily_chart_labels.push(item + ' PM');
                        }

                    });

                    $(".prg_daily_overall").data("val", daily_activity.overall_accuracy);
                    if (daily_activity.best_club.accuracy > 0){
                        $(".prg_daily_bestclub").data("val", daily_activity.best_club.accuracy).data("best-club", daily_activity.best_club.name);
                    }
                    daily_long_count = daily_activity.practice_info.long;
                    daily_short_count = daily_activity.practice_info.short;
                    daily_putting_count = daily_activity.practice_info.putting;
                    daily_long_dist = daily_activity.max_dist;
                    daily_club_info = daily_activity.data_by_club
                }else{
                    initialize_daily_data();
                }

                renderDailyActivity();

            },
            error: function (r) {
                console.log(r);
            }
        });
    }

    $club_select.on("change", function () {
        renderClubChart();
    });

    $putting_select.on("change", function () {
        renderPuttingChart();
    });


    // send initial request

    if ( $("#reportrange").length ){
        cb(start, end);
        getDailyActivity(moment());
    }
});