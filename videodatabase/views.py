import json
import os

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from moviepy.editor import VideoFileClip

from videodb import settings
from . import videoEdit
from .models import EditedVideo, Clip, Container, Scenes, ProductCategory, Style
from .video import GeneratedEditedVideo
from .shotelement import GeneratedShotElement


def home(request):
    """广告短视频数据库主页"""
    video_list = EditedVideo.objects.all().order_by('-id')
    videos = paginate(request, video_list)
    context = get_context(request)
    context['videos'] = videos
    return render(request, 'videodatabase/home.html', context)


def get_context(request):
    """
    视频载体 手机 1 电视 2 ...
    业务场景  商品上新 1 促销 2 品牌宣传 3 ...
    产品品类 男装 1 女装 2 ...
    """
    total_amount = EditedVideo.objects.all().count()
    container = Container.objects.all()
    scenes = Scenes.objects.all()
    product_category = ProductCategory.objects.all()
    style = Style.objects.all()
    context = {
        'total_amount': total_amount,
        'container': container,
        'scenes': scenes,
        'product_category': product_category,
        'style': style
    }
    return context


def upload(request):
    """上传视频页面"""
    container = Container.objects.all()
    scenes = Scenes.objects.all()
    product_category = ProductCategory.objects.all()
    style = Style.objects.all()
    context = {
        'container': container,
        'scenes': scenes,
        'product_category': product_category,
        'style': style
    }
    return render(request, 'videodatabase/upload.html', context)


def analysis_video(request):
    """分析视频函数"""
    video = get_video(request)
    return HttpResponseRedirect(reverse('detail', args=(video.id,)))


def get_video(request):
    """获取上传的视频及标签"""
    if request.method == 'POST':
        name = request.FILES['video'].name
        name = name.split('.')[0]
        file = request.FILES.get('video')
        file_path = file.temporary_file_path()
        editedvideo = videoEdit.videoAnalysis(file_path)
        editedvideo.url = file
        editedvideo.name = name
        container_id = request.POST.get('select1')
        editedvideo.container = Container.objects.get(id=container_id)
        scenes_id = request.POST.get('select2')
        editedvideo.scenes = Scenes.objects.get(id=scenes_id)
        product_category_id = request.POST.get('select3')
        editedvideo.productCategory = ProductCategory.objects.get(id=product_category_id)
        style_id = request.POST.get('select4')
        editedvideo.style = Style.objects.get(id=style_id)
        editedvideo.save()
        path = editedvideo.url.path
        clip = VideoFileClip(path)  # 获取视频时长
        editedvideo.duration = clip.duration
        clip.reader.close()
        clip.audio.reader.close_proc()
        editedvideo.save()
        return editedvideo


def paginate(request, list):
    """视频分页功能"""
    paginator = Paginator(list, 5)
    page = request.GET.get('page')
    videos = paginator.get_page(page)
    return videos


def add_container(request):
    """管理员增添视频载体字段"""
    if request.method == 'POST':
        name = request.POST.get('container_name')
        container = Container(name=name)
        container.save()
        return HttpResponseRedirect(reverse('home'))


def add_scenes(request):
    """管理员增添业务场景字段"""
    if request.method == 'POST':
        name = request.POST.get('scenes_name')
        scenes = Scenes(name=name)
        scenes.save()
        return HttpResponseRedirect(reverse('home'))


def add_product_category(request):
    """管理员增添产品品类字段"""
    if request.method == 'POST':
        name = request.POST.get('category_name')
        product_category = ProductCategory(name=name)
        product_category.save()
        return HttpResponseRedirect(reverse('home'))


def add_style(request):
    """管理员增添产品风格字段"""
    if request.method == 'POST':
        name = request.POST.get('style_name')
        style = Style(name=name)
        style.save()
        return HttpResponseRedirect(reverse('home'))


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
    """在搜索框搜索视频"""
    global search_list
    condition = request.GET.get("video")
    search_list = None
    while True:
        search_list = EditedVideo.objects.filter(container__name=condition).order_by('-id')
        if search_list.count() > 0:
            break
        search_list = EditedVideo.objects.filter(scenes__name=condition).order_by('-id')
        if search_list.count() > 0:
            break
        search_list = EditedVideo.objects.filter(productCategory__name=condition).order_by('-id')
        if search_list.count() > 0:
            break
        search_list = EditedVideo.objects.filter(style__name=condition).order_by('-id')
        break
    if search_list is not None:
        search_videos = paginate(request, search_list)
        context = get_context(request)
        context['videos'] = search_videos
        return render(request, 'videodatabase/home.html', context)
    else:
        return render(request, 'videodatabase/home.html')


def search_container(request, container_id):
    """点击视频载体链接搜索视频"""
    result = EditedVideo.objects.filter(container_id=container_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_scenes(request, scenes_id):
    """点击业务场景链接搜索视频"""
    result = EditedVideo.objects.filter(scenes=scenes_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_category(request, category_id):
    """点击产品品类链接搜索视频"""
    result = EditedVideo.objects.filter(productCategory=category_id).order_by('-id')
    search_videos = paginate(request, result)
    context = get_context(request)
    context['videos'] = search_videos
    return render(request, 'videodatabase/home.html', context)


def search_style(request, style_id):
    """点击产品风格链接搜索视频"""
    result = EditedVideo.objects.filter(style=style_id).order_by('-id')
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
    """上传素材页面"""
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
    """下载视频功能"""
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
    """ '联系我们' 页面"""
    return render(request, 'videodatabase/contactUS.html')
