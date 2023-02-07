$(document).ready(function() {
    
    // Popup
    // Show
    $('.popup-show').on('click', function() {
        $(this).next('.popup').show();
    });
    // Hide
    $('.popup-hide').on('click', function(e) {
        e.stopPropagation();
        $(this).closest('.popup').hide();
    });

});