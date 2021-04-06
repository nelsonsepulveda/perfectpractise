from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import Practice, PRACTICE_TYPES, DeltaShotReport, ScoreShotReport
from billing.models import BillingInfo
from constant.models import AimValueRange, TrajectoryValueRange
from profiles.models import ClubBag


User = get_user_model()


class Shot(object):
    def __init__(self, shape, dist, aim, traj):
        self.shape = shape
        self.distance = dist
        self.aim = aim
        self.trajectory = traj


class ShotSerializer(serializers.Serializer):
    shape = serializers.StringRelatedField(read_only=True)
    distance = serializers.IntegerField(read_only=True)
    aim = serializers.StringRelatedField(read_only=True)
    trajectory = serializers.StringRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        practice_type = kwargs.pop('practice_type')

        super(ShotSerializer, self).__init__(*args, **kwargs)

        if practice_type in [PRACTICE_TYPES.standard_putting, PRACTICE_TYPES.random_putting, PRACTICE_TYPES.custom_putting,
                             PRACTICE_TYPES.chip, PRACTICE_TYPES.pitch]:
            self.fields.pop('aim')
            self.fields.pop('shape')


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password',
                  'handicap', 'birthday', 'location', 'years_of_experience', 'creation_time')

    def __init__(self, *args, **kwargs):
        super(RegisterSerializer, self).__init__(*args, **kwargs)
        self.fields['email'].required = True


class ClubSerializer(serializers.ModelSerializer):
    # club_type = serializers.StringRelatedField()

    class Meta:
        model = ClubBag
        fields = ('club_name', 'club_type', 'confidence', 'avg_dist')


class ProfileSerializer(serializers.ModelSerializer):
    clubs = ClubSerializer(many=True)
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'handicap', 'birthday', 'location', 'years_of_experience', 'creation_time', 'photo',
                  'subscription_status', 'clubs')
        read_only_fields = ('username', 'email', 'subscription_status', 'photo')

    def get_subscription_status(self, user):
        try:
            billing_obj = BillingInfo.objects.get(user=user)
        except BillingInfo.DoesNotExist:
            return 0

        if billing_obj.is_active:
            return 1  # active
        elif billing_obj.is_subscribed:
            return 2  # subscribed but inactive
        else:
            return 0  # not subscribed

    def update(self, instance, validated_data):
        new_club_data = validated_data.pop('clubs')
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.handicap = validated_data.get('handicap', instance.handicap)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.location = validated_data.get('location', instance.location)
        instance.years_of_experience = validated_data.get('years_of_experience', instance.years_of_experience)
        instance.creation_time = validated_data.get('creation_time', instance.creation_time)
        instance.save()

        new_club_ids = []
        old_club_ids = list(ClubBag.objects.filter(owner=instance).values_list('id', flat=True))

        for new_club in new_club_data:
            club_name = new_club.get('club_name')
            try:
                if club_name is not None:
                    club = ClubBag.objects.get(owner=instance, club_type=new_club['confidence'], club_name=club_name)
                else:
                    club = ClubBag.objects.get(owner=instance, club_type=new_club['confidence'])
                # club = ClubBag.objects.get(owner=instance, club_type=new_club['confidence'])
                club.club_type = new_club['club_type']
                club.avg_dist = new_club['avg_dist']
                club.confidence = new_club['confidence']
                club.club_name = "sample"
                club.save()  # this is not working

            except ClubBag.DoesNotExist:
                club = ClubBag.objects.create(
                    owner=instance, club_type=new_club['club_type'], club_name=club_name,
                    confidence=new_club['confidence'], avg_dist=new_club['avg_dist']
                )

            new_club_ids.append(club.id)

        del_ids = list(set(old_club_ids)-set(new_club_ids))
        ClubBag.objects.filter(id__in=del_ids).delete()

        return instance


class DeltaShotSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeltaShotReport
        fields = ('distance', 'aim', 'trajectory', 'club', 'hit', 'delta', 'reported_at')
        read_only_fields = ('reported_at', )

    def __init__(self, *args, **kwargs):
        super(DeltaShotSerializer, self).__init__(*args, **kwargs)
        self.fields['delta'].error_messages['required'] = 'Delta for shot difference is required'
        self.fields['hit'].error_messages['required'] = 'Hit/Miss is required'
        self.fields['distance'].error_messages['required'] = 'Distance is required'
        self.fields['trajectory'].error_messages['required'] = 'Trajectory value is required'

    def validate_aim(self, value):
        try:
            aim_obj = AimValueRange.objects.get(description__iexact=value)
        except Exception:
            raise serializers.ValidationError("Invalid Aim Value")
        return value

    def validate_trajectory(self, value):
        if TrajectoryValueRange.objects.filter(description__iexact=value).count() > 0:
            return value
        else:
            raise serializers.ValidationError("Invalid Trajectory Value")


class ScoreShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreShotReport
        fields = ('putt_counts', 'points', 'reported_at',)
        read_only_fields = ('reported_at',)


class ScoreCardReportSerializer(serializers.Serializer):
    """
    write-only serializer
    """
    practice_type = serializers.IntegerField()
    score_card = ScoreShotSerializer(many=True)

    def validate_practice_type(self, value):
        if value in [PRACTICE_TYPES.within_3feet, PRACTICE_TYPES.challenge_6foot]:
            return value
        raise serializers.ValidationError("Invalid Practice Type")

    def create(self, validated_data):
        practice_type = validated_data.get('practice_type')
        score_card = validated_data.get('score_card')

        if len(score_card) < 1:
            raise serializers.ValidationError("Empty Score Card")

        practice = Practice.objects.create(user=self.context['request'].user, practice_type=practice_type)

        for turn in score_card:
            ScoreShotReport.objects.create(practice=practice, putt_counts=turn['putt_counts'], points=turn['points'])

        return validated_data


class PracticeSerializer(serializers.ModelSerializer):

    class Meta:
        # Read only Serializer
        model = Practice
        fields = ('id', 'practice_type', 'created_at', 'score', 'max_score')


class CustomPracticeSerializer(serializers.Serializer):
    """
    write only
    """
    min_dist = serializers.IntegerField()
    max_dist = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CustomPracticeSerializer, self).__init__(*args, **kwargs)

    def validate_min_dist(self, value):
        # if value < 25:  # NOTE: hardcode
        #     raise serializers.ValidationError("Mininum distance should be greater than 25 yards in custom practice")
        if value < 0:
            raise serializers.ValidationError("Mininum distance should be greater than 0")
        return value

    def validate_max_dist(self, value):
        driver_dist = self.user.longest_distance
        #if driver_dist and driver_dist < value and value < 500:
        #    raise serializers.ValidationError("Maximum distance should be less than your Driver Distance: %d yards." % driver_dist)
        return value


class CustomPuttingSerializer(serializers.Serializer):
    """
    write only
    """
    min_dist = serializers.IntegerField()
    max_dist = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CustomPuttingSerializer, self).__init__(*args, **kwargs)

    def validate_min_dist(self, value):
        if value < 0:
            raise serializers.ValidationError("Mininum distance should be greater than 0")
        return value
