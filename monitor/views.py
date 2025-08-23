from django.http import JsonResponse, FileResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.db import transaction

from .models import Report
from .tasks import generate_report_async

@require_http_methods(["POST"])
def trigger_report(request):
    with transaction.atomic():
        report = Report.objects.create()
    generate_report_async(str(report.id))
    return JsonResponse({"report_id": str(report.id)})

@require_http_methods(["GET"])
def get_report(request):
    report_id = request.GET.get('report_id')
    if not report_id:
        return HttpResponseBadRequest('Missing report_id')

    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return HttpResponseNotFound('No such report')

    if report.status == Report.Status.COMPLETE and report.csv_path:
        response = FileResponse(open(report.csv_path, 'rb'), as_attachment=True, filename=f'report_{report_id}.csv')
        response['X-Report-Status'] = 'Complete'
        return response
    elif report.status == Report.Status.FAILED:
        return JsonResponse({"status": "Failed", "error": report.error}, status=500)
    else:
        return JsonResponse({"status": "Running"})
