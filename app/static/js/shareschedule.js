let posts = [];
const currentUser = "{{ username }}"; // 从模板获取

function renderPosts() {
    const postsList = $('#postsList');
    postsList.empty();

    posts.forEach((post, postIndex) => {
        const commentsHtml = post.comments.map((comment, commentIndex) => {
            return `
                <div class="comment">
                    <strong>${comment.user}</strong>: ${comment.content}
                    ${comment.file_url ? generateFilePreview(comment.file_url) : ''}
                </div>
            `;
        }).join('');

        const postCard = $(`
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">${post.title}</h5>
                    <p class="post-meta">发布者：<strong>${post.user}</strong> 于 ${new Date(post.created_at).toLocaleString()}</p>
                    <p class="card-text">${post.description}</p>
                    ${post.file_url ? generateFilePreview(post.file_url) : ''}
                    ${post.user === currentUser ? `<button class="btn btn-sm btn-danger mb-3" onclick="deletePost(${post.id})">删除帖子</button>` : ''}
                    <hr>
                    <h6>评论</h6>
                    <div id="comments-${postIndex}" class="mb-3">
                        ${commentsHtml}
                    </div>
                    <div class="form-group">
                        <input type="text" class="form-control mb-2" id="commentInput-${postIndex}" placeholder="写下您的评论...">
                        <input type="file" class="form-control-file mb-2" id="commentFile-${postIndex}">
                        <button class="btn btn-outline-primary btn-sm" onclick="addComment(${postIndex}, ${post.id})">评论</button>
                    </div>
                </div>
            </div>
        `);

        postsList.append(postCard);
    });
}

function generateFilePreview(fileUrl) {
    const isImage = /\.(jpg|jpeg|png|gif)$/i.test(fileUrl);
    if (isImage) {
        return `<img src="${fileUrl}" class="img-preview">`;
    } else {
        return `<p>附件：<a href="${fileUrl}" download>下载文件</a></p>`;
    }
}

function fetchPosts() {
    $.get('/api/posts', function(data) {
        posts = data;
        renderPosts();
    }).fail(function(xhr) {
        $('#alertContainer').html(`<div class="alert alert-danger">加载帖子失败：${xhr.responseJSON?.error || '未知错误'}</div>`);
    });
}

$('#postForm').submit(function(e) {
    e.preventDefault();
    const title = $('#postTitle').val().trim();
    const content = $('#postContent').val().trim();
    if (title.length > 150) {
        $('#alertContainer').html('<div class="alert alert-danger">标题长度不能超过150个字符</div>');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', content);
    formData.append('schedule_id', 1); // 示例，需动态获取
    if ($('#postFile')[0].files.length > 0) {
        formData.append('file', $('#postFile')[0].files[0]);
    }

    $.ajax({
        url: '/api/posts',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function() {
            $('#postForm')[0].reset();
            fetchPosts();
            $('#alertContainer').html('<div class="alert alert-success">帖子发布成功！</div>');
            setTimeout(() => $('#alertContainer').empty(), 3000);
        },
        error: function(xhr) {
            $('#alertContainer').html(`<div class="alert alert-danger">错误：${xhr.responseJSON?.error || '未知错误'}</div>`);
        }
    });
});

function addComment(postIndex, postId) {
    const textInput = $(`#commentInput-${postIndex}`);
    const fileInput = $(`#commentFile-${postIndex}`)[0];
    const commentText = textInput.val().trim();
    if (!commentText) {
        $('#alertContainer').html('<div class="alert alert-danger">评论内容不能为空</div>');
        return;
    }

    const formData = new FormData();
    formData.append('shared_schedule_id', postId);
    formData.append('content', commentText);
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }

    $.ajax({
        url: '/api/comments',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function() {
            textInput.val('');
            fileInput.value = '';
            fetchPosts();
            $('#alertContainer').html('<div class="alert alert-success">评论添加成功！</div>');
            setTimeout(() => $('#alertContainer').empty(), 3000);
        },
        error: function(xhr) {
            $('#alertContainer').html(`<div class="alert alert-danger">错误：${xhr.responseJSON?.error || '未知错误'}</div>`);
        }
    });
}

function deletePost(postId) {
    if (confirm('确定要删除此帖子吗？')) {
        $.ajax({
            url: `/api/posts/${postId}`,
            type: 'DELETE',
            success: function() {
                fetchPosts();
                $('#alertContainer').html('<div class="alert alert-success">帖子已删除</div>');
                setTimeout(() => $('#alertContainer').empty(), 3000);
            },
            error: function(xhr) {
                $('#alertContainer').html(`<div class="alert alert-danger">错误：${xhr.responseJSON?.error || '未知错误'}</div>`);
            }
        });
    }
}

$(document).ready(function() {
    fetchPosts();
});