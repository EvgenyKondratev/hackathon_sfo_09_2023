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
                    pathName.textContent = 'Архив успешно загружен на сервер. Имя файла:  ' + data.filename + '. Path: ' + data.path + '  Хотите проанализировать фотографии?';
                    receivedFileName = data.filename;
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
    
        try {
            const response = await fetch("/predict?filename=${receivedFileName}", {
                method: 'POST',
            });
           
        if (response.ok) {
                console.log('response 2 получен');
                const data = await response.json();
                output2.classList.remove('hidden');
                output.classList.add('hidden');
                console.log(data.images);
                // output3.textContent = data;
                let testArr = ['string-1', 'string-2', 'string-3'];
                let html = '';
                let col1Html = '';
                
                // let html = `<tr>
                //             <td>Animals</td>
                //             <td>Blurred</td>
                //             <td>Nobody</td>
                //             </tr>`;
                testArr.forEach((el) => {
                    html += `
                    <div class = "cards"><img src="/test/183868593e414a6eabe5dd4725889cea/SYER0023.JPG" alt=""></div>
              `; 
                });
                console.log(html);
                col2.innerHTML = html;
      
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


