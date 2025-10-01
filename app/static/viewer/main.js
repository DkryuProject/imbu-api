import { initViewer, loadModel } from './viewer.js';

const urn = getUrnFromUrl();

function urnify(id) {
    return btoa(id).replace(/=/g, '');
}

function getUrnFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('urn'); // 없으면 null 반환
}

initViewer(document.getElementById('preview'), urn).then(viewer => {
    //const urn = window.location.hash?.substring(1);
    //setupModelSelection(viewer, urn);
    //setupModelUpload(viewer);
    if (urn) {
        console.log("Viewer initialized");
        loadModel(viewer, urn);
    }
});

function showNotification(message) {
    const overlay = document.getElementById('overlay');
    overlay.innerHTML = `<div class="notification">${message}</div>`;
    overlay.style.display = 'flex';
}

function clearNotification() {
    const overlay = document.getElementById('overlay');
    overlay.innerHTML = '';
    overlay.style.display = 'none';
}