from django.db import models

# Create your models here.

#사용자 정보 테이블
class User(models.Model):
    uid = models.CharField(max_length=255, unique=True)  # UID
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# 회사별 무게 테이블
class Weight(models.Model): 
    company = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.company}: {self.weight}kg" # weight_instance = Weight(company="abc", weight=123) print(weight_instance) ---> abc: 123kg 형식으로 출력되게 만들어줌

