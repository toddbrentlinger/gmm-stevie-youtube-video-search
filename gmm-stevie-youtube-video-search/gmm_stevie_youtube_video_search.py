import json
import time
import math

from apiclient.discovery import build

import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def createYouTubeResourceObject():
    # Arguments that need to passed to the build function 
    with open('../../youtube_developer_key.json', 'r') as outfile:
        DEVELOPER_KEY = json.load(outfile)['dev_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
   
    # creating Youtube Resource Object 
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEY)

def getCommentThreadReplies(commentThread, youtube_object, isStevieNotInTopLevelComment):
    # If totalReplyCount is zero, return empty array
    if (not commentThread['snippet']['totalReplyCount']):
        return []

    replyObjArr = []
    # If totalReplyCount is more than replies array, use comments.list() to get replies
    if (commentThread['snippet']['totalReplyCount'] != len(commentThread['replies']['comments'])):
        isNextPage = True
        response = False
        while (isNextPage):
            # Get comment threads from video
            request = youtube_object.comments().list(
                part="snippet",
                parentId=commentThread['snippet']['topLevelComment']['id'],
                maxResults=100,
                pageToken=response['nextPageToken'] if response and isNextPage else ""
            )
            try:
                response = request.execute()
            except:
                print("CommentThread request has error for video ID: " + videoID)
                response = False

            if response and response['items']:
                for reply in response['items']:
                    replyObjArr.append(reply)

            # Check for next page
            isNextPage = response and 'nextPageToken' in response.keys()

    # Else use replies from commentThread object
    else:
        replyObjArr = commentThread['replies']['comments']

    replies = []
    for reply in replyObjArr:
        replyText = reply['snippet']['textDisplay']
        authorName = reply['snippet']['authorDisplayName']

        # If "stevie" NOT in top level comment text
        # AND "stevie" NOT in reply text
        # continue
        if isStevieNotInTopLevelComment and 'stevie' not in replyText.lower():
            continue

        replies.append({
            "reply": replyText,
            "authorName": authorName,
            "likeCount": reply['snippet']['likeCount']
        })

    # Function to sort replies to pass into sort()
    def sortReplies(val):
        return val['likeCount']
    # Sort replies by likes in decreasing order
    replies.sort(key=sortReplies, reverse=True)

    # Keep top 20 replies after sort
    if (len(replies) > 20):
        replies = replies[:20]

    # Return replies array
    return replies

# TODO: 
# - Add replies that contain "stevie"
# If topComment does contain "stevie", add all replies
# Else only add replies that contain "stevie"
# If totalReplies is more than array of replies, use
# comments.list() with parentID parameter to retrieve all replies
def getStevieVideoData(videoObj, youtube_object):
    # Variables
    totalComments = 0
    totalLikes = 0
    totalReplies = 0
    comments = []

    # Title
    title = videoObj['snippet']['title']
    # Description
    description = videoObj['snippet']['description']
    # PublishedAt
    publishedAt = videoObj['snippet']['publishedAt']
    # Thumbnails
    thumbnails = videoObj['snippet']['thumbnails']
    # Views
    videoViewCount = int(videoObj['statistics'].get('viewCount', 0))
    # Likes
    videoLikeCount = int(videoObj['statistics'].get('likeCount', 0))
    # Dislikes
    videoDislikeCount = int(videoObj['statistics'].get('dislikeCount', 0))

    isNextPage = True
    response = False
    while (isNextPage):
        # Get comment threads from video
        request = youtube_object.commentThreads().list(
            part="snippet, replies",
            videoId=videoObj['id'],
            maxResults=100,
            order="relevance",
            searchTerms="stevie",
            pageToken=response['nextPageToken'] if response and isNextPage else ""
        )
        try:
            response = request.execute()
        except:
            print("CommentThread request has error for video ID: " + videoObj['id'])
            response = False

        if response and response['items']:
            for commentThread in response['items']:
                # Top Level Comment
                topLevelComment = commentThread['snippet']['topLevelComment']['snippet']['textDisplay']
                # Author - Top Level Comment
                authorName = commentThread['snippet']['topLevelComment']['snippet']['authorDisplayName']
                
                # Continue if "stevie" NOT in top level comment AND author includes "steve"
                #if 'stevie' not in topLevelComment.lower() and 'steve' in authorName.lower():
                #    continue
                
                # Likes - Top Level Comment
                likeCount = commentThread['snippet']['topLevelComment']['snippet']['likeCount']
                # Replies - Top Level Comment
                replyCount = commentThread['snippet']['totalReplyCount']
                replies = getCommentThreadReplies(
                    commentThread, 
                    youtube_object, 
                    'stevie' not in topLevelComment.lower()
                )

                # Continue if "stevie" NOT in top level comment AND replies is empty
                if 'stevie' not in topLevelComment.lower() and not replies:
                    continue

                # Comment Obj
                comments.append({
                    "topLevelComment": topLevelComment,
                    "authorName": authorName,
                    "likeCount": likeCount,
                    "replyCount": replyCount,
                    "replies": replies
                })
                # Total Comments
                totalComments += 1
                # Total Likes
                totalLikes += likeCount
                # Total Replies
                totalReplies += replyCount

        # Check for next page
        isNextPage = response and 'nextPageToken' in response.keys()

    # Function to sort comments to pass into sort()
    def sortComments(comment):
        return comment['likeCount']

    # Sort comments by likes in decreasing order
    comments.sort(key=sortComments, reverse=True)

    # Keep first top 100 comments after sort
    if (len(comments) > 100):
        comments = comments[:100]

    # Return video info
    return {
        "videoId": videoObj['id'],
        "title": title,
        "description": description,
        "publishedAt": publishedAt,
        "thumbnails": thumbnails,
        "viewCount": videoViewCount,
        "likeCount": videoLikeCount,
        "dislikeCount": videoDislikeCount,
        "totalComments": totalComments,
        "totalCommentLikes": totalLikes,
        "totalCommentReplies": totalReplies,
        "comments": comments,
    }

def getStevieVideoDataOld(youtube_object, videoID):
    # Variables
    title = ""
    description = ""
    thumbnails = []
    totalComments = 0
    totalLikes = 0
    totalReplies = 0
    comments = []

    # Get title, description, and thumbnails
    request = youtube_object.videos().list(
        part="snippet",
        id=videoID
    )
    try:
        response = request.execute()
    except:
        print("Video request has error for video ID: " + videoID)
        response = False

    if response and response['items']:
        # Title
        title = response['items'][0]['snippet']['title']
        # Description
        description = response['items'][0]['snippet']['description']
        # Thumbnails
        thumbnails = response['items'][0]['snippet']['thumbnails']

    isNextPage = True
    response = False
    while (isNextPage):
        # Get comment threads from video
        request = youtube_object.commentThreads().list(
            part="snippet, replies",
            videoId=videoID,
            maxResults=100,
            order="relevance",
            searchTerms="stevie",
            pageToken=response['nextPageToken'] if response and isNextPage else ""
        )
        try:
            response = request.execute()
        except:
            print("CommentThread request has error for video ID: " + videoID)
            response = False

        if response and response['items']:
            for commentThread in response['items']:
                # Top Level Comment
                topLevelComment = commentThread['snippet']['topLevelComment']['snippet']['textDisplay']
                # Author - Top Level Comment
                authorName = commentThread['snippet']['topLevelComment']['snippet']['authorDisplayName']
                
                # Continue if "stevie" NOT in top level comment AND author includes "steve"
                #if 'stevie' not in topLevelComment.lower() and 'steve' in authorName.lower():
                #    continue
                
                # Likes - Top Level Comment
                likeCount = commentThread['snippet']['topLevelComment']['snippet']['likeCount']
                # Replies - Top Level Comment
                replyCount = commentThread['snippet']['totalReplyCount']
                replies = getCommentThreadReplies(
                    commentThread, 
                    youtube_object, 
                    'stevie' not in topLevelComment.lower()
                )

                # Continue if "stevie" NOT in top level comment AND replies is empty
                if 'stevie' not in topLevelComment.lower() and not replies:
                    continue

                # Comment Obj
                comments.append({
                    "topLevelComment": topLevelComment,
                    "authorName": authorName,
                    "likeCount": likeCount,
                    "replyCount": replyCount,
                    "replies": replies
                })
                # Total Comments
                totalComments += 1
                # Total Likes
                totalLikes += likeCount
                # Total Replies
                totalReplies += replyCount

        # Check for next page
        isNextPage = response and 'nextPageToken' in response.keys()

    # Function to sort comments to pass into sort()
    def sortComments(comment):
        return comment['likeCount']

    # Sort comments by likes in decreasing order
    comments.sort(key=sortComments, reverse=True)

    # Keep first top 100 comments after sort
    if (len(comments) > 100):
        comments = comments[:100]

    # Return video info
    return {
        "videoId": videoID,
        "title": title,
        "description": description,
        "thumbnails": thumbnails,
        "totalComments": totalComments,
        "totalLikes": totalLikes,
        "totalReplies": totalReplies,
        "comments": comments,
    }

# Returns JSON object of Stevie videos data from list of
# YouTube video ID's.
def findStevieVideosFromIDList(videoList):
    # Create YouTube Resource Object
    youtube_object = createYouTubeResourceObject()

    stevieVideoList = []
    videoCount = 0

    totalVideos = len(videoList)
    i = 0
    while (i < totalVideos):
        # Create string of 50 incremented, comma separated, video ID's
        videoIDListStr = ",".join(videoList[i:(min(i+50, totalVideos))])

        request = youtube_object.videos().list(
            part="snippet,statistics",
            id=videoIDListStr
        )
        try:
            response = request.execute()
        except:
            print("Video request has error for videos at index: " + str(i) + "-" + str(i+50))
            response = False

        if response and response['items']:
            for videoObj in response['items']:
                # Append video info to Stevie video list
                stevieVideoList.append(
                    getStevieVideoData(videoObj, youtube_object)
                )
        
                videoCount += 1
                if videoCount % 50 == 0:
                    print(str(videoCount) + " videos finished")
        # Increment index by 50
        i += 50
    
    print("Created " + str(videoCount) + " video objects from " + str(len(videoList)) + " video IDs")

    return stevieVideoList

# Takes list of YouTube video ID's from readFile and creates JSON
# file of Stevie videos data in writeFile.
def findStevieVideos(readFile, writeFile):
    # Open JSON array from local file and save to python list
    with open(readFile, 'r') as outfile:
        videoList = json.load(outfile)

    stevieVideoList = findStevieVideosFromIDList(videoList)
    
    print("List length " + str(len(stevieVideoList)))
    with open(writeFile, 'w') as outfile:
        json.dump(stevieVideoList, outfile)

# Takes JSON file of Stevie videos data and creates JSON file of
# sorted Stevie videos data.
def sortStevieVideoList(readFile, writeFile):
    # Open JSON array from local file and save to python list
    with open(readFile, 'r') as outfile:
        videoList = json.load(outfile)

    # Sort function to pass into sort()
    def sortComments(val):
        return val['totalComments']
    # Sort videos by totalComments in decreasing order
    videoList.sort(key=sortComments, reverse=True)

    # Filter to only include videos with comments
    videoList = list(filter(lambda video: video['totalComments'], videoList))

    with open(writeFile, 'w') as outfile:
        json.dump(videoList, outfile)

# Creates file of list of video ID's from YouTube channel uploads.
def getYouTubeChannelVideoIDs(channelID, writeFile):
    # Create Youtube Resource Object 
    youtube_object = createYouTubeResourceObject()

    uploadsPlaylistID = getUploadsPlaylistID(channelID, youtube_object)

    videoIDList = getPlaylistVideos(uploadsPlaylistID, youtube_object)

    with open(writeFile, 'w') as outfile:
        json.dump(videoIDList, outfile)

    print("Number of videos: " + str(len(videoIDList)))

# Returns Playlist ID of YouTube channel uploads.
def getUploadsPlaylistID(channelID, youtube_object):
    request = youtube_object.channels().list(
        part="statistics, contentDetails",
        id=channelID
    )
    response = request.execute()

    if response['items']:
        print("Video Count: " + response['items'][0]['statistics']['videoCount'])
        print("Playlist ID: " + response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])

        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Returns list of YouTube video ID's in playlist.
def getPlaylistVideos(id, youtube_object):
    request = youtube_object.playlistItems().list(
        part="contentDetails",
        playlistId=id,
        maxResults=50
    )
    response = request.execute()

    videoIDList = []
    if response['items']:
        for video in response['items']:
            videoIDList.append(video['contentDetails']['videoId'])
        print("NextPageToken: " + response['nextPageToken'])
        # While 'nextPageToken' key is in response, add videos on next page
        while 'nextPageToken' in response.keys():
            request = youtube_object.playlistItems().list(
                part="contentDetails",
                playlistId=id,
                maxResults=50,
                pageToken=response['nextPageToken']
            )
            response = request.execute()

            if response['items']:
                for video in response['items']:
                    videoIDList.append(video['contentDetails']['videoId'])
        
    return videoIDList


if __name__ == "__main__":
    # Elapsed Time - Start
    startTime = time.time()

    # Good Mythical Morning
    # Channel ID: UC4PooiX37Pld1T8J5SYT-SQ
    # Uploads Playlist ID: UU4PooiX37Pld1T8J5SYT-SQ
    #getYouTubeChannelVideoIDs('UC4PooiX37Pld1T8J5SYT-SQ', 'gmmVideoList.json')
    findStevieVideos('gmmVideoList.json', 'gmmStevieVideoList.json')
    sortStevieVideoList('gmmStevieVideoList.json', 'gmmStevieVideoListSorted.json')

    # Good Mythical More
    # Channel ID: UCzpCc5n9hqiVC7HhPwcIKEg
    # Uploads Playlist ID: UUzpCc5n9hqiVC7HhPwcIKEg
    #getYouTubeChannelVideoIDs('UCzpCc5n9hqiVC7HhPwcIKEg', 'gmMoreVideoList.json')
    #findStevieVideos('gmMoreVideoList.json', 'gmMoreStevieVideoList.json')
    #sortStevieVideoList('gmMoreStevieVideoList.json', 'gmMoreStevieVideoListSorted.json')

    # TESTING
    #youtube_object = createYouTubeResourceObject()
    #print(
    #    json.dumps(
    #        getStevieVideoData(youtube_object, "JAXuhhDaXPM"),
    #        indent=4
    #    )
    #)
    #request = youtube_object.videos().list(
    #    part="snippet,statistics",
    #    id="-qc0JnXyBAk"
    #)
    #try:
    #    response = request.execute()
    #except:
    #    print("Video request has error for video")
    #    response = False

    #if response and response['items']:
    #    videoObj = response['items'][0]
    #    videoObj = getStevieVideoData(videoObj, youtube_object)
    #    print(json.dumps(videoObj, indent=4))

    # Elapsed Time - End
    timeElapsed = time.time() - startTime
    print('\nTime Elapsed: ', math.floor(timeElapsed / 60), 'min:', math.floor(timeElapsed % 60), 'sec')