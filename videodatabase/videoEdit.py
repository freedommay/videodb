from .models import EditedVideo, ShotElement


def videoAnalysis(videoName):
    shots = []
    editedVideo = EditedVideo(jumpArg=0, speedArg=1, positionArg=1, cramArg=1, colorArg=1)
    editedVideo.save()
    shot1 = ShotElement(start=0, end=2, during=2, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot1.save()
    shots.append(shot1)
    shot2 = ShotElement(start=2, end=3, during=1, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=0, editedVideo=editedVideo)
    shot2.save()
    shots.append(shot2)
    shot3 = ShotElement(start=3, end=8, during=5, speed=[0, 1], position=[1, 1], craMotion=[1, 1],
                        color=[0, 0], shotSize=3, editedVideo=editedVideo)
    shot3.save()
    shots.append(shot3)
    shot4 = ShotElement(start=8, end=10, during=2, speed=[1, 0], position=[1, 1], craMotion=[1, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot4.save()
    shots.append(shot4)
    shot5 = ShotElement(start=10, end=12, during=2, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot5.save()
    shots.append(shot5)
    shot6 = ShotElement(start=12, end=15, during=3, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot6.save()
    shots.append(shot6)
    return editedVideo


def VideoMerge(fileNames, timeTemplete, editedVideo):  # 自动视频组接
    # timeTemplete list
    # editedVideo EditedVideo
    return "file.mp4"  # return string
