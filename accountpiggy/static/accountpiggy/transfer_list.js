function recvAction() {
    var reloaddiv = $(this).parent().parent().parent();
    var entry_id = $(this).parent().find('input')[0].value;
    var url = $(this).attr('href');
    // console.log(entry_id);

    var data = {
        entry_id: entry_id,
        buttontype: "recevier_0"
    };
    reloaddiv.load(url, data, function () {
        $('.button_recv').click(recvAction);
        $('.button_send').click(sendAction);
    });
    return false;
}

function sendAction() {
    var reloaddiv = $(this).parent().parent().parent();
    var entry_id = $(this).parent().find('input')[0].value;
    // console.log(entry_id);

    var url = $(this).attr('href');
    var data = {
        entry_id: entry_id,
        buttontype: "sender_0"
    };

    reloaddiv.load(url, data, function () {
        $('.button_recv').click(recvAction);
        $('.button_send').click(sendAction);
    });
    return false;
}

$(document).ready(function () {
    $('.button_recv').click(recvAction);
    $('.button_send').click(sendAction);
});