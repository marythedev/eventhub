// handle image upload with 'Change Photo' button (users/account.html)
const fileInput = document.getElementById('imageUpload');
const changePhotoBtn = document.getElementById('changePhotoBtn');
const form = document.getElementById('avatarUploadForm');

// when the button is clicked, trigger the hidden file input
changePhotoBtn.addEventListener('click', () => {
    fileInput.click();
});

// when a file is selected, submit the form
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        form.submit();
    }
});