from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from ..Service.gemini_services import generate_movie_description, ask_gemini, ask_gemini_cinema_system, analyze_revenue_data


@csrf_exempt
@staff_member_required
def gemini_generate_description_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ!'}, status=400)

    movie_name = request.POST.get('movie_name', '').strip()
    categories = request.POST.get('categories', '').strip()
    director = request.POST.get('director', '').strip()
    actor = request.POST.get('actor', '').strip()

    if not movie_name:
        return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập Tên Phim trước khi tạo mô tả tự động!'}, status=400)

    try:
        desc = generate_movie_description(movie_name, categories, director, actor)
        return JsonResponse({'status': 'success', 'description': desc})
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=200)


@csrf_exempt
def gemini_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ!'}, status=400)

    prompt = request.POST.get('prompt', '').strip()
    if not prompt:
        import json
        try:
            body = json.loads(request.body.decode('utf-8'))
            prompt = body.get('prompt', '').strip()
        except Exception:
            pass

    if not prompt:
        return JsonResponse({'status': 'error', 'message': 'Nội dung câu hỏi không được để trống!'}, status=400)

    try:
        reply = ask_gemini_cinema_system(prompt)
        return JsonResponse({'status': 'success', 'reply': reply})
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=200)


@csrf_exempt
@staff_member_required
def gemini_analyze_revenue_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ!'}, status=400)

    summary = {
        'today': request.POST.get('today', 0),
        'month': request.POST.get('month', 0),
        'quarter': request.POST.get('quarter', 0),
        'year': request.POST.get('year', 0),
        'overall': request.POST.get('overall', 0),
        'period': request.POST.get('period', 'Hôm nay'),
        'details': request.POST.get('details', '')
    }
    try:
        analysis = analyze_revenue_data(summary)
        return JsonResponse({'status': 'success', 'analysis': analysis})
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=500)
