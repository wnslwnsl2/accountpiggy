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

    $(".settingRoom").click(createRoomNameInput);
});

function createRoomNameInput() {
    var roomNameSpan = $(this).parent().find("span.roomName")
    var roomName = roomNameSpan.text()
    var roomNameInput = document.createElement("input");
    roomNameInput.type = 'text';
    roomNameInput.id = 'roomNameInput';
    roomNameInput.value = roomName;
    $(roomNameInput).css('width', '250px');
    $(roomNameInput).focusout(function(){
        var roomNameSpan = document.createElement("span");
        $(roomNameSpan).addClass("roomName");
        $(roomNameSpan).text($(this).val())
        $(this).after(roomNameSpan);
        $(this).remove();
    });
    roomNameSpan.after(roomNameInput);
    roomNameSpan.remove();
}