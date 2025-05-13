$(document).ready(function() {
    // Username search
    $('#receiver_username').on('input', function() {
        const query = $(this).val().trim();
        if (query.length === 0) {
            $('#search-results').empty();
            return;
        }

        $.ajax({
            url: '/messages/search',
            method: 'GET',
            data: { query: query },
            success: function(data) {
                const results = $('#search-results');
                results.empty();
                if (data.length === 0) {
                    results.append('<div class="list-group-item">无匹配用户</div>');
                    return;
                }
                data.forEach(user => {
                    const item = $(`<a href="#" class="list-group-item list-group-item-action">${user.username}</a>`);
                    item.click(function(e) {
                        e.preventDefault();
                        $('#receiver_username').val(user.username);
                        results.empty();
                    });
                    results.append(item);
                });
            },
            error: function() {
                $('#search-results').html('<div class="list-group-item">搜索失败，请重试</div>');
            }
        });
    });

    // Form submission
    $('#messageForm').submit(function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        $.ajax({
            url: '/messages/send',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function() {
                window.location.reload(); // Refresh page to show new message
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON && xhr.responseJSON.message ? xhr.responseJSON.message : '发送失败，请重试';
                alert(errorMsg);
            }
        });
    });
});