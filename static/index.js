
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