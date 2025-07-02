from rest_framework import serializers
from .models import SubjectArea,JournalSection,Journal

class SubjectAreaSerializer(serializers.ModelSerializer): #serializer for subject area
    class Meta:
        model = SubjectArea
        fields = ['id', 'name']

class JournalSectionSerializer(serializers.ModelSerializer): #serializer for journal section
    class Meta:
        model = JournalSection
        fields = ['id', 'name']

'''class JournalSerializer(serializers.ModelSerializer): #serializer for journal
    class Meta:
        model = Journal
        fields = '__all__'  # Or specify explicitly if you prefer
    '''

class JournalSerializer(serializers.ModelSerializer):
    subject_area_name = serializers.CharField(source='subject_area.name', read_only=True)
    journal_section_name = serializers.CharField(source='journal_section.name', read_only=True)
    user_id = serializers.IntegerField(source='corresponding_author.user.id', read_only=True)  # ✅ corrected

    class Meta:
        model = Journal
        fields = '__all__'  # Includes original IDs and adds name fields

class JournalStatusSerializer(serializers.ModelSerializer): #serializer for journal status
    class Meta:
        model = Journal
        fields = ['id', 'title', 'submission_date', 'status']
