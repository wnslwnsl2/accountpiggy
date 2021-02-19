$(document).ready(function () {
    $("#btn-share-url").click(function () {
        var item = $(this).parent().parent();
        var roomA = $("#roomA").text();
        var roomQ = $("#roomQ").text();
        var url = $("#shareURL").val();

        var tempElem = document.createElement('textarea');
        tempElem.value = `[정산돼지]\n질문:${roomQ}\n답:${roomA}\n${url}`;
        document.body.appendChild(tempElem);
        tempElem.select();
        tempElem.setSelectionRange(0, 9999);

        document.execCommand("copy");
        document.body.removeChild(tempElem);
    });

    $(".settingRoom").click(setRoomName);
});

function setRoomName() {
    var roomNameSpan = $(this).parent().find("span.roomName")
    var roomName = roomNameSpan.text()
    var roomNameInput = document.createElement("input");
    roomNameInput.type = 'text';
    roomNameInput.id = 'roomNameInput';
    roomNameInput.value = roomName;
    $(roomNameInput).css('width', '250px');
    $(roomNameInput).focusout(function(){
        var roomName = $(this).val();
        url = $(this).parent().find("#settingRoomURL").val();
        console.log(url);

        data ={
            roomName:roomName
        };

        $.post(url,data,function(result){
            var roomNameInput = $('#roomNameInput');
            roomNameInput.after(result);
            roomNameInput.remove();
        })
    });
    roomNameSpan.after(roomNameInput);
    roomNameSpan.remove();
}