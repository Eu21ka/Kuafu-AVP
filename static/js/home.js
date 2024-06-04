$(document).ready(function() {
    var csrftoken = $('[name=csrfmiddlewaretoken]').val(); // 获取CSRF Token

    $("#excelImport").click(function() {
        $('#fileupload').click();
    });

    $('#fileupload').change(function() {
        handleFileUpload($('#fileupload')[0].files);
    });

    function handleFileUpload(files) {
        var formData = new FormData();
        formData.append('file', files[0]);  // 这里假设只处理单个文件上传
        formData.append('csrfmiddlewaretoken', csrftoken); // 添加CSRF Token

        $.ajax({
            url: uploadUrl, // 修改为您的Django后端URL
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                $('.alert').alert('close');
                if (data.success){
                    var alertHTML = '<div class="alert alert-success alert-dismissible fade show" role="alert">' +
                                '<div>'+ data.message +'</div>' +
                                '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                                '</div>';
                }else{
                    var alertHTML = '<div class="alert alert-danger alert-dismissible fade show" role="alert">' +
                                '<div>'+ data.message +'</div>' +
                                '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                                '</div>';
                }
                $('#alert-container').html(alertHTML);
                
                // 重置输入控件，准备下一次上传
                resetFileInput(); 
            },
            error: function(xhr, status, error) {
                let response = JSON.parse(xhr.responseText);
                let message = response.message || "未知错误";
                alert(message);
            }
        });
    }

    function resetFileInput() {
        $('#fileupload').val(''); // 清空文件输入控件的值
    }

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = $('#js-upload-form');
    
    uploadForm.on('submit', function(e) {
        e.preventDefault();
        handleFileUpload($('#fileupload').prop('files'));
    })

    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        handleFileUpload(e.dataTransfer.files); // 处理拖拽上传
    }
    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    }
    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    }
});