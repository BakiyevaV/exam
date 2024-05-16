var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

let username
clearAlerts()

let subscription = document.querySelector('.subscribe')
let ignor  = document.querySelector('.ignor')
console.log(subscription)
console.log(ignor)
if (subscription) {
    if (subscription.querySelector('a').innerHTML == 'Подписаться') {
        console.log('Подписаться')
        subscription.setAttribute('onclick', 'Subscribe(this)');
    } else {
        console.log('Отписаться', subscription.innerHTML)
      subscription.setAttribute('onclick', 'CancelSubscribe(this)');
    }
}

if (ignor) {
    if (ignor.querySelector('a').innerHTML == 'Игнорировать') {
        ignor.setAttribute('onclick', 'Ignore(this)');
    } else {
        ignor.setAttribute('onclick', 'CancelIgnor(this)');
    }
}



const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
const appendAlert = (message, type) => {
  const wrapper = document.createElement('div')
  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('')

  alertPlaceholder.append(wrapper)
}

const alertPlaceholderReg = document.getElementById('liveAlertPlaceholderReg')
const appendAlertReg = (message, type) => {
  const wrapper = document.createElement('div')
  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('')

  alertPlaceholderReg.append(wrapper)
}

async function authorization(){
    const login = document.getElementById('InputLogin').value
    const password = document.getElementById('InputPassword').value
    const mem = document.getElementById('memorize').value
    if (login != "" && password != ""){
        let stat = await getUserData(login, password)
        console.log(stat)
        if (stat){
            if(stat === 'notConfirmed'){
                appendAlert('Пользователь не закончил регистрацию!',  'danger')
            } else {
                const data = await logIn(login, password)
                if (data) {
                    let myModal = document.getElementById('authorization');
                    myModal.classList.remove('show')
                    console.log(password, login)
                    console.log(document.getElementById('auth_form'))
                    document.getElementById('auth_form').submit()
                }
            }
        } else {
            appendAlert('Пользователь с такими логином и паролем не найден!',  'danger')
        }
    }
}

async function auth(login, password){
    const url = domain + 'user/api/authenticate/';
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: login,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data.success)
        
        return data.success;
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
    

}
function register(){
    const login = document.getElementById('InputLoginReg').value
    const email = document.getElementById('InputEmailReg').value
    const password = document.getElementById('InputPasswordReg').value
    const second_password = document.getElementById('InputPasswordDouble').value
    const birth_date = document.getElementById('InputBirthDate').value
    const mem = document.getElementById('memorizeReg').value
    clearAlerts();
    if (login == "" || email == "" || password == "" || second_password == "" || birth_date == "") {
        appendAlertReg('Не все поля заполнены!', 'danger')
    } else {
        if (password !== second_password) {
            appendAlertReg('Введенные пароли не совпадают', 'danger')
        } else {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const url = domain + 'user/api/register/'
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                body: JSON.stringify({
                    user: {
                        username: login,
                        password: password,
                        email: email
                    },
                    birthdate: birth_date
                })
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(obj => {
                if (obj.status === 200 || obj.status === 201) {
                    console.log('Регистрация успешна', obj.body);
                    appendAlertReg('На указанный вами адрес электронной почты было направлено письмо с подтверждением регистрации', 'success')
                    // Перенаправление пользователя или обновление интерфейса
                } else if (obj.status === 400) {
                    if (obj.body.user != undefined){
                        if (Array.isArray(obj.body.user)){
                            if (obj.body.user.email != undefined){
                            appendAlertReg(obj.body.user.email[0], 'danger')
                            }
                            if (obj.body.user.username != undefined){
                                appendAlertReg(obj.body.user.username[0], 'danger')
                            }
                            if (obj.body.user.password != undefined){
                                appendAlertReg(obj.body.user.password[0], 'danger')
                            }
                        } else {
                            if (obj.body.user.email != undefined){
                            appendAlertReg(obj.body.user.email, 'danger')
                            }
                            if (obj.body.user.username != undefined){
                                appendAlertReg(obj.body.user.username, 'danger')
                            }
                            if (obj.body.user.password != undefined){
                                appendAlertReg(obj.body.user.password, 'danger')
                            }
                        
                        }
                    }
                    if(obj.body.birthdate != undefined){
                        appendAlertReg(obj.body.birthdate, 'danger')
                    }
                }
            })
            .catch((error) => {
                console.error('Ошибка:', error);
            });
        }
    }
}

async function logIn(username, password) {
    console.log(username, password)
    const url = domain + 'user/api/token/';
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Access Token:', data.access);
        console.log('Refresh Token:', data.refresh);
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);

        return data;
    } catch (error) {
        return false
    }
}

async function getUserData(username, password){
    const url = domain + `user/api/getUserData/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log(domain)
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.data == 'False'){
            console.log(data.data)
            return "notConfirmed";
        }
        return true;
    } catch (error) {
        return false
    }
}

async function Subscribe(element){
    console.log('Подписываемся')
    const user_id = element.getAttribute('data-user_id')
    const author_id = element.getAttribute('data-aut_id')
    const url = domain + `api/subscriptions/create/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const requestBody = JSON.stringify({
        user: user_id,
        informator: author_id
    });
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: requestBody
    }).then(response => response.json())
      .then(data => {
          console.log(document.querySelector('.ignor'))
          if (!data.error){
              element.querySelector('a').innerHTML = `Отписаться`
              element.removeAttribute('onclick', 'Subscribe(this)')
              element.setAttribute('onclick', 'CancelSubscribe(this)');
              console.log(element)
              if (ignor) {
                  console.log('ignore',ignor)
                  ignor.setAttribute('hidden', 'True')
              }
          }
      })
      .catch(error => console.error('Error CancelSubscribe:', error));

}

async function Ignore(element){
    console.log('Игнорим')
    const user_id = element.getAttribute('data-user_id')
    const author_id = element.getAttribute('data-aut_id')
    const url = domain + `api/ignore/create/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const requestBody = JSON.stringify({
        user: user_id,
        ignored_user: author_id
    });
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: requestBody
    }).then(response => response.json())
      .then(data => {
          if (!data.error){
              element.querySelector('a').innerHTML = `Отменить игнор`
              element.removeAttribute('onclick', 'Ignore(this)')
              element.setAttribute('onclick', 'CancelIgnor(this)');
              console.log(element)
              if(subscription){
                  console.log('subscription',subscription)
                  subscription.setAttribute('hidden', 'True')
              }
          }
      })
      .catch(error => console.error('Error updating Ignore:', error));

}

async function CancelSubscribe(element){
    console.log('Отписываемся')
    const user_id = element.getAttribute('data-user_id')
    const author_id = element.getAttribute('data-aut_id')
    const url = domain + `api/subscriptions/delete/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const requestBody = JSON.stringify({
        user: user_id,
        informator: author_id
    });
    
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: requestBody
    }).then(response => {
        if (!response.ok) throw new Error('Error in response');
        if (response.status === 204) return {};
        return response.json();
    }).then(data => {
        console.log('Subscribe deleted:', data);
        if (!data.error) {
            element.querySelector('a').innerHTML = `Подписаться`
            element.removeAttribute('onclick', 'CancelSubscribe(this)')
            element.setAttribute('onclick', 'Subscribe(this)');
            console.log(element)
            if (ignor){
                console.log('ignore',ignor)
                ignor.removeAttribute('hidden', 'True')
            }
        }
      })
      .catch(error => console.error('Error updating Subscribes:', error));

}

async function CancelIgnor(element){
    console.log('Отписываемся от игнора')
    const user_id = element.getAttribute('data-user_id')
    const author_id = element.getAttribute('data-aut_id')
    console.log(user_id, author_id)
    const url = domain + `api/ignore/delete/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const requestBody = JSON.stringify({
        user: user_id,
        ignored_user: author_id
    });
    
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: requestBody
    }).then(response => {
        if (!response.ok) throw new Error('Error in response');
        if (response.status === 204) return {};
        return response.json();
    }).then(data => {
        console.log('Subscribe deleted:', data);
        if (!data.error) {
            element.querySelector('a').innerHTML = `Игнорировать`
            element.removeAttribute('onclick', 'CancelIgnor(this)')
            element.setAttribute('onclick', 'Ignore(this)');
            console.log(element)
            if(subscription){
                console.log('subscription',subscription)
                subscription.removeAttribute('hidden', 'True')
            }
        }
      })
      .catch(error => console.error('Error CancelIgnor:', error));

}