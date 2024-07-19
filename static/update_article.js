var url = window.location.href;
var parts = url.split('/');
var id = parts[parts.length - 2]
id = parseInt(id, 10);
console.log(id);


CKEDITOR.replace('id_content');
let image_array = []
let deleted_image_array = []
clearAlerts()

let tags_array = []
const add_tag = document.getElementById('add_tag')
let tags_line = document.getElementById('tags_line')
let customModal = document.getElementById('customModal')
const cancel_button = document.getElementById('cancel')
const update_button = document.getElementById('update')
const delete_button = document.getElementById('delete')
add_tag.addEventListener('click', addTags)
cancel_button.addEventListener('click', cancelAction)
delete_button.addEventListener('click', async function(){deleteArticle()} )

document.querySelectorAll('.tag-wrapper').forEach(tag_wrapper => {
        let tag_span = tag_wrapper.querySelector('span').textContent.replace('#', '')
        tags_array.push(tag_span)
    }
)
console.log(tags_array)

document.querySelectorAll('.fa-xmark').forEach(xmark => {
    xmark.addEventListener('click', function (event){
        let parent = xmark.parentElement;
        let tag_text = parent.querySelector('span').textContent.replace('#', '');
        let index = tags_array.indexOf(tag_text);
        if (index !== -1) {
            tags_array.splice(index, 1);
        }
        
        parent.remove();
    })
})
document.addEventListener("DOMContentLoaded", function() {
    let imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.removeAttribute('required');
    }
});

function cancelAction() {
    document.querySelector('form').reset();
    window.history.back();
}

function addTags(){
    let tag_area = document.getElementById('tag_area')
    let tag = tag_area.value
    tag_area.value = ""
    if (tag != "") {
        const foundTag = tags_array.find(element => element === tag)
        if (foundTag !== undefined) {
            console.log("Тег уже существует в массиве");
        } else {
            console.log("Тега нет в массиве, добавление тега");
            tags_array.push(tag);
            console.log(tags_array)
            tag_container = document.createElement('div')
            tag_container.className = "tag-wrapper"
            let tag_p = document.createElement('span')
            tag_p.textContent = `#${tag}`
            tag_p.className = "tag_text"
            let icon = document.createElement('i');
            icon.className = "fa-solid fa-xmark";
            icon.style.color = "#cfd0d3";
            tag_container.appendChild(tag_p);
            tag_container.appendChild(icon);
            tags_line.appendChild(tag_container)
        }
    }
}

async function deleteArticle(){
    try {
        const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
        const response = await fetch(domain + `/api/create_article/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token_acc}`
            }
        });
        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(`Failed to delete article: ${errorData}`);
        }

        // Успешное удаление
        console.log('Article deleted successfully');
        window.location.href = domain;
    } catch (error) {
        console.error('Error deleting article:', error);
    }
}

async function deleteImage(icon){
    await changePhoto(icon)
    let photo = icon.closest('div')
    photo.remove()
}

async function changePhoto(icon){
    let miniatures_container = document.getElementById('miniatures');
    let miniatures = miniatures_container.children;
    let mini_photo = icon.closest('div')
    let preview_photo = document.getElementById('preview')
    console.log('Miniatures length:', miniatures.length); // Output length to check

    // Debugging output of children
    if (miniatures.length != 0 && miniatures.length > 1){
        for (let i = 0; i < miniatures.length; i++) {
            if(miniatures[i] === mini_photo){
                if(i < miniatures.length-1){
                    let next_photo = miniatures[i+1]
                    console.log('i', i);
                    console.log('next_photo', next_photo);
                    console.log('miniatures[i+1]', miniatures[i+1]);
                    console.log('length', miniatures.length);
                    preview_photo.setAttribute('src', next_photo.querySelector('img').getAttribute('src'))
                } else {
                    let next_photo = miniatures[0]
                    console.log('next_photo', next_photo);
                    preview_photo.setAttribute('src', next_photo.querySelector('img').getAttribute('src'))
                }
               
            }
        }
    } else if(miniatures.length == 1){
         preview_photo.setAttribute('src', "")
    }
    let imageId = icon.getAttribute('data-image-id');
    console.log('Image ID:', imageId);

    if (imageId != 'new') {
        deleted_image_array.push(imageId);
        console.log('Deleted Image Array:', deleted_image_array);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let fileInput = document.querySelector('input[type="file"]');
    let preview = document.getElementById('preview');
    let miniatures = document.getElementById('miniatures');
    fileInput.addEventListener('change', function (e) {
        var file = fileInput.files[0];
        var reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            image_array.push(e.target.result)
            if (miniatures){
                let min = document.createElement('div')
                min.className = 'mini-photo'
                min.innerHTML = `<img style="height: 150px; width: 150px;object-fit: cover;" src = ${e.target.result}>
                <i class="xmark-position  fa-solid fa-trash fa-lg" data-image-id="new" style="color: #ca1616;" onclick="deleteImage(this)"></i>`
                miniatures.appendChild(min)
                min.querySelector('img').addEventListener('click', function (e) { getImage(e) })
            }
        };
        reader.readAsDataURL(file);
    });
});

function getImage(e) {
    e.preventDefault();
    console.log(e.target)
    let imageUrl = e.target.src;
    let modalImage = document.getElementById('modalImage');
    modalImage.src = imageUrl;
    
    let modal = new bootstrap.Modal(document.getElementById('modalForImage'));
    modal.show();
    document.getElementById('modalImageClose').addEventListener('click', function () {
        modal.hide()
    })
}

let form_article = document.getElementById('article_form')
form_article.addEventListener('submit', async function (event) {
    event.preventDefault();
    for (instance in CKEDITOR.instances) {
        CKEDITOR.instances[instance].updateElement();
    }
    
    let formData = new FormData(this);
    formData.delete('image');
    formData.append('tags', tags_array.join(','));
    
    for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value instanceof Blob ? value.slice(0, 100) : value);
    }
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
     const articleResponse = await update_article(csrfToken, token_acc, formData);
    if (articleResponse && image_array.length > 0) {
        formData.delete('title');
        formData.delete('content');
        formData.delete('category');
        formData.delete('tags');
        
        image_array.forEach((imageData, index) => {
            const blob = dataURItoBlob(imageData);
            formData.append('images', blob, `image${index}.jpg`);
        });
        
        await create_image(csrfToken, token_acc, formData, articleResponse.id);
    }
    window.location.href = domain;
})
async function update_article(csrf_token, token, form_data){
    console.log(form_data)
     try {
        const response = await fetch(domain + `/api/create_article/${id}/`, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrf_token,
                'Authorization': `Bearer ${token}`
            },
            body: form_data
        });
        if (!response.ok) {
            throw new Error('Ошибка при отправке формы: ' + response.statusText);
        }
        const data = await response.json();
        console.log(data);
        return data
    } catch (error) {
        console.error('Error during form submission:', error);
        throw error;
    }
    window.location.href = domain;
}

async function create_image(csrf_token, token, form_data, pk){
     try {
        const response = await fetch(domain + `/api/create_image/${pk}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrf_token,
                'Authorization': `Bearer ${token}`
            },
            body: form_data
        });
        if (!response.ok) {
            throw new Error('Ошибка при отправке формы: ' + response.statusText);
        }
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('Error during form submission:', error);
        throw error;
    }
    
}

function dataURItoBlob(dataURI) {
    console.log(dataURI)
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    console.log(mimeString)
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {type: mimeString});
}