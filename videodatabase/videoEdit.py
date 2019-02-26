from .models import EditedVideo, ShotElement


def videoAnalysis(videoName):
    shots = []
    editedVideo = EditedVideo.objects.create(jumpArg=0, speedArg=1, positionArg=1, cramArg=1, colorArg=1)
    shot1 = ShotElement.objects.create(start=0, end=2, during=2, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot2 = ShotElement.objects.create(start=2, end=3, during=1, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=0, editedVideo=editedVideo)
    shot3 = ShotElement.objects.create(start=3, end=8, during=5, speed=[0, 1], position=[1, 1], craMotion=[1, 1],
                        color=[0, 0], shotSize=3, editedVideo=editedVideo)
    shot4 = ShotElement.objects.create(start=8, end=10, during=2, speed=[1, 0], position=[1, 1], craMotion=[1, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot5 = ShotElement.objects.create(start=10, end=12, during=2, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shot6 = ShotElement.objects.create(start=12, end=15, during=3, speed=[0, 0], position=[1, 1], craMotion=[0, 0],
                        color=[0, 0], shotSize=1, editedVideo=editedVideo)
    shots.extend([shot1, shot2, shot3, shot4, shot5, shot6])
    return editedVideo


def VideoMerge(fileNames, timeTemplete, editedVideo):  # 自动视频组接
    return "file.mp4"
