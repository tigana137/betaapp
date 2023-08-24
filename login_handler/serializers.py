from rest_framework import serializers
from .models import Ecole_data, Classes, Eleves, Matieres, Profs


class ecole_data_serializer(serializers.ModelSerializer):
    bool = serializers.BooleanField(default=True)

    class Meta:
        model = Ecole_data
        fields = '__all__'


class classes_serializer(serializers.ModelSerializer):
    is_examned = serializers.SerializerMethodField()

    def get_is_examned(self, instance):
        return (False)

    class Meta:
        model = Classes
        fields = ['id', 'cid', 'name', 'level','count', 'is_active', 'is_examned']


class Profs_serializer(serializers.ModelSerializer):
    class Meta:
        model = Profs
        fields = ['id','eid', 'nom', 'prenom', 'is_active']
        ordering = ['nom']


class Eleves_serializer(serializers.ModelSerializer):
    class Meta:
        model = Eleves
        fields = '__all__'
        ordering = ['nom', 'prenom']


class Matiere_serializer(serializers.ModelSerializer):
    class Meta:
        model = Matieres
        fields = '__all__'
