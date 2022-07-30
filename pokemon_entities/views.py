import django.core.exceptions
import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lt=timezone.localtime(),
        disappeared_at__gt=timezone.localtime(),
    )
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in pokemon_entities:
        add_pokemon(
            folium_map, entity.lat,
            entity.lon,
            request.build_absolute_uri(entity.pokemon.image.url),
        )

    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        try:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': request.build_absolute_uri(pokemon.image.url),
                'title_ru': pokemon.title,
            })
        except ValueError:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': DEFAULT_IMAGE_URL,
                'title_ru': pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    # with open('pokemon_entities/pokemons.json', encoding='utf-8') as database:
    #     pokemons = json.load(database)['pokemons']
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
        pokemons_entities = PokemonEntity.objects.filter(
            appeared_at__lt=timezone.localtime(),
            disappeared_at__gt=timezone.localtime(),
            pokemon=pokemon,
        )
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    # for pokemon in pokemons:
    #     if pokemon['pokemon_id'] == int(pokemon_id):
    #         requested_pokemon = pokemon
    #         break
    # else:
    #     return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon.image.url),
        )
    pokemon_attributes = {
        'title_ru': pokemon.title,
        'img_url': pokemon.image.url,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
    }
    context = {
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_attributes,
    }
    return render(request, 'pokemon.html', context=context)
