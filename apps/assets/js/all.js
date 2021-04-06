// validate
// -------------------
const global_form_validator = {
    rules: {
        email: {
            required: true,
            email: true
        }
    },
    messages: {
        email: "Please enter a valid email address"
    },
    errorElement: "em",
    errorPlacement: function (error, element) {
        // Add the `help-block` class to the error element
        error.addClass("help-block");

        if (element.prop("type") === "checkbox") {
            error.insertAfter(element.parent("label"));
        } else {
            error.insertAfter(element);
        }
    },
    highlight: function (element, errorClass, validClass) {
        $(element).parents(".form-group").addClass("has-error").removeClass("has-success");
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).parents(".form-group").addClass("has-success").removeClass("has-error");
    }
};

$(document).ready(function () {

    // bootstrap date input
    // --------------------
    $('.date-input').datepicker({
        format: 'mm/dd/yyyy'
    });

    // profile script
    // --------------------
    $(".btn-switch-to-form").on("click", function () {
        $(".review-wrapper").hide();
        $(".update-form-wrapper").show();
    });

    $(".btn-profile-cancel").on("click", function () {
        $(".review-wrapper").show();
        $(".update-form-wrapper").hide();
    });

});

// club chart color settings
const CLUB_CHART_INFO = {

};