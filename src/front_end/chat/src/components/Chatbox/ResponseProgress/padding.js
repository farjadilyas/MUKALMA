function getOffset(el) {
    const rect = el.getBoundingClientRect();
    return {
        left: rect.left + window.scrollX,
        top: rect.top + window.scrollY
    };
}

export const updatePadding = (state) => {

    // We first fetch the relevant elements
    var endOfChat = document.getElementById("end-of-chat");
    var progressContainer = document.getElementsByClassName("progress-container")[0];
    var inputGroup = document.getElementsByClassName("input-group")[0]

    // If there is no element of progressContainer we skip
    if (!progressContainer || !state) {
        endOfChat.style.paddingBottom = "50px"
        return
    }

    // Getting the Y values
    var topEndOfChat = getOffset(endOfChat).top
    var topInputGroup = getOffset(inputGroup).top

    // Calculating the difference and checking against height
    var height = topInputGroup - topEndOfChat

    // Setting margin according to the height
    if (height >= 0) {
        endOfChat.style.paddingBottom = "0px"
        progressContainer.style.marginTop = height.toString().concat("px");
    } else {
        progressContainer.style.marginTop = "0px";
        endOfChat.style.paddingBottom = "20px"
    }
}
