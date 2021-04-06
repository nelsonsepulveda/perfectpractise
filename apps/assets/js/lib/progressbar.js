! function(r) {
    "use strict";
    // line
    r.fn.progressbar_line = function(a) {

        return r.prgbar_cache[a.barID] = {
            val: a.barVal,
            prgbar: new ProgressBar.Line(a.barID, {
                id: a.barID,
                val: a.barVal,
                color: a.barColor,
                trailColor: a.trailColor,
                trailWidth: a.barWidth,
                duration: 3e3,
                easing: "easeOut",
                strokeWidth: a.barWidth,
                from: {
                    color: a.barColor
                },
                to: {
                    color: a.barColor
                },
                text: {
                    autoStyleContainer: !1,
                    style: {
                        color: "rgb(218,226,232)"
                    }
                },
                svgStyle: {
                    display: "block",
                    width: "100%",
                    height: a.barWidth + "px"
                },
                step: function(r, a) {
                    var t = Math.round(100 * a.value());
                    0 === t ? a.setText("0%") : a.setText("<span>" + t + "</span>%")
                }
            })
        }, r(this)
    },

    // circle
    r.fn.progressbar_circle = function(a) {
        var t = 100 * a.barWidth / a.barSize,
            o = void 0 !== r.browser && r.browser.msie && t > 6 ? 6 : t;

        return r.prgbar_cache[a.barID] = {
            val: a.barVal,
            prgbar: new ProgressBar.Circle(a.barID, {
                id: a.barID,
                val: a.barVal,
                color: a.barColor,
                trailColor: a.trailColor,
                trailWidth: t,
                duration: 1e3,
                easing: "easeOut",
                strokeWidth: o,
                from: {
                    color: a.barColor
                },
                to: {
                    color: a.barColor
                },
                text: {
                    autoStyleContainer: !1
                },
                svgStyle: {
                    display: "block",
                    width: a.barSize + "px",
                    height: a.barSize + "px"
                },

                specific: a.barSpecific,  // custom option
                bestclub: a.barBestClub,  // custom option
                step: function(r, a) {
                    var t = Math.round(100 * a.value());

                    if(a._opts.specific === "prg_overall_accuracy"){
                        a.setText("<h4>" + t + "%</h4>" + "<span>Overall Accurancy</span>");
                    }else if(a._opts.specific === "prg_best_club"){
                        a.setText("<span>Most Accurate Club</span><h4>" + a._opts.bestclub + "</h4>" + "<span>" + t + "%</span>");
                    }else{
                        0 === t ? a.setText("0%") : a.setText("<h4>" + t + "%</h4>")
                    }

                }
            })
        }, r(this)
    },

    // options
    r.fn.progressbar_opt = function(a) {
        var t = "progressbar_line" + a;

        return r(this).attr("id", t), {
            barID: "#" + t,
            barType: r(this).data("prgbar"),
            barSize: r(this).data("size") ? parseInt(r(this).data("size")) : 160,
            barColor: r(this).data("color") ? r(this).data("color") : "#08dd0a",
            barWidth: r(this).data("width") ? parseInt(r(this).data("width")) : 8,
            barVal: r(this).data("val") ? parseFloat(r(this).data("val")) / 100 : 0,
            trailColor: r(this).data("trail") ? r(this).data("trail") : "#414141",

            barSpecific: r(this).data("specific") ? r(this).data("specific") : '',
            barBestClub: r(this).data("best-club") ? r(this).data("best-club") : ''
        }
    },

    r.progressbar = function() {
        r.prgbar_cache = new Array, r("[data-prgbar]").each(function(a) {
            var t = r(this).progressbar_opt(a);
            switch (r(this).data("prgbar")) {
                case "line":
                    r(this).progressbar_line(t);
                    break;
                case "circle":
                    r(this).progressbar_circle(t)
            }
        });
        var a = function() {
            for (var a in r.prgbar_cache) {
                // r.prgbar_cache[a].prgbar.animate(r.prgbar_cache[a].val);
                // delete r.prgbar_cache[a];
                r(window).scrollTop() + r(window).height() >= r(a).offset().top + 30 && r(window).scrollTop() <= r(a).offset().top + r(a).height() - 30 && (r.prgbar_cache[a].prgbar.animate(r.prgbar_cache[a].val), delete r.prgbar_cache[a])
            }
        };
        a(), r(window).on("scroll", function() {
            a()
        })
    }
}(jQuery);