CKEDITOR.replace('id_content');
let image_array = []
clearAlerts()

document.addEventListener("DOMContentLoaded", function() {s
    let imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.removeAttribute('required');
    }
});

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
                min.name = 'min'
                min.style.border = `1px solid white`
                min.innerHTML = `<img style="height: 150px; width: 150px;" src = ${e.target.result}>`
                min.addEventListener('click', function (e) { getImage(e) })
                miniatures.appendChild(min)
            }
            };
            reader.readAsDataURL(file);
        });
});

function getImage(e) {
    e.preventDefault();
    let imageUrl = e.target.src;
    let modalImage = document.getElementById('modalImage');
    modalImage.src = imageUrl;
    
    let modal = new bootstrap.Modal(document.getElementById('modalForImage'));
    modal.show();
}
let tags_array = []
const add_tag = document.getElementById('add_tag')
let tags_line = document.getElementById('tags_line')
add_tag.addEventListener('click', addTags)

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
            tag_container = document.createElement('div')
            tag_container.className = "tag_container"
            tag_container.innerHTML = `#${tag}`
            tags_line.appendChild(tag_container)
        }
    }
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
     const articleResponse = await create_article(csrfToken, token_acc, formData);
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
async function create_article(csrf_token, token, form_data){
     try {
        const response = await fetch(domain + `/api/create_article/`, {
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
        return data
    } catch (error) {
        console.error('Error during form submission:', error);
        throw error;
    }
    
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