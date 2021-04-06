from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from api.v1.serializers import AimDiffSerializer, TrajectoryDiffSerializer, DistanceDiffSerializer, PuttingAimSerializer, PuttingDistSerializer, ClubTypeSerializer
from constant.models import AimDiffRange, TrajectoryDiffRange, DistanceDiffRange, PuttingAimRange, PuttingDistRange, ClubType


class DistanceDiffList(generics.ListAPIView):
    """
    API endpoint for Distance Difference Range
    """
    serializer_class = DistanceDiffSerializer
    queryset = DistanceDiffRange.objects.all()


class AimDiffList(generics.ListAPIView):
    """
    API endpoint for Aim Difference Range
    """
    serializer_class = AimDiffSerializer
    queryset = AimDiffRange.objects.all()


class TrajectoryDiffList(generics.ListAPIView):
    """
    API endpoint for Trajectory Difference Range
    """
    serializer_class = TrajectoryDiffSerializer
    queryset = TrajectoryDiffRange.objects.all()


class PuttingDiffView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            "aim": PuttingAimSerializer(list(PuttingAimRange.objects.all()), many=True).data,
            "dist": PuttingDistSerializer(list(PuttingDistRange.objects.all()), many=True).data
        })


class ClubTypeListView(generics.ListAPIView):
    """
    Club Type View
    (id, name)
    """
    serializer_class = ClubTypeSerializer
    queryset = ClubType.objects.all()
