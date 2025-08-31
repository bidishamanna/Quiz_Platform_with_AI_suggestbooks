$(document).ready(function () {
    $('#pay-button').click(function (event) {
        event.preventDefault();

        // Disable button while processing
        const $btn = $(this);
        $btn.prop('disabled', true).text('Processing...');

        $.ajax({
            url: '/payment/create-order/',
            method: "POST",
            data: {
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (data) {
                console.log("API Response: ", data);

                const options = {
                    key: data.key,
                    amount: data.amount,
                    order_id: data.order_id,
                    currency: 'INR',
                    name: 'BuyBook Payments',
                    description: 'Payment for your order',
                    handler: function (response) {
                        $.ajax({
                            url: '/payment/verify-payment/',
                            type: 'POST',
                            data: {
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature,
                                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                            },
                            success: function (verificationResponse) {
                                if (verificationResponse.success) {
                                    alert("✅ Payment verified successfully!");
                                    window.location.href = "/payment/history/";
                                } else {
                                    alert("❌ Payment verification failed: " + verificationResponse.error);
                                    $btn.prop('disabled', false).text('Proceed to Pay');
                                }
                            },
                            error: function (error) {
                                alert("Error verifying payment.");
                                console.error(error);
                                $btn.prop('disabled', false).text('Proceed to Pay');
                            }
                        });
                    }
                };

                const rzp = new Razorpay(options);
                rzp.open();

                // Re-enable button after Razorpay closes if user cancels
                rzp.on('payment.failed', function (response) {
                    alert("❌ Payment failed or cancelled.");
                    $btn.prop('disabled', false).text('Proceed to Pay');
                });
            },
            error: function (error) {
                console.error('Order creation error:', error);
                alert('Error creating order.');
                $btn.prop('disabled', false).text('Proceed to Pay');
            }
        });
    });
});


