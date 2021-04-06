from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from collections import OrderedDict
import random
import itertools

from api.v1.serializers import ShotSerializer, Shot, PracticeSerializer, CustomPracticeSerializer, \
    DeltaShotSerializer, ScoreCardReportSerializer, ScoreShotSerializer, CustomPuttingSerializer

from billing.models import StripeInfo
from core.models import PRACTICE_TYPES, Practice, DeltaShotReport
from constant.models import TrajectoryValueRange, AimValueRange, ShotImage, WARMUP_PRACTICE_LIST
from core.utils import pick_random_distances, pick_standard_putts, get_blocked_bin, \
    pick_chip_distances, pick_pitch_distances, pick_custom_distances
from api.v1.permissions import IsPaid

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, OAuth2Authentication
from constant.models import YardBucket, FeetBucket


def make_fullswing_shots(dist_list, practice_type):
    """
    :param dist_list:
    :param practice_type:
    :return: shotserializer
    """
    aim_list = AimValueRange.objects.all()
    trajectory_list = TrajectoryValueRange.objects.filter(type='long')

    shot_list = []

    for dist in dist_list:

        if dist >= settings.DIST_FOR_SHAPE:
            aim = random.choice(aim_list)
            traj = random.choice(trajectory_list)

            try:
                if aim.is_draw:
                    shape = ShotImage.objects.get(name='draw')
                elif aim.is_straight:
                    shape = ShotImage.objects.get(name='straight')
                elif aim.is_fade:
                    shape = ShotImage.objects.get(name='fade')
                else:
                    shape = None

            except ShotImage.DoesNotExist:
                shape = None

        else:
            shape = None
            aim = None
            traj = None

        shot = Shot(shape=shape, dist=dist, aim=aim, traj=traj)

        shot_list.append(shot)

    serializer = ShotSerializer(shot_list, many=True, practice_type=practice_type)
    return serializer


class GetPracticeMixin(object):

    def get_practice_obj(self, request, *args, **kwargs):
        practice_id = kwargs.get('practice_id', None)
        if practice_id is None:
            return None

        practice_id = int(practice_id)

        try:
            practice_obj = Practice.objects.get(user=request.user, id=practice_id)
        except Practice.DoesNotExist:
            return None

        return practice_obj


class UnlmitedModeMixin(object):
    def get_practice_obj(self, request, *args, **kwargs):
        practice_id = kwargs.get('practice_id', None)
        if practice_id is None:
            return None

        practice_id = int(practice_id)

        if practice_id == 0:
            practice_obj = Practice.objects.create(user=request.user, practice_type=self.practice_type)
        else:
            try:
                practice_obj = Practice.objects.get(user=request.user, id=practice_id)
            except Practice.DoesNotExist:
                return None
        return practice_obj


# -----------------------------
# --- Report ---
# -----------------------------

class DeltaReportView(GetPracticeMixin, generics.CreateAPIView):
    """
    - NOTE:
        * delta: JSON string
            - e.g: "{ delta_dist: 1, delta_aim: 1, delta_traj: 1 }"(yard)
                    or "{delta_x: 2, delta_y: 3}" (putting)
        * hit: 1 or 0 (1: 'hit', 0: 'missing')
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    serializer_class = DeltaShotSerializer

    def create(self, request, *args, **kwargs):
        practice_obj = self.get_practice_obj(request, *args, **kwargs)
        if practice_obj is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        if practice_obj.practice_type == PRACTICE_TYPES.warmup:
            return Response({'error': 'Report is not allowed in WARM UP mode.'}, status=status.HTTP_400_BAD_REQUEST)

        # elif practice_obj.practice_type in [PRACTICE_TYPES.standard_putting, PRACTICE_TYPES.within_3feet, PRACTICE_TYPES.challenge_6foot]:
        #     serializer = ScoreShotSerializer(data=request.data)
        #
        # else:
        #     serializer = DeltaShotSerializer(data=request.data)
        serializer = DeltaShotSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(practice=practice_obj)

        return Response(request.data, status=status.HTTP_201_CREATED)


class ScoreCardReportView(generics.CreateAPIView):

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    serializer_class = ScoreCardReportSerializer


# -----------------------------
# --- History ---
# -----------------------------

class HistoryListView(APIView):

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        practices = Practice.objects.filter(user=request.user)

        histories = []
        for p in practices:
            if not p.is_valid:
                continue
            histories.append(p)

        serializer = PracticeSerializer(histories, many=True)

        return Response(serializer.data)


class HistoryDetailView(GetPracticeMixin, APIView):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        practice_obj = self.get_practice_obj(request, *args, **kwargs)
        if practice_obj is None or not practice_obj.is_valid:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        if practice_obj.practice_type in [PRACTICE_TYPES.standard_putting, PRACTICE_TYPES.within_3feet, PRACTICE_TYPES.challenge_6foot]:
            serializer = ScoreShotSerializer(practice_obj.reports, many=True)
        else:
            serializer = DeltaShotSerializer(practice_obj.reports, many=True)

        return Response(serializer.data)


# -----------------------------
# --- Full Swing ---
# -----------------------------

class GatedRandomPracticeView(UnlmitedModeMixin, APIView):
    """
    Gated Random Practice

    if practice_id=0,  new practice, otherwise unlimited mode
    """
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    practice_type = PRACTICE_TYPES.random

    def get(self, request, *args, **kwargs):
        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)
        dist_list = pick_random_distances(putting=False, practice=practice, driver=request.user.longest_distance, clubs=request.user.clubs)
        serializer = make_fullswing_shots(dist_list, self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class PuttingRandomPracticeView(UnlmitedModeMixin, APIView):
    """
    Putting-Random Practice

    if practice_id=0,  new practice, otherwise unlimited mode
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.random_putting

    def get(self, request, *args, **kwargs):
        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        dist_list = pick_random_distances(putting=True, practice=practice)
        trajectory_list = TrajectoryValueRange.objects.filter(type='putting')
        # shape_list = ShotImage.objects.all()

        shot_list = []

        for dist in dist_list:
            shot = Shot(
                shape=None,
                dist=dist,
                aim=None,
                traj=random.choice(trajectory_list)
            )

            shot_list.append(shot)

        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class WarmupPracticeView(APIView):
    """
    Warmup Practice
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    practice_type = PRACTICE_TYPES.warmup

    def get(self, request, format=None):
        warmup_practice = random.choice(WARMUP_PRACTICE_LIST)

        shot_list = []

        for shot in warmup_practice:
            # dist
            dist = shot.get('dist')
            if dist == 'Driver':
                dist = request.user.longest_distance
            # aim & shape
            aim = None
            shape = None

            aim_name = shot.get('aim', None)
            if aim_name is not None:
                try:
                    aim = AimValueRange.objects.get(description=aim_name)
                    if dist >= settings.DIST_FOR_SHAPE:
                        try:
                            if aim.is_draw:
                                shape = ShotImage.objects.get(name='draw')
                            elif aim.is_straight:
                                shape = ShotImage.objects.get(name='straight')
                            elif aim.is_fade:
                                shape = ShotImage.objects.get(name='fade')
                            else:
                                shape = None

                        except ShotImage.DoesNotExist:
                            pass
                except AimValueRange.DoesNotExist:
                    pass
            # traj
            traj = None
            traj_name = shot.get('traj', None)

            if traj_name is not None:
                try:
                    traj = TrajectoryValueRange.objects.get(description=traj_name, type='long')
                except TrajectoryValueRange.DoesNotExist:
                    pass

            # make shot object
            shot = Shot(shape=shape, dist=dist, aim=aim, traj=traj)
            shot_list.append(shot)

        # make serialiser
        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", -1),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class StandardPuttingView(APIView):
    """
    Putting-Standard Practice

    * distance: up to 25 feet
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.standard_putting

    def get(self, request, format=None):
        practice = Practice.objects.create(user=request.user, practice_type=self.practice_type)

        dist_list = pick_standard_putts()
        trajectory_list = TrajectoryValueRange.objects.filter(type='putting')
        # shape_list = ShotImage.objects.all()

        shot_list = []

        for dist in dist_list:
            shot = Shot(shape=None, dist=dist, aim=None, traj=random.choice(trajectory_list))

            shot_list.append(shot)

        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


# -----------------------------
# --- Pricing ---
# -----------------------------

class PricingInfoView(APIView):
    """
    get Stripe Public key and Pricing data
    * public_key: Stripe Public Key
    * subs_fee: subscription price(unit: USD)
    """

    def get(self, request, format=None):
        subs_fee = StripeInfo.get_subscription_price()

        return Response(OrderedDict([
            ("public_key", settings.STRIPE_PUBLIC_KEY),
            ("subs_fee", str(subs_fee))])
        )


# -----------------------------
# --- Around the Green ---
# -----------------------------

class PitchPracticeView(UnlmitedModeMixin, APIView):
    """
    Around the Green (Pitch)

    * distance: 25 ~ 75 yards
    * trajectory: Low

    if practice_id=0,  new practice, otherwise unlimited mode
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.pitch

    def get(self, request, *args, **kwargs):
        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        dist_list = pick_pitch_distances()
        pitch_traj = TrajectoryValueRange.objects.get(type='pitch')

        shot_list = []

        for dist in dist_list:
            shot = Shot(
                shape=None,
                dist=dist,
                aim=None,
                traj=pitch_traj
            )
            shot_list.append(shot)

        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class ChipPracticeView(UnlmitedModeMixin, APIView):
    """
    Around the Green (Chip)

    * distance: 5 ~ 25 yards
    * trajectory: High

    if practice_id=0,  new practice, otherwise unlimited mode
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.chip

    def get(self, request, *args, **kwargs):
        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        dist_list = pick_chip_distances()
        chip_traj = TrajectoryValueRange.objects.get(type='chip')

        shot_list = []

        for dist in dist_list:
            shot = Shot(
                shape=None,
                dist=dist,
                aim=None,
                traj=chip_traj
            )
            shot_list.append(shot)

        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )

# -----------------------------
# --- Serial/Block Practice ---
# -----------------------------


class BlockPracticeView(APIView):
    """
    Block Practice
    * If a block practice is not available for user, "is_available": False
    """
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    practice_type = PRACTICE_TYPES.block

    def get(self, request, format=None):
        practice_obj = Practice.objects.create(user=request.user, practice_type=self.practice_type)
        blocked_bin = get_blocked_bin(request.user)

        if blocked_bin is None:
            return Response({"is_available": False})

        if isinstance(blocked_bin, int):
            mid_dist = blocked_bin
        else:
            mid_dist = blocked_bin.mid

        dist_list = list(itertools.repeat(mid_dist, settings.PICK_COUNT))

        serializer = make_fullswing_shots(dist_list, self.practice_type)

        # generate serial shots

        return Response(OrderedDict([
            ("is_available", True),
            ("practice_id", practice_obj.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class SerialPracticeView(APIView):
    """
    Serial Practice
    * If a serial practice is not available for user, "is_available": False
    """
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    practice_type = PRACTICE_TYPES.serial

    def get(self, request, format=None):
        practice_obj = Practice.objects.create(user=request.user, practice_type=self.practice_type)

        # blocked_bin = get_blocked_bin(request.user)

        blocked_bin = None
        practice_list = Practice.objects.filter(
            user=request.user,
            practice_type__in=[PRACTICE_TYPES.random, PRACTICE_TYPES.block, PRACTICE_TYPES.serial,
                               PRACTICE_TYPES.custom]
        )

        last_custom_practice = DeltaShotReport.objects.filter(practice__in=practice_list).order_by('-reported_at')[0]
        last_min_dist = last_custom_practice.distance

        yards = YardBucket.objects.all()
        for yard in yards:
            if last_min_dist in range(yard.min, yard.max):
                blocked_bin = YardBucket.objects.get(min=yard.min)

        if blocked_bin is None and last_min_dist is not None:
            blocked_bin = last_min_dist

        if blocked_bin is None:
            return Response({"is_available": False})

        if isinstance(blocked_bin, int):
            min_dist = blocked_bin
            mid_dist = blocked_bin
            max_dist = blocked_bin
        else:
            min_dist = blocked_bin.min
            mid_dist = blocked_bin.mid
            max_dist = blocked_bin.max

        # 3, 4, 3
        dist_list = [min_dist, min_dist, min_dist,
                     mid_dist, mid_dist, mid_dist, mid_dist,
                     max_dist, max_dist, max_dist]

        # generate block shotst ite

        serializer = make_fullswing_shots(dist_list, self.practice_type)

        # generate serial shots

        return Response(OrderedDict([
            ("is_available", True),
            ("practice_id", practice_obj.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


# -----------------------------
# --- Custom Practice ---
# -----------------------------


# class CustomPracticeView(UnlmitedModeMixin, generics.CreateAPIView):
#     """
#     NOTE: code is good, but keyerror in swagger doc
#     if practice_id=0,  new practice, otherwise unlimited mode
#     """
#
#     authentication_classes = [OAuth2Authentication, ]
#     permission_classes = [IsAuthenticated, IsPaid]
#
#     serializer_class = CustomPracticeSerializer
#
#     practice_type = PRACTICE_TYPES.custom
#
#     def create(self, request, *args, **kwargs):
#         serializer = CustomPracticeSerializer(data=request.data, user=self.request.user)
#
#         # Check format and unique constraint
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         practice = self.get_practice_obj(request, *args, **kwargs)
#         if practice is None:
#             return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if practice.min_dist is None:
#             practice.min_dist = serializer.validated_data['min_dist']
#             practice.max_dist = serializer.validated_data['max_dist']
#             practice.save()
#
#         dist_list = pick_custom_distances(serializer.validated_data['min_dist'], serializer.validated_data['max_dist'])
#
#         serializer = make_fullswing_shots(dist_list, self.practice_type)
#
#         return Response(OrderedDict([
#             ("practice_id", practice.id),
#             ("shots", serializer.data)])
#         )

class CustomPracticeView(UnlmitedModeMixin, APIView):
    """
    :param
    e.g:
    {
    >>    min_dist: 150,
    >>    max_dist:180
    }

    if practice_id=0,  new practice, otherwise unlimited mode
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.custom

    def post(self, request, *args, **kwargs):
        serializer = CustomPracticeSerializer(data=request.data, user=self.request.user)

        # Check format and unique constraint
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        if practice.min_dist is None:
            practice.min_dist = serializer.validated_data['min_dist']
            practice.max_dist = serializer.validated_data['max_dist']
            practice.save()

        dist_list = pick_custom_distances(serializer.validated_data['min_dist'],
                                          serializer.validated_data['max_dist'])

        serializer = make_fullswing_shots(dist_list, self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


class CustomPuttingView(UnlmitedModeMixin, APIView):
    """
    :param
    e.g:
    {
    >>    min_dist: 3,
    >>    max_dist: 50
    }

    if practice_id=0,  new practice, otherwise unlimited mode
    """

    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, IsPaid]

    practice_type = PRACTICE_TYPES.custom_putting

    def post(self, request, *args, **kwargs):
        serializer = CustomPuttingSerializer(data=request.data, user=self.request.user)

        # Check format and unique constraint
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        practice = self.get_practice_obj(request, *args, **kwargs)
        if practice is None:
            return Response({'error': 'Invalid Practice'}, status=status.HTTP_400_BAD_REQUEST)

        if practice.min_dist is None:
            practice.min_dist = serializer.validated_data['min_dist']
            practice.max_dist = serializer.validated_data['max_dist']
            practice.save()

        dist_list = pick_custom_distances(serializer.validated_data['min_dist'],
                                          serializer.validated_data['max_dist'])
        trajectory_list = TrajectoryValueRange.objects.filter(type='putting')

        shot_list = []

        for dist in dist_list:
            shot = Shot(
                shape=None,
                dist=dist,
                aim=None,
                traj=random.choice(trajectory_list)
            )

            shot_list.append(shot)

        serializer = ShotSerializer(shot_list, many=True, practice_type=self.practice_type)

        return Response(OrderedDict([
            ("practice_id", practice.id),
            ("practice_type", self.practice_type),
            ("shots", serializer.data)])
        )


# -----------------------------
# --- Constant ---
# -----------------------------


class PracticeTypeListView(APIView):
    """
    Practice Type View
    (id, name)
    """
    def get(self, request):
        return Response(OrderedDict( list(PRACTICE_TYPES) ))


