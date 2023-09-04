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
        fields = ['id', 'cid', 'name', 'level','is_active', 'is_examned']

class classes_serializer2(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ['id','name', 'level',]



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

class Eleves_serializer2(serializers.ModelSerializer):  # less data
    class Meta:
        model = Eleves
        fields = ['uid','nom','prenom','sexe','date_naissance']
        ordering = ['nom', 'prenom']

class Matiere_serializer(serializers.ModelSerializer):
    class Meta:
        model = Matieres
        fields = '__all__'
