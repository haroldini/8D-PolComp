const sleep = ms => new Promise(r => setTimeout(r, ms));

// Add to button onclick with div as target. Div will open / close on click
function show_more(target, msg1="Show less...", msg2="Show more...", hideonly=false) {
    const div = document.getElementById(target+"-div")
    const link = document.getElementById(target+"-link")

    // SHOW MORE
    if(div.classList.contains("showmore-var")) {
        if (!hideonly) {
            div.classList.remove("showmore-var")
            div.style.maxHeight = div.scrollHeight+"px"
            div.style.height = div.scrollHeight+"px"
            link.firstChild.innerText = msg1
        }
    
    // SHOW LESS
    } else {
        div.classList.add("showmore-var")
        div.style.maxHeight = "0"
        div.style.height = "auto"
        link.firstChild.innerText = msg2
    }
}

// Converts given hexcode string to rgba string with transparency
function add_transparency(hexcode, opacity = 1){
    if (hexcode.length != 7) {
        return hexcode
    }
    var hex = hexcode.replace('#', '');

    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    var r = parseInt(hex.substring(0,2), 16),
        g = parseInt(hex.substring(2,4), 16),
        b = parseInt(hex.substring(4,6), 16);

    if (opacity > 1 && opacity <= 100) {
        opacity = opacity / 100;   
    }
    
    return 'rgba('+r+','+g+','+b+','+opacity+')';
}


function disable_button(tar, text="Downloading...") {
    tar.classList.add("disabled")
    tar.disabled = true
    tar.children[1].innerText = text
}
function enable_button(tar, text="Download Database") {
    tar.classList.remove("disabled")
    tar.disabled = false
    tar.children[1].innerText = text
}

// Give date input element today's date as input
function set_todays_date(event) {
    event.value = new Date();
}

// Scrolls to top of page
function scroll_to_top() {
    document.body.scrollTop = 0
    document.documentElement.scrollTop = 0
}

// Scrolls to a given element
function scroll_to(id) {
    document.getElementById(id).style.scrollMarginTop = "2rem"
    document.getElementById(id).scrollIntoView()
}

// Copies current url to clipboard
async function copy_link(tar, btn_text="Copy Link") {
    disable_button(tar, "Copied")
    let currentPath = new URL(window.location.href)
    navigator.clipboard.writeText(currentPath)
    .then(function () {
        setTimeout(function () {
            enable_button(tar, btn_text);
        }, 2500);
    })
}

// Saves chart from target id to device
async function save_image(tar, div_id, btn_text="Save Image") {
    disable_button(tar)
    let scale = 2;
    let domNode = document.getElementById(div_id)
    let backgroundColor = getComputedStyle(document.documentElement).getPropertyValue('--black').trim()

    domtoimage.toJpeg(domNode, {
        width: domNode.clientWidth * scale,
        height: domNode.clientHeight * scale,
        style: {
            transform: 'scale('+scale+')',
            transformOrigin: 'top left',
            backgroundColor: backgroundColor
        }
    })
    .then(function (blob) {
        enable_button(tar, btn_text)
        window.saveAs(blob, '8dpolcomp-image.jpg');
    });
}