$(document).ready(function () {
    $("#settingRoom").click(function () {
        console.log(this.parent());
        return false;
    });

    $("#btn-share-url").click(function () {
        var item = $(this).parent().parent();

        var roomA = $("#roomA").val();
        var roomQ = $("#roomQ").val();
        var url = $("#shareURL").val();

        var tempElem = document.createElement('textarea');

        tempElem.value = `[정산돼지]\n질문:${roomQ}\n답:${roomA}\n${url}`;
        document.body.appendChild(tempElem);
        tempElem.select();
        tempElem.setSelectionRange(0, 9999);

        document.execCommand("copy");
        document.body.removeChild(tempElem);
    });
});