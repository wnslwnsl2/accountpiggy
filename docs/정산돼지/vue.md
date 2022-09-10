백엔드를 더 공부하려면 기본적인 프론트 페이지 구성을 할 수 있어야한다고 느낀다.

간단한 서비스를 만들면서 사용자 편의 성을 위한 클라이언트의 비동기 처리를 javascipt로 구현해보았는데, 구현해야하는 코드의 양이 적지 않았고, 이를 위해 알아야하는 것도 많았다. 선택지가 javascript 밖에 없었다면 사용했겠지만, 프론트를 구현하기 위해 트렌드를 참조하여 프론트 웹 프레임워크를 선택하기로 했다.

vue.js 선택


### Introduction
### Vue instance
### Template Syntax

v-bind: 데이터를 DOM과 연동한다.
```html
<a v-bind:href="url"> ... </a>

<a :href="url"> ... </a>
```

v-on: DOM에 이벤트를 연결한다.
```html
<a v-on:click="doSomething"> ... </a>

<a @click="doSomething"> ... </a>
```

### computed property

template에서 message를 거꾸로 출력하려면

```
<div id="example">
  {{ message.split('').reverse().join('') }}
</div>
```

template에 로직이 길게 들어가면 좋지 않다.

template 부분
```
<div id="example">
  {{ message.split('').reverse().join('') }}
</div>
```

computed property
```javascript
var vm = new Vue({
  el: '#example',
  data: {
    message: 'Hello'
  },
  computed: {
    // a computed getter
    reversedMessage: function () {
      // `this` points to the vm instance
      return this.message.split('').reverse().join('')
    }
  }
})
```

computed vs method
computed는 cache를 사용하기 때문에 computed로 구현하는 것이 좋다.


### Class and Style Bindings

class 와 style을 DOM과 연결해 보자.

`<div v-bind:class="active"></div>`

위 active가 isActive boolen 변수에 따라 생기고 없어지게 한다면?

`<div v-bind:class="{active: isActive}"></div>`

가장 일반적으로 사용하는 방법
`<div v-bind:class="classObject"></div>`
```
computed:{
	classObject: function(){
    	return {
        	active: this.isActive
        }
    }
}
```

### Conditional Rendering
1. v-if
2. Conditional Groups with v-if on template
3. Controlling Reusable Elements with key
4. v-show
5. v-show vs v-if
>v-if is “real” conditional rendering because it ensures that event listeners and child components inside the conditional block are properly destroyed and re-created during toggles.
>
>v-if is also lazy: if the condition is false on initial render, it will not do anything - the conditional block won’t be rendered until the condition becomes true for the first time.
>
>In comparison, v-show is much simpler - the element is always rendered regardless of initial condition, with CSS-based toggling.
>
>Generally speaking, v-if has higher toggle costs while v-show has higher initial render costs. So prefer v-show if you need to toggle something very often, and prefer v-if if the condition is unlikely to change at runtime.


### List Rendering