
export function setTyping () {
    const indicator = document.getElementById("indicator")
    indicator.style.visibility = "visible"
}

export function hideTyping() {
    const indicator = document.getElementById("indicator")
    indicator.style.visibility = "hidden"
}
