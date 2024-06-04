const exampleModal = document.getElementById('exampleModal')
exampleModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget
    const recipient = button.getAttribute('data-bs-whatever')
    document.getElementById('shellcode_name_input').value = recipient
})

    $(document).ready(function() {
        $('#trojan_form').submit(function(e) {
            e.preventDefault();
            var formData = new FormData(this);

            var btntHTML = '<div class="spinner-border text-success"></div>'
            $('#btn-container').html(btntHTML);

            $.ajax({
                url: createUrl,
                type: 'POST',
                data: formData,
                success: function(data) {
                    $('.alert').alert('close');
                    document.getElementById("closeBtn").click();
                    var btntHTML = '<button type="submit" class="btn btn-primary">生成</button>'
                    $('#btn-container').html(btntHTML);
                    // 显示警告消息
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
                },
                error: function(error) {
                    document.getElementById("closeBtn").click();
                    var btntHTML = '<button type="submit" class="btn btn-primary">生成</button>'
                    $('#btn-container').html(btntHTML);
                    // 处理错误
                    console.error('Error:', error);
                },
                cache: false,
                contentType: false,
                processData: false
            });

        });
    });

$(document).ready(function(){
    $('.delete-btn').click(function(){
        var fileID = $(this).data('file-id');
        var csrfToken = $("#csrf_token").val();
        var confirmed = confirm("确定要删除这个文件吗？");
        if (confirmed) {
            $.ajax({
                url: $("#trojan_form").data("delete-url").replace('/0/', '/' + fileID + '/'),
                type: 'POST',
                data: {
                    'file_id': fileID,
                    'csrfmiddlewaretoken': csrfToken
                },
                dataType: 'json',
                success: function(data) {
                    // 显示警告消息
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
                    setTimeout(function(){location.reload()}, 500)
                },
            });
        }
    });
});

function generateKey() {
    const selectedLength = parseInt(document.getElementById('keyLength').value);
    const characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+';
    let result = '';
    const charactersLength = characters.length;
    for (let i = 0; i < selectedLength; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    document.getElementById('encode_key').value = result;
}