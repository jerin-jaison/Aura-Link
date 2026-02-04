// Playlist Auto-Play

class VideoPlaylist {
    constructor(videos, loopEnabled = false) {
        this.videos = videos;
        this.currentIndex = 0;
        this.loopEnabled = loopEnabled;
    }
    
    play() {
        if (this.currentIndex < this.videos.length) {
            const video = this.videos[this.currentIndex];
            this.playVideo(video);
        } else if (this.loopEnabled) {
            this.currentIndex = 0;
            this.play();
        } else {
            console.log('Playlist ended');
        }
    }
    
    playVideo(video) {
        console.log('Playing:', video.title);
        // Implement video player logic here
    }
    
    next() {
        this.currentIndex++;
        this.play();
    }
    
    previous() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.play();
        }
    }
}
