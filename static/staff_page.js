let change_status_button = document.getElementById('save_status')
change_status_button.addEventListener('click', changeStatus)

async function changeStatus(){
	let checkbox_array = document.querySelectorAll('input[type="checkbox"]')
	console.log(checkbox_array)
	for (const checkbox of checkbox_array) {
        if (checkbox.checked) {
            let status = await updateStatus(checkbox.getAttribute('data-inquiry-id'))
        }
    }
	window.location.href = '/for_staff/';
}

async function updateStatus(pk){
	try{
	 	const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    	const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
		const response = await fetch(domain + `api/inquiry/${pk}/`, {
			method: 'PATCH',
			headers: {
				'X-CSRFToken': csrfToken,
				'Authorization': `Bearer ${token_acc}`
			},
			body: JSON.stringify({ is_resolved: true })
		});
		if (!response.ok) {
			throw new Error('Ошибка при отправке формы: ' + response.statusText);
		}
		const data = await response.json();
		console.log(data);
		return data
	}catch (error) {
        console.error('Error during form submission:', error);
        throw error;
    }
}

