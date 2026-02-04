// Video Upload Handler

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(uploadForm);
            const submitBtn = document.getElementById('uploadBtn');
            const progressContainer = document.getElementById('uploadProgressContainer');
            const progressBar = progressContainer.querySelector('.progress-bar');

            // Reset UI
            submitBtn.disabled = true;
            progressContainer.classList.remove('d-none');
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/v1/videos/upload/', true);
            xhr.setRequestHeader('X-CSRFToken', formData.get('csrfmiddlewaretoken'));

            // Upload progress
            xhr.upload.onprogress = function (e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = percentComplete + '%';
                    progressBar.textContent = percentComplete + '%';
                }
            };

            xhr.onload = function () {
                if (xhr.status === 201) {
                    alert('Video uploaded successfully!');
                    location.reload();
                } else {
                    let errorMessage = 'Upload failed';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMessage = response.error || errorMessage;
                    } catch (e) {
                        // response is not JSON
                    }
                    alert('Error: ' + errorMessage);
                    resetUI();
                }
            };

            xhr.onerror = function () {
                alert('Network error occurred during upload.');
                resetUI();
            };

            function resetUI() {
                submitBtn.disabled = false;
                progressContainer.classList.add('d-none');
                progressBar.style.width = '0%';
            }

            xhr.send(formData);
        });
    }
});
