$(document).ready(function() {
    
    // Popup
    // Show
    $('.popup-show').on('click', function() {
        $(this).next('.popup').show();
    });
    // Hide
    $('.popup-hide, .popup').on('click', function(e) {
        e.stopPropagation();
        $(this).closest('.popup').hide();
    });

    // Audio files
    // Play/pause
    $('.audio-control').on('click', function() {
        var audioId = $(this).attr('data-id');
        var audio = $('#audio-' + audioId)
        // Play/pause audio
        if (!audio.prop('paused')) audio.trigger('pause');
        else audio.trigger('play');
    });
    // Toggle play/pause button
    $('audio').on('play', function(){
        $(this).next('span').addClass('active');
    });
    $('audio').on('pause', function(){
        $(this).next('span').removeClass('active').html('<i class="fas fa-microphone"></i>')
    });
    $('audio').trigger('pause'); // Pause on start to load the label for all audio elements

});