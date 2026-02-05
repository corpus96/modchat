// Global state
let currentState = {
    conversation: null,
    auto_response_enabled: true,
    show_reactions: true,
    current_message_index: -1,
    selectedCharacterId: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadState();
});

function setupEventListeners() {
    document.getElementById('autoResponse').addEventListener('change', (e) => {
        toggleSetting('auto_response', e.target.checked);
    });

    document.getElementById('showReactions').addEventListener('change', (e) => {
        toggleSetting('show_reactions', e.target.checked);
        refreshMessages();
    });

    document.getElementById('messageInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendManualMessage();
        }
    });

    // ESC key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Close any active modal
            document.querySelectorAll('.modal.active').forEach(modal => {
                modal.classList.remove('active');
            });
        }
    });
}

// API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const url = method === 'GET' && data 
            ? `${endpoint}?${new URLSearchParams(data)}`
            : endpoint;

        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }

        return await response.json();
    } catch (error) {
        showError(error.message);
        throw error;
    }
}

// Load current state
async function loadState() {
    try {
        const state = await apiCall('/api/state');
        currentState = state;
        
        if (state.conversation) {
            renderConversation();
        }
    } catch (error) {
        console.error('Failed to load state:', error);
    }
}

// Show/hide modals
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function closeModalOnBackdrop(event, modalId) {
    // Close modal when clicking on the backdrop (outside the modal content)
    if (event.target.classList.contains('modal')) {
        closeModal(modalId);
    }
}

function showNewConversationModal() {
    showModal('newConversationModal');
}

function showAddCharacterModal() {
    if (!currentState.conversation) {
        showError('Create a conversation first');
        return;
    }
    showModal('addCharacterModal');
}

function showLoadModal() {
    loadConversationsList();
    showModal('loadModal');
}

// Create new conversation
async function createNewConversation() {
    const scenario = document.getElementById('newScenario').value.trim();
    const char1Name = document.getElementById('char1Name').value.trim();
    const char1Desc = document.getElementById('char1Desc').value.trim();
    const char2Name = document.getElementById('char2Name').value.trim();
    const char2Desc = document.getElementById('char2Desc').value.trim();

    // Only require character names - descriptions are optional
    if (!char1Name || !char2Name) {
        showError('Please provide names for both characters');
        return;
    }

    showThinking();
    showStatus('Creating story with AI...');

    try {
        const formData = new URLSearchParams({
            scenario_description: scenario || '',
            character1_name: char1Name,
            character1_description: char1Desc || '',
            character2_name: char2Name,
            character2_description: char2Desc || ''
        });

        await fetch('/api/conversation/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        closeModal('newConversationModal');
        await loadState();
        hideThinking();
        showSuccess('Story created! Click on a character to begin.');
        
        // Clear form
        document.getElementById('newScenario').value = '';
        document.getElementById('char1Name').value = '';
        document.getElementById('char1Desc').value = '';
        document.getElementById('char2Name').value = '';
        document.getElementById('char2Desc').value = '';
    } catch (error) {
        hideThinking();
        showError('Failed to create conversation');
    }
}

// Add character
async function addCharacter() {
    const name = document.getElementById('newCharName').value.trim();
    const description = document.getElementById('newCharDesc').value.trim();

    if (!name) {
        showError('Please provide a character name');
        return;
    }

    showThinking();

    try {
        const formData = new URLSearchParams({ 
            name, 
            description: description || '' 
        });
        
        await fetch('/api/character/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        closeModal('addCharacterModal');
        await loadState();
        hideThinking();
        showSuccess('Character added!');
        
        // Clear form
        document.getElementById('newCharName').value = '';
        document.getElementById('newCharDesc').value = '';
    } catch (error) {
        hideThinking();
        showError('Failed to add character');
    }
}

// Generate AI response
async function generateAIResponse() {
    console.log('generateAIResponse called, auto_response_enabled:', currentState.auto_response_enabled);
    
    if (!currentState.conversation) {
        showError('No active conversation');
        return;
    }

    const characterId = currentState.auto_response_enabled 
        ? null 
        : document.getElementById('characterSelect').value;

    if (!currentState.auto_response_enabled && !characterId) {
        showError('Please select a character');
        return;
    }

    // Show thinking indicator
    showThinking();

    try {
        const formData = new URLSearchParams();
        if (characterId) {
            formData.append('character_id', characterId);
        }

        const response = await fetch('/api/message/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to generate message');
        }

        await loadState();
        hideThinking();
        
        console.log('Message generated successfully');
    } catch (error) {
        console.error('Generate AI response error:', error);
        showError(error.message);
    }
}

// Send manual message
async function sendManualMessage() {
    const content = document.getElementById('messageInput').value.trim();
    const characterId = document.getElementById('characterSelect').value;

    console.log('sendManualMessage called:', {
        content: content,
        characterId: characterId,
        hasConversation: !!currentState.conversation,
        conversation: currentState.conversation
    });

    if (!content) {
        showError('Please enter a message');
        return;
    }

    if (!characterId) {
        showError('Please select a character');
        return;
    }

    if (!currentState.conversation) {
        showError('No active conversation. Please create a new story first.');
        return;
    }

    try {
        const formData = new URLSearchParams({
            character_id: characterId,
            content: content
        });

        console.log('Sending manual message:', { character_id: characterId, content: content });

        const response = await fetch('/api/message/manual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Failed to send message:', response.status, errorData);
            throw new Error(errorData.detail || 'Failed to send message');
        }

        document.getElementById('messageInput').value = '';
        await loadState();
        hideThinking();
        
        console.log('Manual message sent, auto_response_enabled:', currentState.auto_response_enabled);
        
        // Auto-generate ONE response from another character if enabled
        if (currentState.auto_response_enabled) {
            console.log('Scheduling ONE AI response after manual message...');
            // Small delay to show the manual message first
            setTimeout(() => {
                console.log('Triggering ONE AI response after manual message');
                generateAIResponse(); // Generate ONE response, then STOP (will show thinking indicator)
            }, 800);
        }
    } catch (error) {
        console.error('Send manual message error:', error);
        showError('Failed to send message: ' + error.message);
    }
}

// Edit message
async function editMessage(index) {
    const message = currentState.conversation.messages[index];
    const newContent = prompt('Edit message:', message.content);

    if (newContent === null) return;

    try {
        const formData = new URLSearchParams({
            content: newContent
        });

        if (message.reaction) {
            const newReaction = prompt('Edit reaction:', message.reaction);
            if (newReaction !== null) {
                formData.append('reaction', newReaction);
            }
        }

        await fetch(`/api/message/${index}/edit`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        await loadState();
        showSuccess('Message edited');
    } catch (error) {
        showError('Failed to edit message');
    }
}

// Regenerate message
async function regenerateMessage() {
    if (!currentState.conversation || !currentState.conversation.messages.length) {
        showError('No messages to regenerate');
        return;
    }

    showStatus('Regenerating...');

    try {
        await fetch('/api/message/regenerate', { method: 'POST' });
        await loadState();
        showStatus('Ready');
    } catch (error) {
        showError('Failed to regenerate message');
    }
}

// Navigate messages
async function navigateMessages(direction) {
    try {
        const formData = new URLSearchParams({ direction });
        const result = await fetch('/api/message/navigate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        }).then(r => r.json());

        await loadState();
        showStatus(`Message ${result.current_index + 1} of ${result.total_messages}`);
    } catch (error) {
        showError('Navigation failed');
    }
}

// Toggle settings
async function toggleSetting(setting, value) {
    try {
        const formData = new URLSearchParams({ setting, value: value.toString() });
        await fetch('/api/settings/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        currentState[setting + '_enabled'] = value;
        
        // Update UI based on setting
        if (setting === 'auto_response') {
            document.getElementById('characterSelect').disabled = value;
        }
    } catch (error) {
        showError('Failed to update setting');
    }
}

// Update scenario
async function updateScenario() {
    const whatHappensNext = document.getElementById('whatHappensNext').value;
    const neverForget = document.getElementById('neverForget').value;

    try {
        const formData = new URLSearchParams();
        if (whatHappensNext) formData.append('what_happens_next', whatHappensNext);
        if (neverForget) formData.append('never_forget', neverForget);

        await fetch('/api/scenario/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        await loadState();
        showSuccess('Scenario updated');
    } catch (error) {
        showError('Failed to update scenario');
    }
}

// Save conversation
async function saveConversation() {
    if (!currentState.conversation) {
        showError('No conversation to save');
        return;
    }

    try {
        const result = await fetch('/api/conversation/save', { method: 'POST' }).then(r => r.json());
        showSuccess(`Saved as ${result.filename}`);
    } catch (error) {
        showError('Failed to save conversation');
    }
}

// Load conversations list
async function loadConversationsList() {
    try {
        const result = await fetch('/api/conversation/list').then(r => r.json());
        const container = document.getElementById('conversationsList');

        if (result.conversations.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #6c757d;">No saved conversations</p>';
            return;
        }

        container.innerHTML = result.conversations.map(conv => `
            <div class="character-card" onclick="loadConversation('${conv.filename}')">
                <div class="character-name">${conv.name}</div>
                <div class="character-desc">
                    ${new Date(conv.created_at).toLocaleDateString()}<br>
                    ${conv.message_count} messages
                </div>
            </div>
        `).join('');
    } catch (error) {
        showError('Failed to load conversations list');
    }
}

// Load conversation
async function loadConversation(filename) {
    try {
        const formData = new URLSearchParams({ filename });
        await fetch('/api/conversation/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        closeModal('loadModal');
        await loadState();
        showSuccess('Conversation loaded');
    } catch (error) {
        showError('Failed to load conversation');
    }
}

// Select character
async function selectCharacter(characterId) {
    console.log('Character card clicked:', characterId);
    
    currentState.selectedCharacterId = characterId;
    document.getElementById('characterSelect').value = characterId;
    
    // Update UI
    document.querySelectorAll('.character-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector(`[data-character-id="${characterId}"]`)?.classList.add('active');
    
    // Automatically generate a response for this character
    if (!currentState.conversation) {
        showError('No active conversation');
        return;
    }
    
    // Get character name for thinking indicator
    const character = currentState.conversation.characters.find(c => c.id === characterId);
    const characterName = character ? character.name : 'Character';
    
    console.log('Generating AI response for character:', characterId);
    showThinking(characterName);
    
    try {
        const formData = new URLSearchParams();
        formData.append('character_id', characterId);

        const response = await fetch('/api/message/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate message');
        }

        await loadState();
        hideThinking();
        console.log('Message generated successfully for:', characterId);
    } catch (error) {
        console.error('Generate message error:', error);
        showError(error.message);
    }
}

// Render conversation
function renderConversation() {
    if (!currentState.conversation) return;

    renderCharacters();
    renderMessages();
    renderScenario();
    renderStats();
}

// Render characters
function renderCharacters() {
    const container = document.getElementById('charactersList');
    const selectElement = document.getElementById('characterSelect');

    if (!currentState.conversation) return;

    container.innerHTML = currentState.conversation.characters.map(char => `
        <div class="character-card ${char.is_narrator ? 'narrator' : ''}" 
             data-character-id="${char.id}"
             onclick="selectCharacter('${char.id}')">
            ${char.image_path ? `<img src="/images/${char.image_path}" class="character-image" alt="${char.name}">` : ''}
            <div class="character-name">${char.name}</div>
            <div class="character-desc">${char.description.substring(0, 100)}...</div>
            ${!char.is_narrator && char.id.startsWith('char') && parseInt(char.id.replace('char', '')) <= 2 ? `
                <input type="file" accept="image/*" onchange="uploadCharacterImage('${char.id}', event)" 
                       style="margin-top: 10px; font-size: 11px;">
            ` : ''}
        </div>
    `).join('');

    selectElement.innerHTML = '<option value="">Select character...</option>' +
        currentState.conversation.characters.map(char => 
            `<option value="${char.id}">${char.name}</option>`
        ).join('');
}

// Upload character image
async function uploadCharacterImage(characterId, event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        await fetch(`/api/character/${characterId}/image`, {
            method: 'POST',
            body: formData
        });

        await loadState();
        showSuccess('Image uploaded');
    } catch (error) {
        showError('Failed to upload image');
    }
}

// Render messages
function renderMessages() {
    const container = document.getElementById('messagesContainer');

    if (!currentState.conversation || !currentState.conversation.messages.length) {
        container.innerHTML = '<div class="loading"><p>No messages yet. Start the conversation!</p></div>';
        return;
    }

    const messagesToShow = currentState.conversation.messages.slice(0, currentState.current_message_index + 1);

    container.innerHTML = messagesToShow.map((msg, index) => {
        const character = currentState.conversation.characters.find(c => c.id === msg.character_id);
        const initials = character ? character.name.substring(0, 2).toUpperCase() : '??';

        return `
            <div class="message">
                <div class="message-header">
                    <div class="message-avatar">${initials}</div>
                    <div class="message-name">${msg.character_name}</div>
                    <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</div>
                </div>
                ${msg.reaction && currentState.show_reactions ? `
                    <div class="message-reaction">${msg.reaction}</div>
                ` : ''}
                <div class="message-content">${msg.content}</div>
                <div class="message-actions">
                    <button onclick="editMessage(${index})">Edit</button>
                </div>
            </div>
        `;
    }).join('');

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Render scenario
function renderScenario() {
    if (!currentState.conversation) return;

    document.getElementById('scenarioDescription').textContent = 
        currentState.conversation.scenario.description;
    document.getElementById('whatHappensNext').value = 
        currentState.conversation.scenario.what_happens_next || '';
    document.getElementById('neverForget').value = 
        currentState.conversation.scenario.never_forget || '';
}

// Render stats
function renderStats() {
    if (!currentState.conversation) return;

    const stats = `
        Messages: ${currentState.conversation.messages.length}<br>
        Characters: ${currentState.conversation.characters.length}<br>
        Summaries: ${currentState.conversation.summaries.length}
    `;

    document.getElementById('stats').innerHTML = stats;
}

// UI helpers
function showStatus(message) {
    const statusBar = document.getElementById('statusBar');
    statusBar.classList.remove('thinking');
    statusBar.innerHTML = message;
}

function showThinking(characterName = null) {
    const statusBar = document.getElementById('statusBar');
    statusBar.classList.add('thinking');
    const message = characterName ? `${characterName} is thinking` : 'AI is thinking';
    statusBar.innerHTML = `
        ${message}
        <div class="thinking-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
}

function hideThinking() {
    const statusBar = document.getElementById('statusBar');
    statusBar.classList.remove('thinking');
    statusBar.textContent = 'Ready';
}

function showError(message) {
    const statusBar = document.getElementById('statusBar');
    statusBar.classList.remove('thinking');
    statusBar.textContent = `Error: ${message}`;
    setTimeout(() => hideThinking(), 3000);
}

function showSuccess(message) {
    const statusBar = document.getElementById('statusBar');
    statusBar.classList.remove('thinking');
    statusBar.textContent = `${message}`;
    setTimeout(() => hideThinking(), 2000);
}

// Refresh messages display
function refreshMessages() {
    if (currentState.conversation) {
        renderMessages();
    }
}
