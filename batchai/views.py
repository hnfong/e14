from django.http import JsonResponse
from . import models
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def pending_requests(request):
    pending_requests = models.TextInferenceRequest.list_pending()
    data = []
    for req in pending_requests:
        data.append({
                'uuid': req.uuid,
                'priority': req.priority,
                'requester': req.requester.username if req.requester else None,
                'purpose': req.purpose,
                'created': req.created.isoformat(),
                'modified': req.modified.isoformat(),
                'system_prompt': req.system_prompt,
                'user_prompt': req.user_prompt,
                'llm_model': req.llm_model,
                'temperature': req.temperature,
                'max_tokens': req.max_tokens,
                'created': req.created,
                # 'llama_cpp_extra_arguments': req.llama_cpp_extra_arguments,

            })
    # Add csrf_token for clients to use
    return JsonResponse({"requests": data, "csrf_token": get_token(request)}, safe=False)

def html_list(request):
    items = models.TextInferenceRequest.list().filter(requester=request.user).order_by("-created")
    return render(request, "batchai/list.html", { "items": items })

def submit_request(request):
    if request.method == "POST":
        request_obj = models.TextInferenceRequest()
        request_obj.requester = request.user
        request_obj.status = models.TextInferenceRequest.STATUS_PENDING
        request_obj.user_prompt = request.POST.get("user_prompt")
        request_obj.llm_model = request.POST.get("llm_model")
        request_obj.max_tokens = int(request.POST.get("max_tokens") or "0")
        request_obj.purpose = request.POST.get("purpose") or ""
        request_obj.save()
    return render(request, "batchai/submit.html", {})

# FIXME: use some other auth method.
@csrf_exempt
def submit_inference_result(request):
    try:
        uuid = request.POST.get('uuid')
        result = request.POST.get('result')
        logs = request.POST.get('logs')
        success = request.POST.get('success')

        if not uuid:
            return JsonResponse({'error': 'UUID is required'}, status=400)

        try:
            request_obj = models.TextInferenceRequest.objects.get(uuid=uuid)
        except TextInferenceRequest.DoesNotExist:
            return JsonResponse({'error': 'Invalid UUID'}, status=404)

        if request_obj.status >= models.TextInferenceRequest.STATUS_FINALIZED_LINE:
            return JsonResponse({'error': 'Already inferred'}, status=403)

        if success == "true":
            request_obj.status = models.TextInferenceRequest.STATUS_DONE
        else:
            request_obj.status = models.TextInferenceRequest.STATUS_ERROR

        request_obj.result = result
        request_obj.logs = logs
        request_obj.save()

        return JsonResponse({'status': 'success', 'uuid': uuid})

    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
