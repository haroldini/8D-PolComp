function show_more(target) {
    const div = document.getElementById(target+"-div")
    const link = document.getElementById(target+"-link")


    if(div.classList.contains("hidden")) {
        div.classList.remove("hidden")
        div.style.maxHeight = div.scrollHeight+"px"
        link.firstChild.innerText = "Show less..."
        
    } else {
        div.classList.add("hidden")
        div.style.maxHeight = "0"
        link.firstChild.innerText = "Show more..."
    }

}