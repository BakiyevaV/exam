const pathArray = window.location.pathname.split('/');
console.log(pathArray);
const pk = pathArray[pathArray.length - 2];
console.log(pk);
let is_confirmed = false
clearAlerts()

getContent()

function getContent() {
    let container = ""
    container =
        `<div class="license_agreement">
            <p>Мы рады, что Вы присоединились к нам!</p>
            <p>Для продолжения работы на сайте, рекомендуем ознакомиться с правилами поведения и взаимодействия между пользователями</p>
            <button class="btn btn-outline-success" onclick="get_rules()">Ознакомиться с правилами</button>
            <div class="flex-row-center full-width">
                <input type="checkbox" class="form-check-input" id="agree" value="ok">
                <label class="form-check-label" for="agree">Ознакомился и согласен с правилами</label>
            </div>
            <div class="error_area"></div>
            <button class="btn btn-secondary" onclick="getAgreement()">Подтвердить</button>
        </div>`
    let main = document.querySelector('main')
    if (main) {
    main.innerHTML = container
    }
}

async function get_rules(){
    downloadPDF()
}
async function confirm(pk) {
    const url = domain + `user/api/confirm/${pk}/`;
    console.log(url)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    try{
        const response = await fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'include'
        })
        const data = await response.json();
        if (!response.ok) {
            throw new Error('Ошибка при обновлении токена: ' + response.statusText);
        }
        console.log(data)
    } catch (error) {
        console.error('Error refreshing token:', error);
        throw error;
    }
}
function downloadPDF(token) {
    const url = domain + 'user/api/download-pdf/';

    fetch(url, {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) return response.blob();
        throw new Error('Не удалось загрузить PDF');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'rules.pdf');  // Сохраняем файл как 'rules.pdf'
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);  // Освобождаем URL
    })
    .catch(error => console.error('Ошибка:', error));
}

async function refreshToken(refreshToken) {
    try {
        const url = domain + 'user/api/token/refresh/';
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error('Ошибка при обновлении токена: ' + response.statusText);
        }

        return data.access;
    } catch (error) {
        console.error('Error refreshing token:', error);
        throw error;
    }
}



async function getAgreement(){
    await confirm(pk)
    if (document.getElementById('agree').checked){
        console.log(document.getElementById('agree').value)
        let myModal = new bootstrap.Modal(document.getElementById('authorization'), {
          keyboard: false
        });
        myModal.show();
    } else {
        document.querySelector('.error_area').innerText = "Согласие не получено"
    }
}