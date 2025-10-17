from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import(
    EntryHistory,
    OutHistory
)

from .serializers import CombinedHistorySerializer

class CombinedHistoryView(APIView):
    def get(self, request):
        yard_id = request.query_params.get('yard_id')
        auto_id = request.query_params.get('auto_id')
        auto_number = request.query_params.get('auto_number')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        entry_queryset = EntryHistory.objects.select_related('auto', 'yard')
        out_queryset = OutHistory.objects.select_related('auto', 'yard')
        
        if yard_id:
            entry_queryset = entry_queryset.filter(yard_id=yard_id)
            out_queryset = out_queryset.filter(yard_id=yard_id)
        
        if auto_id:
            entry_queryset = entry_queryset.filter(auto_id=auto_id)
            out_queryset = out_queryset.filter(auto_id=auto_id)
        
        if auto_number:
            entry_queryset = entry_queryset.filter(auto__auto_number__icontains=auto_number)
            out_queryset = out_queryset.filter(auto__auto_number__icontains=auto_number)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                entry_queryset = entry_queryset.filter(created_at__gte=date_from)
                out_queryset = out_queryset.filter(created_at__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                entry_queryset = entry_queryset.filter(created_at__lt=date_to)
                out_queryset = out_queryset.filter(created_at__lt=date_to)
            except ValueError:
                pass
        
        entry_history = list(entry_queryset)
        out_history = list(out_queryset)
        
        combined_history = []
        
        for entry in entry_history:
            combined_history.append({
                'id': entry.id,
                'event_type': 'entry',
                'created_at': entry.created_at,
                'auto': entry.auto,
                'yard': entry.yard
            })
        
        for out in out_history:
            combined_history.append({
                'id': out.id,
                'event_type': 'exit',
                'created_at': out.created_at,
                'auto': out.auto,
                'yard': out.yard
            })
        
        combined_history.sort(key=lambda x: x['created_at'], reverse=True)
        
        serializer = CombinedHistorySerializer(combined_history, many=True)
        
        return Response(serializer.data)