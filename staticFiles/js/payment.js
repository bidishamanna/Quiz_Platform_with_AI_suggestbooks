 $(document).ready(function () {
    $('#pay-button').click(function (event) {
      event.preventDefault();

      const subjectId = $('#subject_id').val();
      const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

      if (!subjectId) {
        alert("⚠️ Subject not found. Please try again.");
        return;
      }
      console.log("Pay button clicked");

      // Step 1: Create Razorpay order
      $.ajax({
        url: '/payment/create-order/',
        type: 'POST',
        data: {
          subject_id: subjectId,
          csrfmiddlewaretoken: csrfToken
        },
        success: function (data) {
          if (data.error) {
            alert("❌ " + data.error);
            return;
          }

          // Step 2: Initialize Razorpay Checkout
          const options = {
            key: data.key,
            amount: data.amount,
            currency: 'INR',
            name: 'Quiz Platform',
            description: 'Payment for ' + data.subject,
            order_id: data.order_id,
            handler: function (response) {
              // Step 3: Verify payment
              $.ajax({
                url: '/payment/verify-payment/',
                type: 'POST',
                data: {
                  razorpay_order_id: response.razorpay_order_id,
                  razorpay_payment_id: response.razorpay_payment_id,
                  razorpay_signature: response.razorpay_signature,
                  csrfmiddlewaretoken: csrfToken
                },
                success: function (verificationResponse) {
                  if (verificationResponse.success) {
                    alert("✅ Payment successful!");
                    window.location.href = '/payment/history/';
                  } else {
                    alert("❌ Verification failed: " + verificationResponse.error);
                  }
                },
                error: function () {
                  alert("⚠️ Error verifying payment.");
                }
              });
            },
            theme: {
              color: '#007bff'
            }
          };

          const rzp = new Razorpay(options);
          rzp.open();
        },
        error: function (xhr, status, error) {
          alert("⚠️ Failed to create order. Try again.");
          console.error("Create Order Error:", error);
        }
      });
    });
  });