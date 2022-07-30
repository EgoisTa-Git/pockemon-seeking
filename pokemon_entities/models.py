from django.db import models
from django.utils import timezone


def tomorrow():
    return timezone.now() + timezone.timedelta(days=1)


class Pokemon(models.Model):
    title = models.CharField('Название', max_length=200)
    title_en = models.CharField(
        'Название на английском',
        max_length=200,
        default='',
        blank=True,
    )
    title_jp = models.CharField(
        'Название на японском',
        max_length=200,
        default='',
        blank=True,
    )
    description = models.TextField('Описание', default='', blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous',
        verbose_name='Из кого эволюционировал'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='avatars',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тип покемона'
        verbose_name_plural = 'Типы покемонов'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        verbose_name='Тип покемона'
    )
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    appeared_at = models.DateTimeField(
        'Время появления',
        default=timezone.now,
    )
    disappeared_at = models.DateTimeField(
        'Время исчезновения',
        default=tomorrow
    )
    level = models.IntegerField('Уровень', default=0, blank=True)
    health = models.IntegerField('Здоровье', default=1, blank=True)
    strength = models.IntegerField('Сила', default=1, blank=True)
    defence = models.IntegerField('Защита', default=1, blank=True)
    stamina = models.IntegerField('Выносливость', default=1, blank=True)

    def __str__(self):
        return f'{self.pokemon.title} ({self.level})'

    class Meta:
        verbose_name = 'Покемон'
        verbose_name_plural = 'Покемоны'
