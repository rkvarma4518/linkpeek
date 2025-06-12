const socket = io();

let localStream;
let peerConnection;
let currentRoom = null;
const config = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

// Video elements
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');

// Buttons and status
const nextBtn = document.getElementById('nextBtn');
const statusText = document.getElementById('status');
// const chatToggleBtn = document.getElementById('chatToggle');
// const chatSection = document.getElementById('chatSection');

// Chat elements
const messageInput = document.getElementById('chatInput');
const messagesContainer = document.getElementById('chatMessages');


// --- Get user media and start signaling ---
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        localVideo.srcObject = stream;
        localStream = stream;
        socket.emit('join');
    })
    .catch(error => {
        console.error('Error accessing media devices.', error);
    });

// --- Socket.IO signaling events ---
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

// --- Setup WebRTC connection ---
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

// --- Handle next partner button ---
nextBtn.addEventListener('click', () => {
    if (peerConnection) {
        peerConnection.close();
    }
    socket.emit('leave');
    statusText.textContent = "Looking for a new partner...";
    remoteVideo.srcObject = null;
    socket.emit('join');
});

// Send message functionality
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');

function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        const msgDiv = document.createElement('div');
        msgDiv.textContent = "You: " + message;
        chatMessages.appendChild(msgDiv);
        chatInput.value = '';
        chatInput.focus();
        socket.emit('send_message', message);
    }
}

chatInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

socket.on('receive_message', (message) => {
    const msgDiv = document.createElement('div');
    msgDiv.textContent = message;
    chatMessages.appendChild(msgDiv);
});

