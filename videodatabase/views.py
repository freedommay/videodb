import json
import os
import uuid

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from moviepy.editor import VideoFileClip
from qiniu import Auth, put_file

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
    风格
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


def save_to_local(file, file_name):
    """上传视频到本地服务器目录"""
    folder = uuid.uuid4().hex[:8]
    path = os.path.join(settings.MEDIA_ROOT, 'video', folder).replace("\\", "/")
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, file_name), "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return 'video/%s/%s' % (folder, file_name)


def save_to_qiniu(file, file_name):
    """上传视频到七牛云存储空间"""
    return qiniu_upload_file(file, file_name)


def qiniu_upload_file(file, filename):
    access_key = 'n3Mua5gMrHZKfx82ug-xtL9-kmbzPYTjpSvBVA2C'
    secret_key = 'BDyebFk_OA-bsCdpmtFb9IaF5Zkc2U6wob_HIagX'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 存储空间名称
    bucket_name = 'media'
    key = filename
    folder = uuid.uuid4().hex[:8]
    # 上传后保存的文件名，采用虚拟目录
    # key = 'video/' + folder + '/' + key
    key = os.path.join('video', folder, key).replace("\\", "/")
    # 生成上传 Token
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, file.temporary_file_path())
    bucket_domain = 'pnigxm4gh.bkt.clouddn.com'
    base_url = 'http://%s/%s' % (bucket_domain, key)  # 获取外链
    return base_url


def get_video(request):
    """获取上传的视频及标签"""
    if request.method == 'POST':
        file = request.FILES.get('video')
        name = file.name
        show_name = ""
        if name.find('.') > 0:
            show_name = name.split('.')[0]
        # url = save_to_local(file, name)
        url = save_to_qiniu(file, name)
        # editedvideo = videoEdit.videoAnalysis(os.path.join(settings.MEDIA_ROOT, url))
        editedvideo = videoEdit.videoAnalysis(url)
        editedvideo.url = url
        editedvideo.name = show_name
        container_id = request.POST.get('select1')
        if int(container_id) != 0:
            editedvideo.container = Container.objects.get(id=container_id)
        scenes_id = request.POST.get('select2')
        if int(scenes_id) != 0:
            editedvideo.scenes = Scenes.objects.get(id=scenes_id)
        product_category_id = request.POST.get('select3')
        if int(product_category_id) != 0:
            editedvideo.productCategory = ProductCategory.objects.get(id=product_category_id)
        style_id = request.POST.get('select4')
        if int(style_id) != 0:
            editedvideo.style = Style.objects.get(id=style_id)
        # clip = VideoFileClip(os.path.join(settings.MEDIA_ROOT, url))
        clip = VideoFileClip(url)  # 获取视频时长
        editedvideo.duration = clip.duration
        clip.reader.close()
        clip.audio.reader.close_proc()
        editedvideo.save()
        return editedvideo


def paginate(request, list):
    """视频分页功能"""
    paginator = Paginator(list, 8)
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
    result = EditedVideo.objects.filter(container=container_id).order_by('-id')
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
    """素材删除"""
    clip = get_object_or_404(Clip, pk=clip_id)
    clip.delete()
    return HttpResponseRedirect(reverse('autoEdit'))


def save_clip_to_qiniu(file, filename, cookie):
    """保存素材到云存储空间"""
    access_key = 'n3Mua5gMrHZKfx82ug-xtL9-kmbzPYTjpSvBVA2C'
    secret_key = 'BDyebFk_OA-bsCdpmtFb9IaF5Zkc2U6wob_HIagX'
    q = Auth(access_key, secret_key)
    bucket_name = 'media'
    key = os.path.join('clip', cookie, filename).replace("\\", "/")
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, file.temporary_file_path())
    bucket_domain = 'pnigxm4gh.bkt.clouddn.com'
    base_url = 'http://%s/%s' % (bucket_domain, key)
    return base_url


def save_clip(request):
    """上传素材"""
    if request.method == 'POST':
        cookie = request.COOKIES['csrftoken']
        file = request.FILES.get('file')
        name = file.name
        clip = Clip(name=name)
        clip.userId = cookie
        url = save_clip_to_qiniu(file, name, cookie)
        clip.url = url
        clip.save()
        return HttpResponseRedirect(reverse('autoEdit'))


def auto_edit(request):
    """上传素材页面"""
    cookie = request.COOKIES['csrftoken']
    clip_list = Clip.objects.filter(userId=cookie).order_by('-id')
    context = {
        'clips': clip_list
    }
    return render(request, 'videodatabase/autoEdit.html', context)


def setting(request):
    """设置参数页面"""
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
        cookie = request.COOKIES['csrftoken']
        for clip in Clip.objects.filter(userId=cookie):
            filelist.append(clip.url)
        video = videoEdit.VideoMerge(filelist, timeTemplete, editedVideo)
        context = {
            'video': video
        }
        return render(request, "videodatabase/download.html", context)
    else:
        raise Http404


def download_video(request):
    """下载视频功能"""
    name = request.POST.get('video')
    file_path = os.path.join(settings.BASE_DIR, 'media', 'generate', name)
    cookie = request.COOKIES['csrftoken']
    if os.path.exists(file_path):
        Clip.objects.all().filter(userId=cookie).delete()
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def contact(request):
    """ '联系我们' 页面"""
    return render(request, 'videodatabase/contactUS.html')
