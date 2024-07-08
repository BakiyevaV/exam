



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

console.log("details")
document.addEventListener('DOMContentLoaded', (event) => {
    // Получаем текущий URL
    const url = new URL(window.location.href);
    console.log(url)
    
    // Получаем параметры из URL
    const postId = url.pathname.split('/').filter(Boolean).pop(); // Извлекаем postId из пути URL
    const commentId = url.searchParams.get('commentId'); // Извлекаем commentId из параметров URL
    
    console.log('Post ID:', postId);
    console.log('Comment ID:', commentId);

    if (commentId) {
        const commentElement = document.querySelector(`[data-comment-id='${commentId}']`);
        console.log('commentElement:', commentElement);
        
        if (commentElement) {
            if (commentElement.classList.contains('children_comment')) {
                const parent_id = commentElement.getAttribute('data-parent')
                const parentComment = document.querySelector(`.comment[data-comment-id='${parent_id}']`);
                const dropdownLink = parentComment.querySelector('.dropdown-toggle');
                const dropdownMenu = parentComment.querySelector('.comments-menu');
                
                // Получаем позицию элемента commentElement
                const rect = dropdownLink.getBoundingClientRect();
                console.log(dropdownLink.closest('.comment_text'))
                console.log(dropdownMenu.offsetWidth)
                dropdownMenu.style.top = `${rect.bottom + window.scrollY}px`; // Устанавливаем позицию сверху
                dropdownMenu.style.left = `${rect.left + window.scrollX + (rect.width * 2 - 5)}px`; // Устанавливаем позицию слева
                
                dropdownMenu.classList.add('show');
                dropdownLink.setAttribute('aria-expanded', 'true');
                commentElement.classList.add('current-comment');
                commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                commentElement.classList.add('current-comment');
            }
            
        }
    }
    haveView()
});

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



