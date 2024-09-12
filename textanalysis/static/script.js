$(document).ready(function() {
    $('#upload-form').on('submit', function(e) {
        e.preventDefault();
        
        $('#please-wait').show(); // Show the "Please wait" message

        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: '{% url "upload_image" %}',  // Keep the upload URL
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                $('#please-wait').hide(); // Hide the "Please wait" message
                
                if (response.error) {
                    alert(response.error);
                } else {
                    // Redirect to the extracted_text page
                    window.location.href = '{% url "extracted_text" %}';
                }
            },
            error: function(xhr, status, error) {
                $('#please-wait').hide(); // Hide the "Please wait" message on error
                console.log(xhr.responseText);
                alert('An error occurred. Please try again.');
            }
        });
    });
});
