from rest_framework import serializers

from constant.models import AimDiffRange, TrajectoryDiffRange, DistanceDiffRange, ShotImage, \
    PuttingAimRange, PuttingDistRange, ClubType


class DistanceDiffSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistanceDiffRange
        fields = ('mode', 'min', 'max', 'step')


class AimDiffSerializer(serializers.ModelSerializer):

    class Meta:
        model = AimDiffRange
        fields = ('mode', 'min', 'max', 'step')


class TrajectoryDiffSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrajectoryDiffRange
        fields = ('value', 'description')


class ShotImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShotImage
        fields = ('name', 'shape')


class PuttingAimSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuttingAimRange
        fields = ('value', 'description')


class PuttingDistSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuttingDistRange
        fields = ('value', 'description')


class ClubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubType
        fields = ('id', 'name')
