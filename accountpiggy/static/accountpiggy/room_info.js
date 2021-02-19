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

    $(".settingRoom").click(function(){
        
    });
});