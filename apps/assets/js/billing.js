$(document).ready(function () {
    var $billForm = $("form[id='billingForm']");
    var $stripe_errors = $("#id_cc_errors");
    var $btn_pay = $(".btn-pay");
    var $input_stripe_token = $("input[name='stripe_token']");

    $stripe_errors.hide();

    // post bill form
    var postBillingData = function ($form) {

        $btn_pay.prop("disabled", true);

        // --- get billing info
        var billing = {};
        billing.first_name = $("#id_first_name").val();
        billing.last_name = $("#id_last_name").val();
        billing.name = [billing.first_name, billing.last_name].join(" ");
        billing.email = $("#id_email").val();

        billing.address_line1 = $("#id_address_line1").val();
        billing.address_line2 = $("#id_address_line2").val();
        billing.address_city = $("#id_city").val();
        billing.address_state = $("#id_state").val();
        billing.address_zip = $("#id_postcode").val();
        billing.address_country = $("#id_country").val();
        billing.currency = "usd";

        // --- create Stripe token
        stripe.createToken(card_number, billing).then(function (result) {
            if (result.error) {

                $stripe_errors.show();
                $stripe_errors.find("p").text(result.error.message);
                $btn_pay.prop("disabled", false);

            } else {
                console.log(result, "----------------");

                $stripe_errors.hide();
                $stripe_errors.find("p").text("");
                $input_stripe_token.val(result.token.id);

                $form.submit();
            }
        });
    };

    // form submit
    $billForm.validate(global_form_validator);

    $btn_pay.on("click", function (e) {
        e.preventDefault();

        if($billForm.valid()){
            postBillingData($billForm);
        }

        return false
    })


});


