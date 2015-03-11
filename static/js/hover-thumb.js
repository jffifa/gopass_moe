$(function(){
    var dataMouseTimeId = null;
    $('[data-mouseover]').on('mouseover',function(){
        if ($(this).children('[data-mouseshow]').length == 0) {
            var img = $('<img>');
            img.addClass('thumbnail');
            img.attr('data-mouseshow', '1');
            var url = $(this).attr('href');
            if (!url) {
                url = $(this).find('a').attr('href');
            }
            img.attr('src', url);
            var selft = $(this);
            dataMouseTimeId = setTimeout(function(){selft.append(img);}, 300);
        }
        return false;
    });
    $('[data-mouseover]').on('mouseout',function(){
        if (dataMouseTimeId) clearTimeout(dataMouseTimeId);
        $(this).children('[data-mouseshow]').remove();
        return false;
    });
});
