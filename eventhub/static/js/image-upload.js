/* Account Page - Avatar Upload */

// handle image upload with 'Change Photo' button (users/account.html)
const fileInput = document.getElementById('imageUpload');
const changePhotoBtn = document.getElementById('changePhotoBtn');
const form = document.getElementById('avatarUploadForm');

// when the button is clicked, trigger the hidden file input
if (changePhotoBtn)
    changePhotoBtn.addEventListener('click', () => {
        fileInput.click();
    });

// when a file is selected, submit the form
if (fileInput)
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            form.submit();
        }
    });



/* Create New Event Page - Event Images Upload */

const MAX_FILE_SIZE_MB = 5;
const uploadBox = document.getElementById('uploadBox');
const imageUpload = document.getElementById('imageUpload');
const uploadedImages = document.getElementById('uploadedImages');
const imgUploadError = document.getElementById('image-upload-error');

// helper functions

// frontend validation for event images
function isValidImage(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const imageTypeValid = validTypes.includes(file.type);
    const imageSizeValid = file.size <= MAX_FILE_SIZE_MB * 1024 * 1024;

    if (!imageTypeValid)
        imgUploadError.textContent = `${file.name} has unsupported image format. Please upload a JPG, PNG, GIF or WEBP file.`;
    else if (!imageSizeValid)
        imgUploadError.textContent = `${file.name} image file is too large (max ${MAX_FILE_SIZE_MB}MB).`;

    return imageTypeValid && imageSizeValid;
}

function renderUploadedImage(e, file, uploadedFiles) {
    // img element
    const imgElement = document.createElement('img');
    imgElement.src = e.target.result;
    imgElement.alt = file.name;

    // delete icon
    const deleteButton = document.createElement('div');
    deleteButton.classList.add('delete-uploaded-image');
    deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
    deleteButton.addEventListener('click', function () {
        imageDiv.remove();
        const index = uploadedFiles.indexOf(file);
        if (index > -1)
            uploadedFiles.splice(index, 1);
    });

    // parent container
    const imageDiv = document.createElement('div');
    imageDiv.classList.add('uploaded-image');
    imageDiv.appendChild(imgElement);
    imageDiv.appendChild(deleteButton);

    // appending parent container to existing dom
    const uploadedImagesDiv = document.getElementById('uploadedImages');
    uploadedImagesDiv.appendChild(imageDiv);
}

function setFilesToInput(fileInput, filesArray) {
    const dataTransfer = new DataTransfer();
    filesArray.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
}


// manipulations
if (uploadBox && imageUpload) {

    // trigger file browse on click
    uploadBox.addEventListener('click', () => {
        imageUpload.click();
    });
    imageUpload.addEventListener('change', (e) => {
        handleFileUpload(e.target.files);
    });


    // handle file drag and drop
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.add('dragover');
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');

        const files = e.dataTransfer.files;
        handleFileUpload(files);
    });
}

const uploadedFiles = [];
function handleFileUpload(files) {
    imgUploadError.textContent = "";
    // add uploaded images to 'uploaded images div'
    for (let file of files) {
        if (isValidImage(file)) {
            const reader = new FileReader();
            reader.onload = function (e) {
                uploadedFiles.push(file);
                renderUploadedImage(e, file, uploadedFiles);
            };

            reader.readAsDataURL(file);
        }
    }
}

// send uploaded files with the form
const eventForm = document.getElementById('eventForm');
if (eventForm) {
    eventForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // put files in event_images input
        setFilesToInput(imageUpload, uploadedFiles);
        eventForm.submit();
    });
}