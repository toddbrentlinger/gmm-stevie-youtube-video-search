"use strict";

/* TODO:
 * - Max video count in playlist viewer is 200. Create function that 
 * will play an array of videos in 200 video increments. After 200th
 * episode ends, change playlist to view next 200 videos in array.
 * Perhaps wait until video 150 finishes to create new playlist in
 * order to leave 50 episodes in playlist to view what is next. Similar
 * function to display 
 */

// Load the IFrame Player API code asynchronously.
export function loadPlayerAPI() {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/player_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // This function creates an <iframe> (and YouTube player)
    // after the API code downloads.
    window.onYouTubePlayerAPIReady = function () {
        replayEpisodeCollection.videoPlayer = new YT.Player('youtubePlayerPlaceholder', {
            height: 360,
            width: 640,
            //videoId: '0ZtEkX8m6yg', // default video: Replay Highlights
            playerVars: {
                playlist: [replayEpisodeCollection.selectedVideoIdArray.slice(0, 200) || '0ZtEkX8m6yg'],
                iv_load_policy: 3, // video annotations (default: 1)
                modestbranding: 1,
                enablejsapi: 1,
                loop: 0,
                origin: 'https://toddbrentlinger.github.io/Game-Informer-Replay-Website/Game-Informer-Replay-Website/'
            },
            events: {
                onReady: replayEpisodeCollection.onPlayerReady.bind(replayEpisodeCollection),
                //onStateChange: replayEpisodeCollection.onPlayerStateChange.bind(replayEpisodeCollection),
                onError: replayEpisodeCollection.onPlayerError.bind(replayEpisodeCollection)
            }
        });

        //console.log('window.onYouTubePlayerAPIReady() has finished');
    };
}