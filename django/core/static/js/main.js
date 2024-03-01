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

    // Filter select lists
    // "Owned By" and "Collaborators" lists to hide students and guests
    $('#id_owned_by option, #id_collaborators option').each(function(){
        if ($(this).text().includes('(student)') || $(this).text().includes('(guest)')) $(this).remove();
    });

});