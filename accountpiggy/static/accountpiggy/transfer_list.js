function setTransferButtonCss(){
    var send_buttons = $(".button_send")
    var recv_buttons = $(".button_recv")

    var i = 0;
    for(i=0;i<send_buttons.length;i++){
        var sendbutton = send_buttons[i];
        if ($(sendbutton).hasClass('state0')){
            $(sendbutton).css('background-color','white');
            $(sendbutton).text('보냈다.');
        }else if($(sendbutton).hasClass('state1')){
            $(sendbutton).css('background-color','gray');
            $(sendbutton).prop('disabled',true);
            $(sendbutton).text('확인중');
        }else if($(sendbutton).hasClass('state2')){
            $(sendbutton).css('background-color','red');
            $(sendbutton).text('다시봐봐');
        }else{
            $(sendbutton).css('background-color','grays');
            $(sendbutton).text('완료');
        }
    }

    for(i=0;i<recv_buttons.length;i++){
        var recvbutton = recv_buttons[i];
        if ($(recvbutton).hasClass('state0')){
            $(recvbutton).css('background-color','white');
            $(recvbutton).text('받았다.');
        }else if($(recvbutton).hasClass('state1')){
            $(recvbutton).css('background-color','green');
            $(recvbutton).text('받았다.');
        }else if($(recvbutton).hasClass('state2')){
            $(recvbutton).css('background-color','green');
            $(recvbutton).text('받았다.');
        }else{
            $(recvbutton).css('background-color','gray');
            $(recvbutton).text('완료');
        }
    }
}

$(document).ready(function(){
    setTransferButtonCss();

    $('.button_recv').click(function () {
        var div = $(this).parent();
        var entry_id = div.find('input')[0].value;

        var data = {
            entry_id:entry_id
        };
        var url = $(this).attr('href');
        $.ajax({
            type:'POST',
            url:url,
            data:data,
            success: function(state){
                console.log(state)
            },
            dataType:'ints'
        });
        return false;
    });

    $('.button_send').click(function () {
        var div = $(this).parent();
        var entry_id = div.find('input')[0].value;
        console.log(entry_id);

        var data = {
            entry_id:entry_id,
        };

        var url = $(this).attr('href');
        $.ajax({
            type:'POST',
            url:url,
            data:data,
            success: function(state){
                console.log(state)
            },
            dataType:'ints'
        });
        return false;
    });
});