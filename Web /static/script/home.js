const rwrapper = document.querySelector('.register-wrapper');
const lwrapper = document.querySelector('.login-wrapper');

const rlink = document.querySelector('.register-link');
const llink = document.querySelector('.login-link');
// const btn_Login_Popup = document.querySelector('.btn_Login_Popup');
const btn_login = document.querySelector('.btn-login');
const btn_signup = document.querySelector('.btn-signup');

const iconClose = document.querySelector('.icon-close');
const ic = document.querySelector('.register-wrapper .icon-close');
// const btn_Signup_Popup = document.querySelector('.btn_Signup_Popup');

rlink.addEventListener('click', ()=>{
    rwrapper.classList.add('active-popup');
    lwrapper.classList.remove('active-popup');
})

llink.addEventListener('click', ()=>{
    lwrapper.classList.add('active-popup');
    rwrapper.classList.remove('active-popup');
})


// btn_Login_Popup.addEventListener('click', ()=>{
//     lwrapper.classList.add('active-popup');
//     rwrapper.classList.remove('active-popup');
// })

btn_login.addEventListener('click', ()=>{
    lwrapper.classList.add('active-popup');
    rwrapper.classList.remove('active-popup');
})


iconClose.addEventListener('click', ()=>{
    lwrapper.classList.remove('active-popup');
})

ic.addEventListener('click', ()=>{
    rwrapper.classList.remove('active-popup');
})

// btn_Signup_Popup.addEventListener('click', ()=>{
//     lwrapper.classList.remove('active-popup');
//     rwrapper.classList.add('active-popup');
// })

btn_signup.addEventListener('click', ()=>{
    lwrapper.classList.remove('active-popup');
    rwrapper.classList.add('active-popup');
})