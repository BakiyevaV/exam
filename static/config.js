const domain = 'https://64.226.87.192:8000/';

const mainalertPlaceholder = document.getElementById('liveAlertPlaceholder2')
const appendAlertMain = (message, type) => {
  const wrapper = document.createElement('div')
    console.log(wrapper)
    console.log(mainalertPlaceholder)
  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('')
  mainalertPlaceholder.append(wrapper)
    console.log(mainalertPlaceholder)
}
function clearAlerts() {
    const alertContainer = document.querySelector('.alert');
    console.log(alertContainer)
    if (alertContainer) {
        alertContainer.remove(); // Правильно: вызываем remove на самом элементе
    }
}

async function refreshToken(refreshToken) {
    const url = domain + 'user/api/token/refresh/';
    try {
        const response =  await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({refresh: refreshToken})
        })
        if (response.ok) {
            const result = await response.json();
            console.log(result)
            return result.access
        } else {
            throw new Error('Failed to update user information.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

