How to set up the project:
first go to the "Login" page. There are three users: basic user, premium user and enterprise user.
To login basic user use this code:
{"username":"basic_user",
"password":"ASasDwdWADsDW1122@@"}

for premium user use this code: 
{"username":"premium_user",
"password":"ASasDwdWADsDW1122@@"}

for enterprise user use this code:
{"username":"enterprise_user",
"password":"ASasDwdWADsDW1122@@"}

and click: "POST".

To upload an image, go to "Images List" and upload an image. You can access all your images from "Images List".

If you log as enterprise user you can also choose "Create link". It's for creating temporary links.
To create a temporary link you need to provide an original link and expiration time (in seconds). For example:
{"link":"https://kd-image-api.herokuapp.com/media/your-image-name.jpg",
"expiration_time": "5000"}
In this case you gonna get a link (e.g. https://kd-image-api.herokuapp.com/temp/10-random-chars) that gonna expires in 5000 seconds

You can also login as admin here: https://kd-image-api.herokuapp.com/admin
The username is: "admin"
The password is: "admin"
 
To upload an image, go to "Image models" and then "add". You can create a custom thumbnail there:
e.g. if you set "Custom thumbnail" to 333, you gonna get an original image and a thumbnail with height 333.
If you leave it empty you only gonna get the original image.
In admin panel you can also fetch a link. To do it go to "Fetch links", "add". 
In original url just write your image's name, e.g. "your-image-name.jpg" (you can get the name in Image models).
In temporary url write your new url's name, e.g. "my-temporary-url". Also set expiration date.
The result gonna be e.g. temp/my-temporary-url. To see your image go to https://kd-image-api.herokuapp.com/temp/my-temporary-url


