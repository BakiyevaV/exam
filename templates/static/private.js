console.log('личный кабинет')
clearAlerts()
const form = document.querySelector('.user_info_form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault(); // Предотвратить стандартное поведение формы

        const username = document.getElementById('username').value;
        const last_name = document.getElementById('last_name').value;
        const b_date = document.getElementById('b_date').value;
        const phone = document.getElementById('phone').value;
		const photo = document.getElementById('photo').files[0];
		const pk = document.getElementById('pk').innerText;

        console.log(username, last_name, b_date, phone, photo);
		
		const formData = new FormData();
		if (username){
			console.log(username)
			formData.append('username', username);
		}
		if (last_name){
			console.log(last_name)
			formData.append('last_name', last_name);
		}
		if (b_date){
			console.log(b_date)
			formData.append('birthdate', b_date);
		}
		if (phone){
			console.log(photo)
			formData.append('phone', phone);
		}
		if (photo){
			console.log(photo)
			formData.append('photo', photo);
		}
		
		
		console.log(formData);
		const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
		console.log(csrfToken)
		const token_acc = await refreshToken(localStorage.getItem('refreshToken'));
		console.log(token_acc)
		 try {
			const response =  await fetch(domain + `user/api/save/${pk}/`, {
				method: 'PATCH',
				headers: {
                    'X-CSRFToken': csrfToken,
					'Authorization': `Bearer ${token_acc}`
                },
				credentials: 'include',
				body: formData,
			});
			if (response.ok) {
				const result = await response.json();
				console.log(result)
			} else {
				throw new Error('Failed to update user information.');
			}
		} catch (error) {
			console.error('Error:', error);
		}
    });
	

   
