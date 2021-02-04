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

def doesCommentContainStevie(commentObj):
    # If comment does NOT contain "stevie" 
    # AND author does contain "steve"
    # return false
    return

# TODO: 
# - Add replies that contain "stevie"
# If topComment does contain "stevie", add all replies
# Else only add replies that contain "stevie"
# If totalReplies is more than array of replies, use
# comments.list() with parentID parameter to retrieve all replies
def getStevieVideoData(youtube_object, videoID):
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
            part="snippet",
            videoId=videoID,
            maxResults=3,
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
            totalComments += response['pageInfo']['totalResults']
            for commentThread in response['items']:
                # Comment
                comment = commentThread['snippet']['topLevelComment']['snippet']['textDisplay']
                # Likes
                likes = commentThread['snippet']['topLevelComment']['snippet']['likeCount']
                # Replies
                replies = commentThread['snippet']['totalReplyCount']
                # Comment Obj
                comments.append({
                    "comment": comment,
                    "likes": likes,
                    "replies": replies
                })
                # Total Likes
                totalLikes += likes
                # Total Replies
                totalReplies += replies

        # Check for next page
        isNextPage = response and 'nextPageToken' in response.keys()

    # Function to sort comments to pass into sort()
    def sortComments(comment):
        return comment['likes']

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

    # Get comment threads from video
    request = youtube_object.commentThreads().list(
        part="snippet",
        videoId=videoID,
        maxResults=100,
        order="relevance",
        searchTerms="stevie"
    )
    try:
        response = request.execute()
    except:
        print("CommentThread request has error for video ID: " + videoID)
        response = False

    if response and response['items']:
        totalComments += response['pageInfo']['totalResults']
        for commentThread in response['items']:
            # Comment
            comment = commentThread['snippet']['topLevelComment']['snippet']['textDisplay']
            # Likes
            likes = commentThread['snippet']['topLevelComment']['snippet']['likeCount']
            # Replies
            replies = commentThread['snippet']['totalReplyCount']
            # Comment Obj
            comments.append({
                "comment": comment,
                "likes": likes,
                "replies": replies
            })
            # Total Likes
            totalLikes += likes
            # Total Replies
            totalReplies += replies

        # While 'nextPageToken' key is in response, add commentThreads on next page
        while 'nextPageToken' in response.keys():
            request = youtube_object.commentThreads().list(
                part="snippet",
                videoId=videoID,
                maxResults=100,
                order="relevance",
                searchTerms="stevie",
                pageToken=response['nextPageToken']
            )
            response = request.execute()

            if response['items']:
                totalComments += response['pageInfo']['totalResults']
                for commentThread in response['items']:
                    # Comment
                    comment = commentThread['snippet']['topLevelComment']['snippet']['textDisplay']
                    # Likes
                    likes = commentThread['snippet']['topLevelComment']['snippet']['likeCount']
                    # Replies
                    replies = commentThread['snippet']['totalReplyCount']
                    # Comment Obj
                    comments.append({
                        "comment": comment,
                        "likes": likes,
                        "replies": replies
                    })
                    # Total Likes
                    totalLikes += likes
                    # Total Replies
                    totalReplies += replies

        # Function to sort comments to pass into sort()
        def sortComments(comment):
            return comment['likes']

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

def findStevieVideosFromIDList(videoList):
    # Create YouTube Resource Object
    youtube_object = createYouTubeResourceObject()

    stevieVideoList = []
    videoCount = 0

    for videoID in videoList:
        # Append video info to Stevie video list
        stevieVideoList.append(
            getStevieVideoData(youtubeyoutube_object, videoID)
        )
        
        videoCount += 1
        if videoCount % 50 == 0:
            print(str(videoCount) + " videos finished")
    
    return stevieVideoList

def findGMMStevieVideos():
    # Open JSON array from local file and save to python list
    with open('gmmVideoList.json', 'r') as outfile:
        videoList = json.load(outfile)

    stevieVideoList = findStevieVideosFromIDList(videoList)

    print("List length " + str(len(stevieVideoList)))
    with open('gmmStevieVideoList.json', 'w') as outfile:
        json.dump(stevieVideoList, outfile)

def findGMMoreStevieVideos():
    # Open JSON array from local file and save to python list
    with open('gmMoreVideoList.json', 'r') as outfile:
        videoList = json.load(outfile)

    stevieVideoList = findStevieVideosFromIDList(videoList)

    print("List length " + str(len(stevieVideoList)))
    with open('gmMoreStevieVideoList.json', 'w') as outfile:
        json.dump(stevieVideoList, outfile)

def sortStevieVideoList(videoList):
    # TODO:
    # - Remove videos with NO comments
    # - Remove comments that do NOT include "stevie"

    def sortComments(val):
        return val['totalComments']

    videoList.sort(key=sortComments, reverse=True)

def sortGMMStevieVideoList():
    # Open JSON array from local file and save to python list
    with open('gmmStevieVideoList.json', 'r') as outfile:
        videoList = json.load(outfile)

    sortStevieVideoList(videoList)

    with open('gmmStevieVideoListSorted.json', 'w') as outfile:
        json.dump(videoList, outfile)

def sortGMMoreStevieVideoList():
    # Open JSON array from local file and save to python list
    with open('gmMoreStevieVideoList.json', 'r') as outfile:
        videoList = json.load(outfile)

    sortStevieVideoList(videoList)

    with open('gmMoreStevieVideoListSorted.json', 'w') as outfile:
        json.dump(videoList, outfile)

def getGMMVideos():
    # Create Youtube Resource Object 
    youtube_object = createYouTubeResourceObject()

    # Channel ID: UC4PooiX37Pld1T8J5SYT-SQ
    # Uploads Playlist ID: UU4PooiX37Pld1T8J5SYT-SQ

    channelID = "UC4PooiX37Pld1T8J5SYT-SQ"
    uploadsPlaylistID = getUploadsPlaylistID(channelID, youtube_object)

    videoIDList = getPlaylistVideos(uploadsPlaylistID, youtube_object)

    with open('gmmVideoList.json', 'w') as outfile:
        json.dump(videoIDList, outfile)

    print("Number of videos: " + str(len(videoIDList)))

def getGMMMoreVideos():
    # Create Youtube Resource Object 
    youtube_object = createYouTubeResourceObject()

    # Channel ID: UCzpCc5n9hqiVC7HhPwcIKEg
    # Uploads Playlist ID: UUzpCc5n9hqiVC7HhPwcIKEg

    channelID = "UCzpCc5n9hqiVC7HhPwcIKEg"
    uploadsPlaylistID = getUploadsPlaylistID(channelID, youtube_object)

    videoIDList = getPlaylistVideos(uploadsPlaylistID, youtube_object)

    with open('gmMoreVideoList.json', 'w') as outfile:
        json.dump(videoIDList, outfile)

    print("Number of videos: " + str(len(videoIDList)))

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
    #getGMMVideos()
    #findGMMStevieVideos()
    #sortGMMStevieVideoList()

    # Good Mythical More
    #getGMMMoreVideos()
    #findGMMoreStevieVideos()
    #sortGMMoreStevieVideoList()

    # TESTING
    youtube_object = createYouTubeResourceObject()
    print(
        json.dumps(
            getStevieVideoData(youtube_object, "vehmN2OZ_SQ"),
            indent=4
        )
    )

    # Elapsed Time - End
    timeElapsed = time.time() - startTime
    print('\nTime Elapsed: ', math.floor(timeElapsed / 60), 'min:', math.floor(timeElapsed % 60), 'sec')