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

    $(".inlineEditor").click(setRoomName);
});

function setRoomName() {
    var targetSpan = $(this).parent().find("span.editTarget")
    var targetText = targetSpan.text()
    var editTempInput = document.createElement("input");
    editTempInput.type = 'text';
    editTempInput.id = 'editTempInput';
    editTempInput.value = targetText;
    $(editTempInput).css('width', '250px');
    targetSpan.after(editTempInput);
    targetSpan.remove();

    $(editTempInput).focusout(function(){
        var targetText = $(this).val();
        url = $(this).parent().find(".editTargetURL").val();
        console.log(url);

        data ={
            targetText:targetText
        };

        $(this).parent().parent().load(url,data,function(){
            $(".inlineEditor").click(setRoomName);
        });
    });
}