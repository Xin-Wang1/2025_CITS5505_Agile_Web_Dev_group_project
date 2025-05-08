let posts = [];
const currentUser = "{{ username }}"; 

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
                    <p class="post-meta">Post by：<strong>${post.user}</strong> at ${new Date(post.created_at).toLocaleString()}</p>
                    <p class="card-text">${post.description}</p>
                    ${post.file_url ? generateFilePreview(post.file_url) : ''}
                    ${post.user === currentUser ? `<button class="btn btn-sm btn-danger mb-3" onclick="deletePost(${post.id})">Delete</button>` : ''}
                    <hr>
                    <h6>Comment</h6>
                    <div id="comments-${postIndex}" class="mb-3">
                        ${commentsHtml}
                    </div>
                    <div class="form-group">
                        <input type="text" class="form-control mb-2" id="commentInput-${postIndex}" placeholder="leave your comment...">
                        <input type="file" class="form-control-file mb-2" id="commentFile-${postIndex}">
                        <button class="btn btn-outline-primary btn-sm" onclick="addComment(${postIndex}, ${post.id})">Add comment</button>
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
        return `<p>attachment:<a href="${fileUrl}" download>download</a></p>`;
    }
}

function fetchPosts() {
    $.get('/api/posts', function(data) {
        posts = data;
        renderPosts();
    }).fail(function(xhr) {
        $('#alertContainer').html(`<div class="alert alert-danger">Failed to load：${xhr.responseJSON?.error || 'Unknown error'}</div>`);
    });
}

$('#postForm').submit(function(e) {
    e.preventDefault();
    const title = $('#postTitle').val().trim();
    const content = $('#postContent').val().trim();
    if (title.length > 150) {
        $('#alertContainer').html('<div class="alert alert-danger">The length of the title cannot exceed 150 characters</div>');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', content);
    formData.append('schedule_id', 1); 
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
            $('#alertContainer').html('<div class="alert alert-success">Published successfully！</div>');
            setTimeout(() => $('#alertContainer').empty(), 3000);
        },
        error: function(xhr) {
            $('#alertContainer').html(`<div class="alert alert-danger">Error：${xhr.responseJSON?.error || 'Unknown error'}</div>`);
        }
    });
});

function addComment(postIndex, postId) {
    const textInput = $(`#commentInput-${postIndex}`);
    const fileInput = $(`#commentFile-${postIndex}`)[0];
    const commentText = textInput.val().trim();
    if (!commentText) {
        $('#alertContainer').html('<div class="alert alert-danger">Empty Comment!!!</div>');
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
            $('#alertContainer').html('<div class="alert alert-success">Comment added！</div>');
            setTimeout(() => $('#alertContainer').empty(), 3000);
        },
        error: function(xhr) {
            $('#alertContainer').html(`<div class="alert alert-danger">Error：${xhr.responseJSON?.error || 'Unkown error'}</div>`);
        }
    });
}

function deletePost(postId) {
    if (confirm('Are you sure with this delete？')) {
        $.ajax({
            url: `/api/posts/${postId}`,
            type: 'DELETE',
            success: function() {
                fetchPosts();
                $('#alertContainer').html('<div class="alert alert-success">Post has benn delete</div>');
                setTimeout(() => $('#alertContainer').empty(), 3000);
            },
            error: function(xhr) {
                $('#alertContainer').html(`<div class="alert alert-danger">Error：${xhr.responseJSON?.error || 'Unkown error'}</div>`);
            }
        });
    }
}

$(document).ready(function() {
    fetchPosts();
});