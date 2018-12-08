import json
import os

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from moviepy.editor import VideoFileClip

from videodb import settings
from . import videoEdit
from .models import EditedVideo, Clip
from .video import GeneratedEditedVideo
from .shotelement import GeneratedShotElement


def home(request):
    video_list = EditedVideo.objects.all().order_by('-id')
    videos = paginate(request, video_list)
    context = get_context(request)
    context['videos'] = videos
    return render(request, 'videodatabase/home.html', context)


def upload(request):
    return render(request, 'videodatabase/upload.html')


def analysis_video(request):
    video = get_video(request)
    return HttpResponseRedirect(reverse('detail', args=(video.id,)))


def get_video(request):
    if request.method == 'POST':
        name = request.FILES['video'].name
        name = name.split('.')[0]
        file = request.FILES.get('video')
        file_path = file.temporary_file_path()
        editedvideo = videoEdit.videoAnalysis(file_path)
        editedvideo.url = file
        editedvideo.name = name
        editedvideo.container = request.POST.get('select1')
        editedvideo.scenes = request.POST.get('select2')
        editedvideo.productCategory = request.POST.get('select3')
        editedvideo.save()
        path = editedvideo.url.path
        clip = VideoFileClip(path)
        editedvideo.duration = clip.duration
        clip.reader.close()
        clip.audio.reader.close_proc()
        editedvideo.save()
        return editedvideo


def paginate(request, list):
    paginator = Paginator(list, 5)
    page = request.GET.get('page')
    videos = paginator.get_page(page)
    return videos


def get_context(request):
    """
    视频载体 手机 1 电视 2
    业务场景  商品上新 1 促销 2 品牌宣传 3
    产品品类 男装 1 女装 2
    """
    total_amount = EditedVideo.objects.all().count()
    mobile_amount = EditedVideo.objects.filter(container=1).count()
    television_amount = EditedVideo.objects.filter(container=2).count()
    new_amount = EditedVideo.objects.filter(scenes=1).count()
    promotion_amount = EditedVideo.objects.filter(scenes=2).count()
    advertisement_amount = EditedVideo.objects.filter(scenes=3).count()
    men_clothing_amount = EditedVideo.objects.filter(productCategory=1).count()
    women_clothing_amount = EditedVideo.objects.filter(productCategory=2).count()
    context = {
        'total_amount': total_amount,
        'mobile_amount': mobile_amount,
        'television_amount': television_amount,
        'new_amount': new_amount,
        'promotion_amount': promotion_amount,
        'advertisement_amount': advertisement_amount,
        'men_clothing_amount': men_clothing_amount,
        'women_clothing_amount': women_clothing_amount,
    }
    return context


def detail(request, video_id):
    """
    ----首尾镜头----
    景别： 特写 0 近景 1 中景 2 远景 3
    主体运动强度 弱 0 中 1 强 2
    主体位置 右 0 中 1 左 2
    色调 暖 0 中 1 冷 2
    镜头运动强度 弱 0 中 1 强 2
    ----视频----
    主体运动变化 大 0 小 1
    主体位置变化 大 0 小 1
    镜头运动变化 大 0 小 1
    画面色调变化 大 0 小 1
    是否跳剪 否 0 是 1
    """
    video = get_object_or_404(EditedVideo, pk=video_id)
    shotQuerySet = video.shotelement_set.all()
    value = shotQuerySet.count()
    start_shot = video.shotelement_set.filter(editedVideo=video).first()
    end_shot = video.shotelement_set.filter(editedVideo=video).last()
    time_list = []
    time_shotsize_list = []
    time_speed_list = []
    time_position_list = []
    time_color_list = []
    time_cramotion_list = []
    shotsize_data = []
    speed_data = []
    position_data = []
    color_data = []
    cramotion_data = []
    time_accumulation = 0
    for shot in shotQuerySet:
        time_list.append(time_accumulation)
        time_shotsize_list.append([time_accumulation, shot.shotSize])
        time_speed_list.append([time_accumulation, shot.speed[0]])
        time_position_list.append([time_accumulation, shot.position[0]])
        time_color_list.append([time_accumulation, shot.color[0]])
        time_cramotion_list.append([time_accumulation, shot.craMotion[0]])
        time_accumulation += shot.during
        time_shotsize_list.append([time_accumulation, shot.shotSize])
        shotsize_data.append(
            [{'xAxis': time_accumulation, 'yAxis': 0}, {'xAxis': time_accumulation, 'yAxis': shot.shotSize}])
        time_speed_list.append([time_accumulation, shot.speed[1]])
        speed_data.append(
            [{'xAxis': time_accumulation, 'yAxis': 0}, {'xAxis': time_accumulation, 'yAxis': shot.speed[1]}])
        time_position_list.append([time_accumulation, shot.position[1]])
        position_data.append(
            [{'xAxis': time_accumulation, 'yAxis': 0}, {'xAxis': time_accumulation, 'yAxis': shot.position[1]}])
        time_color_list.append([time_accumulation, shot.color[1]])
        color_data.append(
            [{'xAxis': time_accumulation, 'yAxis': 0}, {'xAxis': time_accumulation, 'yAxis': shot.color[1]}])
        time_cramotion_list.append([time_accumulation, shot.craMotion[1]])
        cramotion_data.append(
            [{'xAxis': time_accumulation, 'yAxis': 0}, {'xAxis': time_accumulation, 'yAxis': shot.craMotion[1]}])
    time_list.append(time_accumulation)
    context = {
        'video': video,
        'value': value,
        'startShot': start_shot,
        'endShot': end_shot,
        'timeAcc': time_accumulation,
        'timeList': json.dumps(time_list),
        'timeShotsizeList': json.dumps(time_shotsize_list),
        'shotsizeData': json.dumps(shotsize_data),
        'timeSpeedList': json.dumps(time_speed_list),
        'speedData': json.dumps(speed_data),
        'timePositionList': json.dumps(time_position_list),
        'positionData': json.dumps(position_data),
        'colorData': json.dumps(color_data),
        'cramotionData': json.dumps(cramotion_data),
        'timeColorList': json.dumps(time_color_list),
        'timeCramotionList': json.dumps(time_cramotion_list),
    }
    return render(request, 'videodatabase/detail.html', context)


def search(request):
    global search_list
    condition = request.GET.get("video")
    if condition == '':
        return render(request, 'videodatabase/home.html')
    elif condition == "手机":
        search_list = EditedVideo.objects.filter(container=1).order_by('-id')
    elif condition == "电视":
        search_list = EditedVideo.objects.filter(container=2).order_by('-id')
    elif condition == "商品上新":
        search_list = EditedVideo.objects.filter(scenes=1).order_by('-id')
    elif condition == "促销":
        search_list = EditedVideo.objects.filter(scenes=2).order_by('-id')
    elif condition == "品牌宣传":
        search_list = EditedVideo.objects.filter(scenes=3).order_by('-id')
    elif condition == "男装":
        search_list = EditedVideo.objects.filter(productCategory=1).order_by('-id')
    elif condition == "女装":
        search_list = EditedVideo.objects.filter(productCategory=2).order_by('-id')
    else:
        return render(request, 'videodatabase/home.html')
    search_videos = paginate(request, search_list)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_container(request, container_id):
    result = EditedVideo.objects.filter(container=container_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_scenes(request, scenes_id):
    result = EditedVideo.objects.filter(scenes=scenes_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_category(request, category_id):
    result = EditedVideo.objects.filter(productCategory=category_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def delete(request, clip_id):
    clip = get_object_or_404(Clip, pk=clip_id)
    clip.delete()
    return HttpResponseRedirect(reverse('autoEdit'))


filelist = []


def save_clip(request):
    if request.method == 'POST':
        name = request.FILES['file'].name
        name = name.split('.')[0]
        file = request.FILES.get('file')
        clip = Clip(name=name)
        clip.url = file
        clip.save()
        filelist.append(clip.url.path)
        return HttpResponseRedirect(reverse('autoEdit'))


def auto_edit(request):
    clip_list = Clip.objects.all().order_by('-id')
    context = {
        'clips': clip_list
    }
    return render(request, 'videodatabase/autoEdit.html', context)


def setting(request):
    return render(request, "videodatabase/setting.html")


def download(request):
    """
        ----首尾镜头----
        景别： 特写 0 近景 1 中景 2 远景 3
        主体运动强度 弱 0 中 1 强 2
        主体位置 右 0 中 1 左 2
        色调 暖 0 中 1 冷 2
        镜头运动强度 弱 0 中 1 强 2
        ----视频----
        主体运动变化 大 0 小 1
        主体位置变化 大 0 小 1
        镜头运动变化 大 0 小 1
        画面色调变化 大 0 小 1
        是否跳剪 否 0 是 1
        ----时间线----
        整体 部分 细节
    """
    global filelist
    if request.method == "POST":
        speedArg = int(request.POST.get("speedArg_options"))
        positionArg = int(request.POST.get("positionArg_options"))
        cramArg = int(request.POST.get("cramArg_options"))
        colorArg = int(request.POST.get("colorArg_options"))
        jumpArg = int(request.POST.get("jumpArg_options"))
        speed = [int(request.POST.get("start_speed_options")), int(request.POST.get("end_speed_options"))]
        craMotion = [int(request.POST.get("start_craMotion_options")), int(request.POST.get("end_craMotion_options"))]
        position = [int(request.POST.get("start_position_options")), int(request.POST.get("end_position_options"))]
        color = [int(request.POST.get("start_color_options")), int(request.POST.get("end_color_options"))]
        shot = GeneratedShotElement(speed, position, craMotion, color)
        editedVideo = GeneratedEditedVideo(jumpArg, speedArg, positionArg, cramArg, colorArg, shot)
        split1, split2 = request.POST.get("myslider").split(',')
        split1 = float(split1)
        split2 = float(split2)
        timeTemplete = []
        timeTemplete.append('%.2f' % (split1 / 100.0))
        timeTemplete.append('%.2f' % (split2 / 100.0 - split1 / 100.0))
        timeTemplete.append('%.2f' % (1.0 - split2 / 100.0))
        filelist = []
        for clip in Clip.objects.all():
            filelist.append(clip.url.path)
        video = videoEdit.VideoMerge(filelist, timeTemplete, editedVideo)
        context = {
            'video': video
        }
        return render(request, "videodatabase/download.html", context)
    else:
        return render(request, "videodatabase/download.html")


def download_video(request):
    global filelist
    file_path = os.path.join(settings.BASE_DIR, 'media', 'generate', 'file.mp4')
    if os.path.exists(file_path):
        filelist = []
        Clip.objects.all().delete()
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def contact(request):
    return render(request, 'videodatabase/contactUS.html')
