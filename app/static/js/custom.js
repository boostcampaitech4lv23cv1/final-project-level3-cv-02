function hello(){
    alert('dd')
}

function preventDefaults(e) { //브라우저 파일 드래그&드롭 기본 이벤트 막기
    e.preventDefault();
    e.stopPropagation();
}

/*드래그 인 시 하이라이팅 & 드래그 아웃 시 하이라이팅 제거*/
const dropArea = document.getElementById("drop-file");

function highlight(e) {
  preventDefaults(e);
  dropArea.classList.add("highlight");
}

function unhighlight(e) {
  preventDefaults(e);
  dropArea.classList.remove("highlight");
}

dropArea.addEventListener("dragenter", highlight, false);
dropArea.addEventListener("dragover", highlight, false);
dropArea.addEventListener("dragleave", unhighlight, false);
