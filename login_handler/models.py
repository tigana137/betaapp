from django.db import models

# Create your models here.


class Dre(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class Del1(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class Ecole_data(models.Model):
    sid = models.IntegerField(primary_key=True)
    school_name = models.CharField(max_length=50)
    stat_school_name = models.CharField(
        max_length=50, blank=True, null=True, default=None)
    pr_nom = models.CharField(max_length=50)
    pr_prenom = models.CharField(max_length=50)
    url = models.CharField(max_length=100)
    nbr_elev=models.PositiveSmallIntegerField()
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True)
    del1 = models.ForeignKey(
        Del1, on_delete=models.SET_NULL, blank=True, null=True)


class Classes(models.Model):
    level_choices = [('0', 'التحضيري'), ('1', 'الأولى'), ('2', 'الثانية'),
                     ('3', 'الثالثة'), ('4', 'الرابعة'), ('5', 'الخامسة'), ('6', 'السادسة')]

    id = models.AutoField(primary_key=True)
    cid = models.BigIntegerField()
    name = models.CharField(max_length=60)
    # level = models.CharField(max_length=1,choices=level_choices)
    level = models.CharField(max_length=10)
    count = models.CharField(max_length=3)
    male_count = models.CharField(max_length=3)
    female_count = models.CharField(max_length=3)
    next_class_id = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)

    def activate(self):
        def add_matiere(saisie_classe, name, saisie_matiere_id):
            matiere = Matieres()
            matiere.name = name
            matiere.saisie_matiere_id = saisie_matiere_id
            matiere.classe = saisie_classe
            matiere.save()

        self.is_active = True
        add_matiere(self, "مجال اللغة العربية التواصل الشفوي و المحفوظات", 1)
        add_matiere(self, "مجال اللغة العربية القراءة", 2)
        add_matiere(self, "مجال اللغة العربية قواعد اللغة رسم/نحو/صرف",
                    3) if self.level >= '3' else add_matiere(self, "مجال اللغة العربية الخط و الإملاء", 4)
        add_matiere(self, "مجال اللغة العربية الانتاج الكتابي", 5)
        add_matiere(self, "مجال العلوم و التكنولوجيا الرياضيات", 6)
        add_matiere(self, "مجال العلوم و التكنولوجيا الايقاظ العلمي", 7)
        add_matiere(self, "مجال العلوم و التكنولوجيا التربية التكنولوجية", 8)
        add_matiere(self, "مجال التنشئة التربية الاسلامية", 9)
        if self.level >= '5':
            add_matiere(self, "مجال التنشئة التاريخ", 10)
            add_matiere(self, "مجال التنشئة الجغرافيا", 11)
            add_matiere(self, "مجال التنشئة التربية المدنية", 12)
        add_matiere(self, "مجال التنشئة التربية التشكيلية", 13)
        add_matiere(self, "مجال التنشئة التربية الموسيقية", 14)
        add_matiere(self, "مجال التنشئة التربية البدنية", 15)
        if self.level >= '2':
            add_matiere(
                self, "مجال اللغة الفرنسية Exp. orale et recitation", 16)
            add_matiere(self, "مجال اللغة الفرنسية Lecture", 17)
            add_matiere(
                self, "مجال اللغة الفرنسية Prod. ecrite et ecriture", 18)
        if self.level >= '4':
            add_matiere(self, "مجال اللغة الانجليزية اللغة الانجليزية", 19)

    class Meta:
        unique_together=('cid','ecole')
        ordering = ['level', 'name']


class Eleves(models.Model):
    id = models.AutoField(primary_key=True)
    eid = models.IntegerField()
    uid = models.BigIntegerField(blank=True, null=True)
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    sexe = models.CharField(max_length=10)
    date_naissance = models.DateField(null=True, blank=True)
    moyen = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True)
    resultat = models.CharField(max_length=25, blank=True, null=True)
    is_graduated = models.BooleanField(default=None, blank=True, null=True)
    # change it just to class (apparently it adds _id it self)
    classe = models.ForeignKey(
        Classes, on_delete=models.PROTECT)
    next_class = models.ForeignKey(
        Classes, on_delete=models.PROTECT, blank=True, null=True, related_name='next_class')

    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)

    class Meta:
        unique_together=('eid','ecole')
        ordering = ['nom', 'prenom']


class Profs(models.Model):
    id = models.AutoField(primary_key=True)
    eid = models.IntegerField()
    pid = models.BigIntegerField(blank=True, null=True)
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)


class Matieres(models.Model):
    field = models.CharField(max_length=80, blank=True, null=True)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE)
    prof = models.ForeignKey(Profs, on_delete=models.SET_NULL, null=True)
    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)

    class Meta:
      #  unique_together = ('field', 'saisie_classe')
        ordering = ['classe',]


class ElevesTransfer(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.BigIntegerField(blank=True,null=True)
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    prev_new_ecole = models.CharField(max_length=40)
    date_naissance = models.DateField(null=True, blank=True)
    date_sortie = models.DateField(null=True, blank=True)
    arriv_sorti = models.BooleanField()
    sexe = models.CharField(max_length=10, blank=True, null=True)
    level = models.CharField(max_length=10, blank=True, null=True)
    is_graduated = models.BooleanField(max_length=10, blank=True, null=True)
    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)


class sexeEleves(models.Model):
    nom = models.CharField(max_length=40, primary_key=True)
    male = models.BooleanField(default=False)
    female = models.BooleanField(default=False)


class excution_time(models.Model):
    id2 = models.PositiveSmallIntegerField()
    funct = models.TextField(blank=True, null=True)
    time = models.TextField(blank=True, null=True)
    ecole = models.ForeignKey(
        Ecole_data, on_delete=models.SET_NULL, blank=True, null=True)


class Logins(models.Model):
    ecole = models.ForeignKey(Ecole_data, on_delete=models.PROTECT)
    field = models.TextField(blank=True, null=True)
    val = models.TextField(blank=True, null=True)


class ExcelData(models.Model):
    dre = models.ForeignKey(
        Dre, on_delete=models.SET_NULL, blank=True, null=True)
    nom_prenom = models.CharField(max_length=50)
    eleve_id = models.BigIntegerField(blank=True, null=True)
    prev_ecole = models.CharField(max_length=50)
    level = models.PositiveSmallIntegerField()
    next_ecole = models.CharField(max_length=50)
