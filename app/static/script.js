console.log('script.js');

document.addEventListener('DOMContentLoaded', function() {

    const file = document.getElementById('fileToUpload');
    const fileChooseButton = document.getElementById('file-choose-button');
    const fileSendButton = document.getElementById('file-send-button');
    const output = document.getElementById('output');
    const output2 = document.getElementById('output2');
    const output3 = document.getElementById('output3');
    const form = document.getElementById('form');
    const fileName = document.getElementById('fileName');
    const pathName = document.querySelector('.pathname');
    const analyzeButton = document.getElementById('analyze');
    const table = document.getElementById('table');
    const col1 = document.getElementById('col1');
    const col2 = document.getElementById('col2');
    const col3 = document.getElementById('col3');

    console.log(analyzeButton);
    
    let receivedFileName = '';

    // Выбор файла 
    fileChooseButton.addEventListener('click', (e) => {
        e.preventDefault();
        file.click();
    });
    // Отображение имени файла
    form.addEventListener('change', e => {
        e.preventDefault();
        console.log(file.files[0].name);
        fileName.textContent = file.files[0].name;
    });

    // Отправка файла на сервер
    form.addEventListener('submit', async function(event) {
        console.log('submit');
        event.preventDefault();
        fileName.textContent = '';
        let formData = new FormData(form);
        formData.append('file', file.files[0]);
        showPopup();
        try {
                const response = await fetch("/upload", {
                    method: 'POST',
                    headers: {
                        "enctype": "multipart/form-data"
                    },                
                    body: formData
                
                });
           
                if (response.ok) {
                    console.log('response получен');
                    const data = await response.json();
                    form.reset(); // Сбрасываем форму
                    console.log(data);
                    output.classList.remove('hidden');
                    pathName.textContent = 'Архив успешно загружен на сервер. Хотите проанализировать фотографии?';
                    receivedFileName = data.filename;
                    console.log(receivedFileName);
                    hidePopup();
        
                } else {
                    output.classList.remove('hidden');
                    output.textContent = 'Ошибка при загрузке файла.';
                    hidePopup();
                }
            } catch (error) {
                console.error('Произошла ошибка:', error);
                output.classList.remove('hidden');
                output.textContent = 'Произошла ошибка при выполнении запроса.';
            }
    });

    analyzeButton.addEventListener('click', async function(event) {
        event.preventDefault();
        console.log('click analyze');
        console.log(receivedFileName);
    
        try {
            const response = await fetch(`/predict?filename=${receivedFileName}`, {
                // const response = await fetch("/predict?filename=3b67c7a2f2434541ba6e325470ef469e", {

                method: 'POST',
                // headers: {
                //     "Content-type": "application/json"
                // },   
            });
           
        if (response.ok) {
                console.log('response 2 получен');
                const data = await response.json();
                output2.classList.remove('hidden');
                output.classList.add('hidden');
                console.log(data);
            
                let col1Html = '';
                data.images.broken.forEach((el) => {
                    col1Html += `
                    <div class = "cards"><img src="${el}" alt=""></div>`;
                });
                console.log(col1Html);
                col1.innerHTML = col1Html;

                let col2Html = '';
                data.images.empty.forEach((el) => {
                    col2Html += `
                    <div class = "cards"><img src="${el}" alt=""></div>`;
                });
                console.log(col2Html);
                col2.innerHTML = col2Html;

                let col3Html = '';
                data.images.animal.forEach((el) => {
                    col3Html += `
                    <div class = "cards"><img src="${el}" alt=""></div>
              `;
                });
                console.log(col3Html);
                col3.innerHTML = col3Html;


                // let html = `<tr>
                //             <td>Animals</td>
                //             <td>Blurred</td>
                //             <td>Nobody</td>
                //             </tr>`;
            //     testArr.forEach((el) => {
            //         html += `
            //         <div class = "cards"><img src="/test/183868593e414a6eabe5dd4725889cea/SYER0023.JPG" alt=""></div>
            //   `; 
            //     });
                // console.log(html);
                // col2.innerHTML = html;
      
            } else {
                output.classList.remove('hidden');
                output.textContent = 'Ошибка при загрузке файла.';
                hidePopup();
            }
        }
         catch (error) {
            console.error('Произошла ошибка:', error);
            output.classList.remove('hidden');
            output.textContent = 'Произошла ошибка при выполнении запроса.';
        }
        
    });

});

// Функция для отображения всплывающего окна
function showPopup() {
    popup.style.display = "block";
}
  
// Функция для скрытия всплывающего окна
function hidePopup() {
    popup.style.display = "none";
}


