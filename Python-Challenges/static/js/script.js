function login() {
    location.href = "https://github.com/login/oauth/authorize?client_id=a1e884efc8b5b30c4cc3&scope=read:user"
}

for (i of document.querySelector("#data").innerHTML.split("\n")) {
    row = i.split("	")
    document.querySelector("#table").innerHTML += "<tr><td>" + row[0] + "</td><td>" + row[2] + "</td><td>" + row[1] + "</td><td><a href='" + row[4] + "'>Link</a></td></tr>"
}