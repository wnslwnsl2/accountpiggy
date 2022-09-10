#### NoReverseMatch       at /16/**room_input_expense**

이거 context에 room 안넣어 줘서 그럼



#### {% url 'nbbanggogoapp:room_input_expense' room.id%}

{% url'nbban < 이렇게 붙이면 에러남



#### if request.method=='POST':

if request.method=='post': < 이렇게 하면 인식 안됨





### 하나의 모델에서 같은 모델에 대해 두개의 FK를 설정할 때

ex) transfer_item > sending_user, receiving_user

user.transfer_item_set() 으로 접근 했을 때 무엇을 보여줘야 하는 지 모른다.

(해결) related_name을 설정해 주면

user.sending_items

user.recving_items 이렇게 사용해서 받을 수 있다.

```
nbbanggogoapp.transfer_item.receiving_user: (fields.E304) Reverse accessor for 'transfer_item.receiving_user' clashes with reverse accessor for 'transfer_item.sending_user'.
        HINT: Add or change a related_name argument to the definition for 'transfer_item.receiving_user' or 'transfer_item.sending_user'.
```

