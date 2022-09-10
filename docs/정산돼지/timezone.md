Django Timezone



datetime은 naive와 aware 두가지 종류가 있다.

naive는 timezone을 갖지 않고 date, time 으로만 이루어 진 객체

aware 는 timezone까지 포함한 객체



aware = naive + timezone



database에 datetime을 저장 할 때, datetime을 UTC 시간으로 저장하는게 좋다. (표준시 기준)

그리고 user와 소통 할 때 datetime을 localtime으로 변경하여 사용하는것이 좋다.



user가 datetime을 입력 할 때

user에게 datetime을 보여 줄 때



1)  장고  template에서 UTC datetime을 로컬타임으로 표시하는 방법은 여기를 참조: https://www.reddit.com/r/django/comments/747whr/how_to_use_template_filters_to_display_datetime/



UTC 기준 시간을 localtime 으로 바꾸는 법

timezone.localtime(UTC_base_datetime)



localtime naive datetime 을 UTC 로 바꾸는 법

timezone.make_aware(naivedatetime)