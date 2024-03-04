idx = 0
names = document.querySelector("#data").innerHTML.split(" / ")[1].split(", ")

for (i of document.querySelector("#data").innerHTML.split(" / ")[0].split(", ")) {
    document.querySelector("#table").innerHTML += "<tr><td>" + (+idx+1) + "</td><td><a href='@" + names[parseInt(idx)] + "'>" + names[parseInt(idx)] + "</a></td><td>" + i + "</td></tr>"
    idx += 1
}