const selectEl = document.getElementById("patch_select"); // 选项的值


// 解析字符串中标签
window.addEventListener('load', function () {
    let elements = document.querySelectorAll('.img-text');
    for (let i = 0; i < elements.length; i++) {
        elements[i].innerHTML = elements[i].innerText;
        // console.log(elements[i].innerHTML)
    }
});


// 当选择发生改变时，get请求的查询参数也发生改变
selectEl.addEventListener("change", function () {
    // console.log(selectEl.value)
    let currentUrl = window.location.href;
    console.log(currentUrl)
    let newUrl = currentUrl.replace(/([?&])patch_name=([^&]*)/, '$1patch_name=' + selectEl.value);
    console.log(newUrl)
    window.location.href = newUrl;
});
