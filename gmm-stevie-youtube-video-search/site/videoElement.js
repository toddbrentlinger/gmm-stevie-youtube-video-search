"use strict";

export class VideoElement {
    /**
     * @constructor
     * @param {any} jsonObj
     */
    constructor(jsonObj, setLastVideoWatched, index) {
        this.jsonObj = jsonObj;
        // Create HTML element
        this.createVideoElement(setLastVideoWatched, index);
    }
    get videoId() {
        return this.jsonObj.videoId;
    }
    get title() {
        return this.jsonObj.title;
    }
    get description() {
        return this.jsonObj.description;
    }
    get totalComments() {
        return this.jsonObj.totalComments;
    }
    get totalLikes() {
        return this.jsonObj.totalLikes;
    }
    get totalReplies() {
        return this.jsonObj.totalReplies;
    }

    createElementSimple(innerHTML, classList, tag = 'div') {
        let tempElement = document.createElement(tag);
        tempElement.classList.add(classList);
        tempElement.innerHTML = innerHTML;
        return tempElement;
    }

    createVideoElement(setLastVideoWatched, index) {
        const rootElement = document.createElement('li');
        rootElement.classList.add('video-container');
        // Title
        rootElement.appendChild(this.createElementSimple(this.title, 'title', 'h2'));
        // YouTube Link
        let tempElement = rootElement.appendChild(document.createElement('a'));
        tempElement.href = `https://www.youtube.com/watch?v=${this.videoId}`;
        tempElement.innerHTML = "YouTube Link";
        tempElement.target = '_blank';
        tempElement.onclick = () => {
            setLastVideoWatched(index);
        };
        // Description
        const newDesc = this.description.split("\n")[0]
        rootElement.appendChild(this.createElementSimple(newDesc, 'description', 'p'));
        // Comments
        rootElement.appendChild(
            this.createElementSimple(
                "Total Stevies Comments: " + this.totalComments, 'total-comments'
            )
        );
        // Likes
        rootElement.appendChild(
            this.createElementSimple(
                "Total Likes: " + this.totalLikes, 'total-likes'
            )
        );
        // Replies
        rootElement.appendChild(
            this.createElementSimple(
                "Total Replies: " + this.totalReplies, 'total-replies'
            )
        );

        //this.htmlElement = rootElement;
        return rootElement;
    }
}