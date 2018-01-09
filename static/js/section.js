$(document).ready(function() {
    $(document).on('click', '.filterbtn', function() {

        var category = $('#filterothers').val();

        req = $.ajax({
            url: '/shop/filter/'+category,
            type: 'POST',
            data: {category : category}
        });
        req.done(function (data) {
            $('.card').html(data)
        })
    });
});