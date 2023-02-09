
// sign up
function signUp(e) {
    debugger;
    const user_password = document.getElementById('user_password');
    const password_check = document.getElementById('password_check');

    if (user_password.value !== password_check.value) {
        alert('패스워드 및 확인 패스워드가 일치하지 않습니다.');
        return false;
    }
    else {
        document.form_ex.submit();
    }
}

//check password
function checkpw(){
    debugger;
    const userEmail = document.getElementById('signin_user_email').value;
    const userPassword = document.getElementById('signin_user_password').value;
    if(userEmail==''){
        alert('이메일을 입력해주세요.');
        return false;
      }

      if(userPassword==''){
        alert('패스워드를 입력해주세요.');
        return false;
      }

    fetch('/users/checkpw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: userEmail, user_password: userPassword }),
        user_email : userEmail,
        user_password: userPassword
      })
        .then((response) => response.json())
        .then((data) => {
            debugger;
          if (data) {
            document.form_ex.submit();
          } else {
            alert('패스워드가 일치하지 않습니다.');
            return false;
          }
        });
}