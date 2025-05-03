const socket = io();
let localStream;
let peerConnection;
let currentRoom = null;
const config = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const nextBtn = document.getElementById('nextBtn');
const statusText = document.getElementById('status');

navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        localVideo.srcObject = stream;
        localStream = stream;
        socket.emit('join');
    })
    .catch(error => {
        console.error('Error accessing media devices.', error);
    });

socket.on('match', (room) => {
    statusText.textContent = "Connected!";
    currentRoom = room;
    setupPeerConnection();
    createOffer();
});

socket.on('offer', async (offer) => {
    setupPeerConnection();
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', { answer: peerConnection.localDescription, room: currentRoom });
});

socket.on('answer', async (answer) => {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
});

socket.on('ice-candidate', async (candidate) => {
    try {
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    } catch (e) {
        console.error('Error adding received ice candidate', e);
    }
});

function setupPeerConnection() {
    peerConnection = new RTCPeerConnection(config);

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('ice-candidate', { candidate: event.candidate, room: currentRoom });
        }
    };

    peerConnection.ontrack = (event) => {
        remoteVideo.srcObject = event.streams[0];
    };

    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
}

async function createOffer() {
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    socket.emit('offer', { offer: peerConnection.localDescription, room: currentRoom });
}

nextBtn.addEventListener('click', () => {
    if (peerConnection) {
        peerConnection.close();
    }
    socket.emit('leave');
    statusText.textContent = "Looking for a new partner...";
    remoteVideo.srcObject = null;
    socket.emit('join');
});






// Reference to the chat elements
const messageInput = document.getElementById('messageInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');
const messagesContainer = document.getElementById('messages');

// Event listener for sending a message
sendMessageBtn.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        // Emit message to the server
        socket.emit('send_message', message);
        // Display message locally
        appendMessage('You: ' + message);
        messageInput.value = ''; // Clear input field
    }
});

// Listen for incoming messages from the server
socket.on('receive_message', (message) => {
    appendMessage(message);
});

// Function to append message to the message container
function appendMessage(message) {
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
}

// Trigger send on Enter key
messageInput.addEventListener('keydown', function (event) {
    if (event.key == 'Enter') {
        event.preventDefault(); // Prevent newline if using textarea
        const message = messageInput.value.trim();
        if (message) {
            // Emit message to the server
            socket.emit('send_message', message);
            // Display message locally
            appendMessage('You: ' + message);
            messageInput.value = ''; // Clear input field
        }
    }
});

// Send button click
sendButton.addEventListener('click', sendMessage);
