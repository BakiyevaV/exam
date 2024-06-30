
function add_emoji(button) {
    event.stopPropagation();
    let articleId = button.getAttribute('data-article-id');
    let allButtons = document.querySelectorAll(`button[data-article-id='${articleId}']`);

    let isActive = Array.from(allButtons).some(btn => btn.getAttribute('data-isEmoji') === 'true' && btn !== button);
    let emotionName = button.getAttribute('name');
    let emotionId = button.getAttribute('data-emoji_id');
    let status = button.getAttribute('data-isEmoji');

    let label = button.querySelector('label[id="label-' + emotionName + '"]');
    let labelNumber = parseInt(label.innerHTML, 10);

    if (!isActive || status === 'true') {
        let data = {article: articleId, emotion_type: emotionId};
        if (status === 'false') {
            label.innerHTML = labelNumber + 1;
            button.setAttribute('data-isEmoji', 'true');
            sendEmotionUpdate(data);  // Отправляем данные на сервер
            allButtons.forEach(btn => {
                if (btn !== button && btn.getAttribute('data-isEmoji') === 'true') {
                    let btnLabel = btn.querySelector('label[id="label-' + btn.getAttribute('name') + '"]');
                    let btnLabelNumber = parseInt(btnLabel.innerHTML, 10);
                    btnLabel.innerHTML = btnLabelNumber - 1;
                    btn.setAttribute('data-isEmoji', 'false');
                }
            });
        } else {
            label.innerHTML = labelNumber - 1;
            button.setAttribute('data-isEmoji', 'false');
            sendEmotionUpdate(data);  // Отправляем данные на сервер
        }
    }
}
async function sendEmotionUpdate(data) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const url = `${domain}/api_router/emoji/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: JSON.stringify({data: [data]}),
    }).then(response => response.json())
      .then(data => console.log('Emotion updated:', data))
      .catch(error => console.error('Error updating emotion:', error));
}
function takeLike(element) {
    let articleId = element.getAttribute('data-article-id');
    let like_status = element.getAttribute('data-like');
    console.log('Article ID:', articleId);
    if (like_status === 'false'){
        console.log('like_status:', like_status);
        element.innerHTML = `<i class="fa-solid fa-heart fa-xl" style="color: #e12323;"></i>`
        element.setAttribute('data-like', 'true')
    } else if (like_status === 'true'){
        console.log('like_status:', like_status);
        element.innerHTML = `<i class="fa-regular fa-heart fa-xl" style="color: #d3d5d9;"></i>`
        element.setAttribute('data-like', 'false')
    }
    saveLike(articleId)
}

async function saveLike(pk){
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const url = `${domain}/api/like/${pk}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
    }).then(response => response.json())
      .then(data => console.log('Likes updated:', data))
      .catch(error => console.error('Error updating Likes:', error));
}


let details = document.querySelectorAll('.show_detail');
details.forEach(function(detail) {
    detail.addEventListener('click', function(event) {
       const closestDiv = this.closest('div');
            if (closestDiv) {
                const id = closestDiv.getAttribute('data-detail_id')
                console.log(id);
                detail.href = domain+`detail/${id}/`
            }
    });
});

function exit() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = domain + 'user/logout/';
}

function row_link(row){
    let id = row.getAttribute('data-my-article-id')
    window.location.href = domain + `/detail/${id}/`;
}

const settings = document.getElementById('settings')
if(settings){
    settings.addEventListener('click', openSettings)
}


function openSettings(){
    const messages =settings.getAttribute('data-massages')
    const notification =settings.getAttribute('data-notifications')
    if (!document.querySelector('.settings-menu')){
        console.log('openSettings')
        const rect = settings.getBoundingClientRect()
        let menu = document.createElement('div')
        menu.innerHTML = `  <div class="flex-row-between">
                                <label for="send_message">Отправлять письма</label>
                                <input type="checkbox" name="send_message" id="send_message">
                            </div>
                            <div class="flex-row-between">
                              <label for="send_notification">Отправлять уведомления</label>
                               <input type="checkbox" name="send_notification" id="send_notification">
                            </div>`
        menu.className = 'settings-menu'
        menu.classList.add('flex-column-center')
        
        console.log(menu.offsetWidth)
        document.querySelector('.title').appendChild(menu)
        menu.style.top  = (rect.top + window.scrollY + menu.offsetHeight / 2 + settings.offsetHeight/2) + 'px';
        menu.style.left  = (rect.left + window.scrollX - menu.offsetWidth / 2 + settings.offsetWidth) + 'px';
        
        document.getElementById('send_message').checked = messages == 'True'? true : false
        document.getElementById('send_notification').checked = notification == 'True'? true : false
        document.getElementById('send_message').addEventListener('change', function (event){updateMessageSettings(event)})
        document.getElementById('send_notification').addEventListener('change', function (event){updateMessageSettings(event)})
    } else {
        console.log('closeSettings')
        if(document.querySelector('.settings-menu').style.display == 'none'){
            document.querySelector('.settings-menu').style.display = 'block'
        } else {
            document.querySelector('.settings-menu').style.display = 'none'
        }
    }
    
}

async function updateMessageSettings(event){
    const sendMessages = document.getElementById('send_message').checked;
    const sendNotification = document.getElementById('send_notification').checked;
    const url = `${domain}/api/settings/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    
    const data = {
        send_messages: sendMessages,
        send_notification: sendNotification
    };
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
      .then(data => console.log('Settings updated:', data))
        .catch(error => console.error('Error updating settings:', error));

}

function getFullNotification(notification){

    const parent = notification.parentElement
    const message = parent.querySelector('[name="message"]')
    console.log(notification)
    console.log(message)
    message.removeAttribute('hidden')
    notification.closest(".more").setAttribute('hidden', 'True')

}
function reduceNotification(event){
     event.preventDefault()
    const message = event.target.parentElement
    message.setAttribute('hidden', 'True')
    const parent = message.parentElement
    parent.querySelector('.more').removeAttribute('hidden')

}