document.addEventListener('DOMContentLoaded', () => {
    const openModalBtn = document.getElementById('open-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const modalOverlay = document.getElementById('video-modal');
    const modalVideo = document.getElementById('modal-video');

    const videoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ'; // Placeholder URL

    const openModal = () => {
        modalVideo.src = videoUrl;
        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    };

    const closeModal = () => {
        modalVideo.src = ''; // Stop video playback
        modalOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    };

    if (openModalBtn) {
        openModalBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal();
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }
});
