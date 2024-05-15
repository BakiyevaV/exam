

async function haveView(){
	const pk = document.getElementById('article_content').getAttribute('data-detail_id')
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const url = `${domain}/api/view/${pk}/`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
    }).then(async response => {
        const data = await response.json();
        console.log('Views updated:', data);
        if (data.message == 'true') {
            let eye = document.getElementById('view_count');
            let view_count = eye.innerHTML != "" ? parseInt(eye.innerHTML, 10) : 0;
            eye.innerHTML = view_count + 1;
            await saveView();
        }
    }).catch(error => console.error('Error updating Views:', error));
}

haveView()

async function saveView(){
	const pk = document.getElementById('article_content').getAttribute('data-detail_id')
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
    const url = `${domain}/api/view/${pk}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${token_acc}`
        },
    }).then(response => response.json())
      .then(data => {
          console.log('Views updated:', data)
      })
      .catch(error => console.error('Error updating Likes:', error));
}