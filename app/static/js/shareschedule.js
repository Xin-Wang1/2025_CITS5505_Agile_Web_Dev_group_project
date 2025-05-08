$(document).ready(function() {
    let selectedUser = null;
    let selectedSchedule = null;

    // Search users
    $('#searchInput').on('input', function() {
        const query = $(this).val().trim();
        if (query.length < 2) {
            $('#userList').empty();
            return;
        }
        $.get('/api/users/search', { query }, function(data) {
            $('#userList').empty();
            if (data.length === 0) {
                $('#userList').append('<li class="list-group-item">No users found</li>');
                return;
            }
            data.forEach(user => {
                if (user.id !== {{ current_user.id }}) {
                    $('#userList').append(
                        `<li class="list-group-item list-group-item-action" data-user-id="${user.id}" data-username="${user.username}">
                            ${user.username}
                        </li>`
                    );
                }
            });
        }).fail(function() {
            $('#status').text('Error searching users').addClass('text-danger');
        });
    });

    // Clear search
    $('#clearSearch').click(function() {
        $('#searchInput').val('');
        $('#userList').empty();
        $('#messageForm').addClass('d-none');
        selectedUser = null;
    });

    // Select user
    $('#userList').on('click', '.list-group-item', function() {
        selectedUser = {
            id: $(this).data('user-id'),
            username: $(this).data('username')
        };
        $('#selectedUser').text(selectedUser.username);
        $('#messageForm').removeClass('d-none');
        const scheduleId = $('#scheduleSelect').val();
        if (scheduleId) {
            const link = `${window.location.origin}/schedule/${scheduleId}`;
            $('#messageContent').val(`Check out my schedule: ${link}`);
        }
    });

    // Select schedule
    $('#scheduleSelect').change(function() {
        selectedSchedule = $(this).val();
        if (selectedUser && selectedSchedule) {
            const link = `${window.location.origin}/schedule/${selectedSchedule}`;
            $('#messageContent').val(`Check out my schedule: ${link}`);
        }
    });

    // Send message
    $('#sendMessage').click(function() {
        if (!selectedUser || !selectedSchedule) {
            $('#status').text('Please select a user and a schedule').addClass('text-danger');
            return;
        }
        const content = $('#messageContent').val().trim();
        if (!content) {
            $('#status').text('Message cannot be empty').addClass('text-danger');
            return;
        }
        $.ajax({
            url: '/api/messages/send',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                receiver_id: selectedUser.id,
                content: content,
                schedule_id: selectedSchedule
            }),
            success: function() {
                $('#status').text/`Message sent to ${selectedUser.username}`).addClass('text-success').removeClass('text-danger');
                $('#messageContent').val('');
                $('#messageForm').addClass('d-none');
                selectedUser = null;
                $('#searchInput').val('');
                $('#userList').empty();
            },
            error: function(xhr) {
                $('#status').text(xhr.responseJSON?.error || 'Error sending message').addClass('text-danger');
            }
        });
    });

    // Cancel message
    $('#cancelMessage').click(function() {
        $('#messageForm').addClass('d-none');
        selectedUser = null;
        $('#status').empty();
    });
});