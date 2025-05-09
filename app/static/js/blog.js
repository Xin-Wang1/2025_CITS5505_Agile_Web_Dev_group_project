const posts = [];

function renderPosts() {
    const postsList = $('#postsList');
    postsList.empty();

    posts.forEach((post, postIndex) => {
        const commentsHtml = post.comments.map((comment, commentIndex) => {
            return `
        <div class="comment">
          <strong>${comment.user}</strong>: ${comment.text}
          ${comment.file ? generateFilePreview(comment.file) : ''}
          <button class="btn btn-sm btn-danger mt-1" onclick="deleteComment(${postIndex}, ${commentIndex})">Delete Comment</button>
        </div>
      `;
        }).join('');

        const postCard = $(`
      <div class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">${post.title}</h5>
          <p class="post-meta">Posted by <strong>${post.user}</strong></p>
          <p class="card-text">${post.content}</p>
          ${post.file ? generateFilePreview(post.file) : ''}
          <button class="btn btn-sm btn-danger mb-3" onclick="deletePost(${postIndex})">Delete Post</button>
          <hr>
          <h6>Comments</h6>
          <div id="comments-${postIndex}" class="mb-3">
            ${commentsHtml}
          </div>
          <div class="form-group">
            <input type="text" class="form-control mb-2" id="commentUser-${postIndex}" placeholder="Your Name" required>
            <input type="text" class="form-control mb-2" id="commentInput-${postIndex}" placeholder="Write a comment...">
            <input type="file" class="form-control-file mb-2" id="commentFile-${postIndex}">
            <button class="btn btn-outline-primary btn-sm" onclick="addComment(${postIndex})">Comment</button>
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
        return `<p>Attachment: <a href="${fileUrl}" download>Download File</a></p>`;
    }
}

$('#postForm').submit(function (e) {
    e.preventDefault();
    const user = $('#postUser').val().trim();
    const title = $('#postTitle').val().trim();
    const content = $('#postContent').val().trim();
    const fileInput = $('#postFile')[0];
    let fileUrl = '';

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileUrl = URL.createObjectURL(file);
    }

    if (user && title && content) {
        posts.unshift({ user, title, content, file: fileUrl, comments: [] });
        $('#postForm')[0].reset();
        renderPosts();
    }
});

function addComment(postIndex) {
    const userInput = $(`#commentUser-${postIndex}`);
    const textInput = $(`#commentInput-${postIndex}`);
    const fileInput = $(`#commentFile-${postIndex}`)[0];
    const commentUser = userInput.val().trim();
    const commentText = textInput.val().trim();
    let fileUrl = '';

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileUrl = URL.createObjectURL(file);
    }

    if (commentUser && (commentText || fileUrl)) {
        posts[postIndex].comments.push({ user: commentUser, text: commentText, file: fileUrl });
        userInput.val('');
        textInput.val('');
        fileInput.value = '';
        renderPosts();
    }
}

function deletePost(index) {
    if (confirm('Are you sure you want to delete this post?')) {
        posts.splice(index, 1);
        renderPosts();
    }
}

function deleteComment(postIndex, commentIndex) {
    if (confirm('Are you sure you want to delete this comment?')) {
        posts[postIndex].comments.splice(commentIndex, 1);
        renderPosts();
    }
}

$(document).ready(function () {
    renderPosts();
});