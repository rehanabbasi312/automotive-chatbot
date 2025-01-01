$(document).ready(function () {
    let urlParams = new URLSearchParams(window.location.search);
    let chatIdFromUrl = urlParams.get('chat_id');
    let currentChatId = chatIdFromUrl || localStorage.getItem('currentChatId') || null;
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || {};

    function renderMarkdown(content) {
        return marked.parse(content);
    }

    function addMessage(role, content, images = null, carDetails = [], carDetailsLinks = []) {
        let messageElement;
    
        // Append images if available
        if (images && images.length > 0) {
            images.forEach((imageUrl, index) => {
                let detailsHtml = '';
                if (carDetails && carDetails[index]) {
                    const details = carDetails[index];
                    detailsHtml = `
                        <div class="car-details">
                            <p><strong>Make:</strong> ${details.make || 'N/A'}</p>
                            <p><strong>Model:</strong> ${details.model || 'N/A'}</p>
                            <p><strong>Engine:</strong> ${details.engine || 'N/A'}</p>
                            <p><strong>Mileage:</strong> ${details.mileage || 'N/A'}</p>
                            <p><strong>Fuel:</strong> ${details.fuel || 'N/A'}</p>
                            <p><strong>Price:</strong> ${details.price || 'N/A'}</p>
                            <p><strong>Year:</strong> ${details.year || 'N/A'}</p>
                            <p><strong>Condition:</strong> ${details.condition || 'N/A'}</p>
                            
                        </div>
                    `;
                }
    
                let detailsLinkHtml = '';
                if (carDetails && carDetails[index] && carDetails[index].id) {
                    const carId = carDetails[index].id;
                    detailsLinkHtml = `
                        <a href="/vdp/${carId}" class="car-link" onclick="saveCurrentChatId()" aria-label="View more details about this car">More Details</a>
                    `;
                }
    
                messageElement = $(`
                    <div class="message ${role} card">
                        <div class="message-icon"><i class="fas fa-car"></i></div>
                        <div class="card-content">
                            <img src="${imageUrl}" alt="Car image" class="card-image">
                            ${detailsHtml}
                            ${detailsLinkHtml}
                        </div>
                    </div>
                `);
                $('#message-container').append(messageElement);
            });
        } else {
            const iconClass = role === 'user' ? 'fas fa-user' : 'fas fa-car';
    
            // If the role is 'assistant', format the response using renderMarkdown
            const formattedContent = role === 'assistant' ? renderMarkdown(content) : content;
    
            messageElement = $(`
                <div class="message ${role} card">
                    <div class="message-icon"><i class="${iconClass}"></i></div>
                    <div class="message-content">${formattedContent}</div>
                </div>
            `);
            $('#message-container').append(messageElement);
        }
    
        // Scroll to the bottom of the container
        $('#message-container').scrollTop($('#message-container')[0].scrollHeight);
    
        // Save the message to local storage
        if (currentChatId) {
            if (!chatHistory[currentChatId]) {
                chatHistory[currentChatId] = { title: 'New Chat', messages: [] };
            }
            chatHistory[currentChatId].messages.push({ role, content, images, carDetails, carDetailsLinks });
    
            // Update the summary/title of the conversation
            chatHistory[currentChatId].title = summarizeConversation(chatHistory[currentChatId].messages);
    
            localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
            updateChatHistory();
        }
    }
    

 
    

    function summarizeConversation(messages) {
        const userMessages = messages.filter(msg => msg.role === 'user').map(msg => msg.content);
        const assistantMessages = messages.filter(msg => msg.role === 'assistant').map(msg => msg.content);

        let summary = "New Chat";
        if (userMessages.length > 0) {
            summary = userMessages[0];
            if (assistantMessages.length > 0) {
                summary += " - " + assistantMessages[assistantMessages.length - 1].slice(0, 30);
            }
        }
        return summary;
    }

    function saveCurrentChatId() {
        localStorage.setItem('currentChatId', currentChatId);
    }

    function sendMessage() {
        const message = $('#user-input').val().trim();
        if (message) {
            addMessage('user', message);
            $('#user-input').val('');
            $('#user-input').css('height', 'auto');
            $('#user-input').prop('disabled', true);
            $('#send-button').prop('disabled', true);
            $('#loading-indicator').show();

            $.ajax({
                url: '/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ message: message, chat_id: currentChatId }),
                success: function (response) {
                    console.log("Response received:", response);

                    if (response.car_images && response.car_images.length > 0) {
                        console.log("Adding car images to response");
                        addMessage('assistant', response.response, response.car_images, response.car_details, response.car_details_links);
                    } else {
                        addMessage('assistant', response.response);
                    }
                },
                error: function (xhr, status, error) {
                    console.error("AJAX request failed:", error);
                    addMessage('assistant', "Sorry, there was an error processing your request.");
                },
                complete: function () {
                    $('#user-input').prop('disabled', false);
                    $('#send-button').prop('disabled', false);
                    $('#loading-indicator').hide();
                    $('#user-input').focus();
                }
            });
        }
    }

    function updateChatHistory() {
        const chatHistoryList = $('#chat-history');
        chatHistoryList.empty();
        for (const chatId in chatHistory) {
            const chat = chatHistory[chatId];
            const chatItem = $('<div class="chat-item"></div>').text(chat.title);
            chatItem.click(function () {
                loadChat(chatId);
            });
            chatHistoryList.append(chatItem);
        }
    }

    function loadChat(chatId) {
        currentChatId = chatId;
        saveCurrentChatId();

        const chat = chatHistory[chatId];
        $('#message-container').empty();
        if (chat && chat.messages.length > 0) {
            chat.messages.forEach(message => {
                addMessage(message.role, message.content, message.images, message.carDetails, message.carDetailsLinks);
            });
        } else {
            addMessage('assistant', "Hi there! I'm Automotive AI, your advanced automotive assistant. How can I help you today?");
        }
    }

    function createNewChat() {
        currentChatId = String(new Date().getTime());
        chatHistory[currentChatId] = { title: 'New Chat', messages: [] };
        saveCurrentChatId();
        $('#message-container').empty();
        addMessage('assistant', "Hi there! I'm Automotive AI, your advanced automotive assistant. How can I help you today?");
        updateChatHistory();
    }

    function clearHistory() {
        localStorage.removeItem('chatHistory');
        chatHistory = {};
        $('#chat-history').empty();
        createNewChat();
    }

    $('#send-button').click(sendMessage);

    $('#user-input').on('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    $('#user-input').keydown(function (e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    $('#new-chat').click(function () {
        createNewChat();
        updateChatHistory();
    });

    $('#clear-history').click(clearHistory);

    // Initialize chat
    if (currentChatId && chatHistory[currentChatId]) {
        loadChat(currentChatId);
    } else {
        createNewChat();
    }
    updateChatHistory();
});
