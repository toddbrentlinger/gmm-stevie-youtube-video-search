"use strict";

import { loadPlayerAPI } from './youtubePlayerController.js';
import { VideoElement } from './videoElement.js';

let requestURL = "./gmmStevieVideoListSorted.json";
let request = new XMLHttpRequest();
request.open('GET', requestURL);

request.responseType = 'json';
request.send();

request.onload = function () {
    let stevieVideoArr = request.response;
    stevieVideoArr.sort((first, second) => {
        // If comments are equal, sort by likes
        return (first.comments === second.comments)
            ? second.likes - first.likes
            : second.comments - first.comments;
    });

    // Create array of VideoElement objects for each video
    stevieVideoArr = stevieVideoArr.map(
        (videoObj, index) => new VideoElement(videoObj, setLastVideoWatched, index)
    );

    let rootElement = document.getElementById('root');
    rootElement = rootElement.appendChild(document.createElement('ol'));
    /*
    stevieVideoArr.forEach(video => {
        rootElement.appendChild(video.htmlElement);
    });
    */
    // Create array of VideoElement objects for first 10 videos
    let startIndex = 0;
    let resultsPerPage = 10;
    for (let i = startIndex; i < startIndex + resultsPerPage; i++) {
        rootElement.appendChild(stevieVideoArr[i].createVideoElement());
    }

    setLastVideoWatched();
};

function setLastVideoWatched(index) {
    const tempElement = document.getElementById('last-video-watched');

    let tempStr = "Last video index watched: ";
    if (index === undefined) {
        tempStr += window.localStorage.getItem('lastVideoIndex');
    } else {
        tempStr += index + 1;
        window.localStorage.setItem('lastVideoIndex', index + 1);
    }
    tempElement.innerHTML = tempStr;
}
