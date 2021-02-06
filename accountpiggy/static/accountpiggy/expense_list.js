$(document).ready(function () {
    $(".expense").click(function () {
        event.preventDefault();
        var collapsed_div = $(this).parent().find(".collapsed-expense-info");

        if (collapsed_div.hasClass("d-none")) {
            collapsed_div.removeClass("d-none");
            $(this).css('borderRight', "2px solid black");
        } else {
            collapsed_div.addClass("d-none");
            $(this).css('borderRight', "none");
        }
    });
});