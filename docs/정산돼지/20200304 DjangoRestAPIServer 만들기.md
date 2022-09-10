# Django Rest API Server 만들기

## url 구조

api server를 만들기 전에 내가 구현해야하는 api 구조와, 이 api 구조를 만들기 위해서 프로젝트 폴더를 어떻게 구성해야하는지 알아보았다.



우선 구현 해야하는 최적의 api구조라기 보단, 사람들이 보통 api를 어떻게 구현하는지, 그리고 어떻게 하는것이 지금으로서 나에게 가장 직관적으로 와닿는지 생각해보기로 하였다.



room이라는 모델에 대해 api를 사용하는 가장 직관적인 api는 `/rooms/` 다.

router를 사용하지 않을 때

1) 메인앱에서 rooms/ url request가 들어오면 > room url로 넘긴다.

2) room 앱의 url.py에서는 빈 공백('')으로 url request를 받는다.



router를 사용할 때

1) 메인앱에서 room.viewset을 router에 등록한다.

2) rooms를 router에 등록한다.



#### 프로젝트 폴더 구조

는 아래와 같이 작성하였다.

```
├── accountpiggy (메인 앱)

├── expenses (앱)

├── matrix (앱)

​	├── expense_matrix_cleaner (모듈)

├── rooms (앱)

└── users (앱)
```





## django restapi auth (회원가입/로그인 기능)

#### Django-rest-auth 셋팅

- Django-rest-auth 와 all-auth 페이지를 보면서 설정한다.

https://django-rest-auth.readthedocs.io/en/latest/installation.html

https://django-allauth.readthedocs.io/en/latest/installation.html



- Django all-auth migrate bug fix

https://stackoverflow.com/questions/35388637/runtimeerror-model-class-django-contrib-sites-models-site-doesnt-declare-an-ex



#### Custom User 사용하기

abstactbaseUser 쓰는건 이전과 똑같음

https://krakensystems.co/blog/2020/custom-users-using-django-rest-framework



## Room Rest API 설정하기



### serializer

```python
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'start_date', 'end_date', 'created']
```



### views

```python
@api_view(['GET', 'POST'])
def room_list(request):
    """
    List all rooms, or create a new room
    """
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def room_detail(request, pk):
    """
    Retrieve, update or delete a room
    """
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```



### room 생성과 동시에 생성될 객체를 생성 > Signals 이용

https://dgkim5360.tistory.com/entry/django-signal-example





# 0305 Restapi 적용 기본적인 부분 모두 적용하자



### 구현

Matrix

user : rest-auth



### 정리

- rest-auth 사용하는 것
- Rest-api 사용하는 것 처음부터 끝까지 일련의 과정
- Signals



Room과 Room 입장비밀번호



#### 1) Rest_Framework 환경설정

#### 2) serializers.py 작성

```python
from rest_framework import serializers
from .model import Room

class RoomSerializers(serializers.Model):
  	class Meta:
      model = Room
      fields = ['id','name','start_data','end_date','created']
```



#### 3) view 작성

```python
from .models import Room
from .serializers import RoomSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET','POST'])
def room_list(request):
  if request.method == 'GET':
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many = True)
    return Response(serializer.data)

  elif request.method == 'POST':
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
  
@api_view(['GET','PUT','DELETE'])
def room_detail(request,pk):
	try:
    room = Room.objects.get(pk = pk)
  except Room.DoesNotExist:
    return Response(status.status.HTTP_400_BAD_REQUEST)
  
  if request.method == 'GET':
    serializer = RoomSerializer(room)
    return Response(serializer.data)
  
  elif request.method == 'PUT':
    serializer = RoomSerializer(room,data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
  
  elif request.method == 'DELETE':
    room.delete()
    return Response(status.HTTP_204_NO_CONTENT)
    
```



#### 4) url 설정





### Signals를 사용하여 외래키 모델 생성

apps를 작성한다.

```python
from django.apps import AppConfig

class RoomsConfig(AppConfig):
  name = 'rooms'
  
  def ready(self):
    import sample.signals # noqa F401
```





signals.py 를 작성한다.

```python
from django.dispatch import receiver
from .model import Room

@receiver(post_save,sender=Room)
def room_post_save(sender,**kwargs):
  room = kwargs['instance']
  EnteringQA.objects.create(room=room)
```



ini을 작성한다.

```
default_app_config = 'rooms.apps.RoomsConfig'
```